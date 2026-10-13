#!/usr/bin/env python3
"""逐格擷取網頁產品畫面（虛擬時鐘），輸出 JPG 序列給動態影片使用。

用法：
  python capture.py shots.json --out videos/demo/assets/clips              # 全部鏡頭
  python capture.py shots.json --out ... --only hero,power                  # 只拍某幾個
  python capture.py shots.json --out ... --test                             # 試拍：每 45 格存一張，檢查動作
  python capture.py shots.json --out ... --jobs 2                           # 兩個瀏覽器平行拍

原理：
  vt.js 在頁面載入前取代 performance.now / requestAnimationFrame / setTimeout，
  每一格呼叫 __step(1000/fps) 推進虛擬時間，再截圖。不管電腦多慢，畫面都是平順的 30fps。

shots.json 格式見 references/capture-guide.md。
"""
import argparse, asyncio, json, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VT = HERE / "vt.js"


def cine_css(cfg):
    c = cfg.get("cine", {})
    box, host = c.get("container"), c.get("canvas_host")
    if not box:
        return ""
    bg = c.get("background", "#18242a")
    css = f"""
{box}{{position:fixed!important;left:0!important;top:0!important;width:100vw!important;height:100vh!important;z-index:2147483000!important;background:{bg}!important;margin:0!important;border:0!important;border-radius:0!important;transform:none!important}}
{box} > *:not({host}){{opacity:0!important}}
{host}{{position:absolute!important;inset:0!important;width:100%!important;height:100%!important}}
"""
    return css + c.get("extra_css", "")


JS_CLICK = """([t,s])=>{const all=[...document.querySelectorAll(s)];
const tx=e=>(e.innerText||e.getAttribute('aria-label')||e.title||'').trim();
const el=all.find(e=>tx(e)===t)||all.find(e=>tx(e).startsWith(t));
if(el){el.click();return true}return false}"""


async def do_action(pg, a, name):
    """執行一個動作。a 是 dict：click / click_sel / fill / select / eval / key / hover / mouse."""
    if "click" in a:
        ok = await pg.evaluate(JS_CLICK, [a["click"], a.get("scope", "button,[role=button],a")])
        if not ok:
            print(f"  ! [{name}] 找不到按鈕文字：{a['click']}", flush=True)
    elif "click_sel" in a:
        await pg.evaluate("s=>{const e=document.querySelector(s); if(e) e.click(); else console.warn('no',s)}", a["click_sel"])
    elif "fill" in a:
        f = a["fill"]
        await pg.evaluate("""([s,v])=>{const i=document.querySelector(s); if(!i) return;
          const p=Object.getPrototypeOf(i); const d=Object.getOwnPropertyDescriptor(p,'value'); d.set.call(i,v);
          i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));}""", [f["selector"], f["value"]])
    elif "select" in a:
        s = a["select"]
        loc = pg.locator(s["selector"])
        loc = loc.nth(s.get("index", 0)) if s.get("index", 0) >= 0 else loc.last
        if "label" in s: await loc.select_option(label=s["label"])
        else: await loc.select_option(value=s["value"])
    elif "eval" in a:
        await pg.evaluate(a["eval"])
    elif "key" in a:
        await pg.keyboard.press(a["key"])
    elif "mouse" in a:   # 內部使用：drag 展開後的滑鼠事件
        kind, x, y = a["mouse"]
        if kind == "move": await pg.mouse.move(x, y)
        elif kind == "down": await pg.mouse.move(x, y); await pg.mouse.down()
        elif kind == "up": await pg.mouse.up()
        elif kind == "wheel": await pg.mouse.wheel(0, y)
    else:
        print(f"  ! [{name}] 不認得的動作：{a}", flush=True)


def expand(actions, frames):
    """把 drag / type 這類跨多格的動作展開成每格的事件，回傳 {frame: [action,...]}。"""
    out = {}
    add = lambda f, a: out.setdefault(int(f), []).append(a)
    for a in actions:
        if "drag" in a:      # {"drag": dx, "dy": 0, "from": 0, "to": 255, "x0": 960, "y": 540}
            f0, f1 = a.get("from", 0), a.get("to", frames - 1)
            x0, y0 = a.get("x0", 960), a.get("y", 540)
            dx, dy = a["drag"], a.get("dy", 0)
            add(f0, {"mouse": ["down", x0, y0]})
            for f in range(f0 + 1, f1):
                k = (f - f0) / (f1 - f0)
                k = k * k * (3 - 2 * k) if a.get("ease", True) else k   # smoothstep，起停比較柔
                add(f, {"mouse": ["move", x0 + dx * k, y0 + dy * k]})
            add(f1, {"mouse": ["up", 0, 0]})
        elif "zoom" in a:    # {"zoom": -300, "from": 0, "to": 60, "x0":960,"y":540}  滾輪縮放（負數＝拉近）
            f0, f1 = a.get("from", 0), a.get("to", 30)
            add(f0, {"mouse": ["move", a.get("x0", 960), a.get("y", 540)]})
            step = a["zoom"] / max(1, f1 - f0)
            for f in range(f0, f1): add(f, {"mouse": ["wheel", 0, step]})
        elif "type" in a:    # {"type": {"selector": "#name", "value": "CNC-07"}, "at": 40, "cps": 12} 逐字輸入
            t = a["type"]; f0 = a.get("at", 0); per = max(1, round(30 / a.get("cps", 12)))
            for i in range(1, len(t["value"]) + 1):
                add(f0 + i * per, {"fill": {"selector": t["selector"], "value": t["value"][:i]}})
        else:
            add(a.get("at", 0), a)
    return out


async def run_shot(cfg, name, shot, out_root, test):
    from playwright.async_api import async_playwright
    W, H = cfg.get("viewport", [1920, 1080]); fps = cfg.get("fps", 30); dt = 1000 / fps
    frames = shot["frames"]; mode = shot.get("mode", "ui")
    od = Path(out_root) / name; od.mkdir(parents=True, exist_ok=True)
    for old in od.glob("*.jpg"): old.unlink()
    async with async_playwright() as p:
        args = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
        if cfg.get("gpu"): args = ["--ignore-gpu-blocklist", "--enable-gpu-rasterization"]
        launch = dict(args=args)
        if cfg.get("channel"): launch["channel"] = cfg["channel"]       # 例如 "chrome"：用本機 Chrome（Mac 上有 GPU，快很多）
        b = await p.chromium.launch(**launch)
        ctx = await b.new_context(viewport={"width": W, "height": H}, device_scale_factor=cfg.get("scale", 1))
        await ctx.add_init_script(path=str(VT))
        for k, v in (cfg.get("local_storage") or {}).items():
            await ctx.add_init_script(f"try{{localStorage.setItem({json.dumps(k)},{json.dumps(v)})}}catch(e){{}}")
        if cfg.get("clear_storage", True):
            await ctx.add_init_script("try{if(!sessionStorage.__ppvs){localStorage.clear();sessionStorage.__ppvs=1}}catch(e){}")
        pg = await ctx.new_page()
        pg.on("pageerror", lambda e: print(f"  ! [{name}] pageerror: {e}", flush=True))
        await pg.goto(shot.get("url", cfg["url"]))
        await pg.wait_for_timeout(cfg.get("load_wait_ms", 1200))
        css = (cine_css(cfg) if mode == "cine" else "") + cfg.get("ui_css", "") + shot.get("css", "")
        if css: await pg.add_style_tag(content=css)
        await pg.evaluate("window.dispatchEvent(new Event('resize'))")
        for a in cfg.get("setup", []) + shot.get("setup", []):
            await do_action(pg, a, name)
            await pg.evaluate(f"__step({dt})")
        for _ in range(int(shot.get("warmup", cfg.get("warmup", 45)))):
            await pg.evaluate(f"__step({dt})")
        acts = expand(shot.get("actions", []), frames)
        q = shot.get("quality", cfg.get("quality", 80))
        for f in range(frames):
            for a in acts.get(f, []): await do_action(pg, a, name)
            await pg.evaluate(f"__step({dt})")
            if test and f % 45 and f != frames - 1: continue
            await pg.screenshot(path=str(od / f"{f:04d}.jpg"), type="jpeg", quality=q)
            if f % 60 == 0: print(f"  {name} {f}/{frames}", flush=True)
        await b.close()
    print(f"✓ {name}（{frames} 格）→ {od}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config"); ap.add_argument("--out", required=True)
    ap.add_argument("--only", default=""); ap.add_argument("--test", action="store_true")
    ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    names = [n for n in cfg["shots"] if not a.only or n in a.only.split(",")]
    if not names: sys.exit("沒有符合的鏡頭")

    async def worker(queue):
        while queue:
            n = queue.pop(0)
            await run_shot(cfg, n, cfg["shots"][n], a.out, a.test)

    async def go():
        # 依照片長平均分給 jobs 個 worker（每個 worker 一次一個瀏覽器）
        names.sort(key=lambda n: -cfg["shots"][n]["frames"])
        buckets = [[] for _ in range(max(1, a.jobs))]
        for i, n in enumerate(names): buckets[i % len(buckets)].append(n)
        await asyncio.gather(*(worker(bk) for bk in buckets))
    asyncio.run(go())


if __name__ == "__main__":
    main()
