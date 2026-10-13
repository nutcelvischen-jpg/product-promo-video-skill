#!/usr/bin/env python3
"""建立一支產品介紹影片的資料夾（以 motion-video-skill 的 wide 版型為底，換成 promo-wide 範本）。

  python new_promo.py videos/my-product --mv .agents/skills/motion-video

會產生：
  videos/my-product/
    index.html        ← promo-wide 範本（素材層、放大、標註、大字、Logo）
    script.json       ← 5 場景行銷腳本範本
    shots.json        ← 鏡頭清單範本（capture.py 用）
    music.json / sfx.json
    assets/fonts/     ← 預設 Manrope；換成產品字型
    assets/clips/     ← capture.py 輸出
    _runtime/         ← motion-video-skill 的 runtime（不要改）
"""
import argparse, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("folder"); ap.add_argument("--mv", required=True)
    a = ap.parse_args(); f = Path(a.folder); mv = Path(a.mv)
    if f.exists() and any(f.iterdir()): sys.exit(f"{f} 已存在且不是空的")
    subprocess.run([sys.executable, str(mv / "scripts" / "new_episode.py"), str(f), "--template", "wide"], check=True)
    for p in (f / "assets").glob("host.*"): p.unlink()
    t = HERE / "templates" / "promo-wide"
    shutil.copy(t / "index.html", f / "index.html"); shutil.copy(t / "script.json", f / "script.json")
    shutil.copytree(t / "assets" / "fonts", f / "assets" / "fonts", dirs_exist_ok=True)
    for n in ("shots.json", "music.json", "sfx.json"):
        shutil.copy(t / n, f / n)
    (f / "assets" / "clips").mkdir(parents=True, exist_ok=True)
    print(f"✓ 已建立 {f}\n  下一步：改 script.json → 改 shots.json → python {HERE}/scripts/capture.py {f}/shots.json --out {f}/assets/clips --test")


if __name__ == "__main__":
    main()
