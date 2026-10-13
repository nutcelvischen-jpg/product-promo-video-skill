#!/usr/bin/env python3
"""配音後處理：整體加速（不變調）＋依實際停頓對齊每句字幕，重建 narration 與 timeline。

為什麼需要：
  motion-video-skill 的 tts.py 每場只產生一個音檔，句子的時間是「按字數比例估計」的。
  產品介紹影片的畫面切換要精準落在句子上，所以這裡用靜音偵測，把句界吸附到真正的停頓。
  另外 TTS 常比預計長 5～10%，可用 --tempo 整體加速（ffmpeg atempo，音高不變）。

用法（在影片資料夾的上一層執行）：
  python align_timeline.py videos/demo --mv .agents/skills/motion-video --tempo 1.06
  python align_timeline.py videos/demo --mv ... --target 90      # 自動算 tempo，讓總長接近 90 秒

第一次執行會把 audio_<lang>/ 備份到 audio_<lang>_raw/，之後都從 raw 重新處理，可以反覆調。
改了某場台詞並用 tts.py --only s03 重做後：加 --refresh s03，把新檔收進 raw。
"""
import argparse, json, shutil, subprocess, sys, wave, array
from pathlib import Path


def gaps(pcm, rate, minsil=0.16, thresh=500):
    a = array.array("h", pcm); win = rate // 100
    loud = [max(abs(x) for x in a[i:i + win]) > thresh for i in range(0, len(a) - win, win)]
    out, i = [], 0
    while i < len(loud):
        if not loud[i]:
            j = i
            while j < len(loud) and not loud[j]: j += 1
            if (j - i) * 0.01 >= minsil and i > 0 and j < len(loud):
                out.append(((i + j) / 2 * 0.01, (j - i) * 0.01))
            i = j
        else:
            i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--mv", required=True, help="motion-video skill 資料夾")
    ap.add_argument("--lang", default="zh"); ap.add_argument("--tempo", type=float, default=1.0)
    ap.add_argument("--target", type=float, help="目標總長（秒），自動計算 tempo")
    ap.add_argument("--minsil", type=float, default=0.16, help="視為停頓的最短靜音（秒）")
    ap.add_argument("--refresh", default="", help="重做過 TTS 的場景（逗號分隔，例 s03,s05）：先把新檔複製進 raw 備份")
    a = ap.parse_args()
    sys.path.insert(0, str(Path(a.mv) / "scripts"))
    from mvlib import LEAD_IN, GAP, TAIL, load_script, split_lines   # noqa
    folder = Path(a.folder); lang = a.lang
    data = load_script(folder)
    src = folder / f"audio_{lang}"; raw = folder / f"audio_{lang}_raw"
    if not raw.exists():
        shutil.copytree(src, raw); print(f"已備份原始配音 → {raw}")
    for sid in [x for x in a.refresh.split(",") if x]:
        shutil.copy(src / f"{sid}.wav", raw / f"{sid}.wav"); print(f"已更新 raw/{sid}.wav")

    ids = [sc["id"] for sc in data["scenes"]]
    def dur(p):
        with wave.open(str(p)) as w: return w.getnframes() / w.getframerate()
    raw_total = sum(dur(raw / f"{i}.wav") for i in ids)
    fixed = LEAD_IN + GAP * (len(ids) - 1) + TAIL
    tempo = a.tempo
    if a.target:
        tempo = raw_total / max(1, a.target - fixed)
        print(f"原始語音 {raw_total:.1f}s，目標 {a.target}s → tempo {tempo:.3f}")
    if not 0.8 <= tempo <= 1.25:
        print(f"⚠ tempo {tempo:.2f} 超出建議範圍（0.9～1.12 聽起來最自然），請考慮改台詞長度")

    for i in ids:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw / f"{i}.wav")]
        if abs(tempo - 1) > 1e-3: cmd += ["-filter:a", f"atempo={tempo:.4f}"]
        cmd += ["-ar", "24000", "-ac", "1", "-sample_fmt", "s16", str(src / f"{i}.wav")]
        subprocess.run(cmd, check=True)

    RATE = 24000
    t = LEAD_IN; tl = {"lang": lang, "lead_in": LEAD_IN, "gap": GAP, "tempo": round(tempo, 4), "scenes": []}
    merged = bytearray(b"\x00\x00" * int(RATE * LEAD_IN))
    for sc in data["scenes"]:
        with wave.open(str(src / f"{sc['id']}.wav")) as w:
            pcm = w.readframes(w.getnframes())
        d = len(pcm) / 2 / RATE
        lines = split_lines(sc[lang], lang, t, d)
        g = gaps(pcm, RATE, a.minsil); used = set()
        for k in range(1, len(lines)):
            est = lines[k]["start"] - t
            cands = [(abs(c - est) - 0.3 * L, c) for c, L in g if c not in used and abs(c - est) < 1.6]
            if cands:
                c = min(cands)[1]; used.add(c)
                lines[k - 1]["end"] = round(t + c, 3); lines[k]["start"] = round(t + c, 3)
            else:
                print(f"  ⚠ {sc['id']} 第 {k} 句找不到停頓，沿用估計值")
        print(f"  {sc['id']} {d:5.2f}s  句界 {[round(l['start'] - t, 2) for l in lines[1:]]}")
        tl["scenes"].append({"id": sc["id"], "start": round(t, 3), "dur": round(d, 3), "lines": lines})
        merged += pcm + b"\x00\x00" * int(RATE * GAP); t += d + GAP
    tl["total"] = round(t + TAIL, 3)
    merged += b"\x00\x00" * int(RATE * TAIL)
    with wave.open(str(folder / f"narration_{lang}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(bytes(merged))
    (folder / f"timeline_{lang}.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ 總長 {tl['total']} 秒。下一步：python {a.mv}/scripts/render.py {folder} --preview")


if __name__ == "__main__":
    main()
