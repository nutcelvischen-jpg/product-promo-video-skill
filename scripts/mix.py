#!/usr/bin/env python3
"""最終混音＋合成：旁白（壓縮）＋背景音樂（側鏈壓縮自動閃避人聲）＋音效 → loudnorm → 換掉影片音軌。

用法：
  python mix.py videos/demo --lang zh                       # 用 out/<name>_<lang>.mp4、narration、bgm.wav、sfx.wav
  python mix.py videos/demo --lang zh --music 0.30 --lufs -15 --max-mb 30

參數：
  --music  背景音樂音量（0.25～0.35 適合有旁白的介紹片）
  --lufs   整體響度。YouTube / 網頁 -14～-16；簡報現場播放 -16～-18
  --max-mb 成品超過這個大小時，自動用目標位元率重新壓縮一份 *_small.mp4（傳檔、上傳有上限時用）
"""
import argparse, json, subprocess
from pathlib import Path


def probe_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--lang", default="zh")
    ap.add_argument("--video"); ap.add_argument("--out")
    ap.add_argument("--music", type=float, default=0.30); ap.add_argument("--lufs", type=float, default=-15)
    ap.add_argument("--max-mb", type=float, default=0)
    a = ap.parse_args()
    f = Path(a.folder); name = f.name
    video = Path(a.video) if a.video else f / "out" / f"{name}_{a.lang}.mp4"
    nar = f / f"narration_{a.lang}.wav"; bgm = f / "bgm.wav"; sfx = f / "sfx.wav"
    out = Path(a.out) if a.out else f / "out" / f"{name}_{a.lang}_final.mp4"
    mixwav = f / "out" / f"mix_{a.lang}.wav"
    ins = ["-i", str(nar)]; graph = "[0:a]aresample=44100,pan=stereo|c0=c0|c1=c0,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=150[v];"
    parts = ["[v1]"]; idx = 1
    if bgm.exists():
        ins += ["-i", str(bgm)]
        graph += f"[v]asplit=2[v1][vk];[{idx}:a]volume={a.music}[m];[m][vk]sidechaincompress=threshold=0.03:ratio=5:attack=30:release=500[md];"
        parts.append("[md]"); idx += 1
    else:
        graph += "[v]anull[v1];"
    if sfx.exists():
        ins += ["-i", str(sfx)]; parts.append(f"[{idx}:a]"); idx += 1
    graph += "".join(parts) + f"amix=inputs={len(parts)}:normalize=0,loudnorm=I={a.lufs}:TP=-1.5:LRA=11,aresample=48000[out]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", graph, "-map", "[out]", "-c:a", "pcm_s16le", str(mixwav)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(mixwav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    mb = out.stat().st_size / 1e6
    print(f"✓ {out}（{probe_dur(out):.1f}s，{mb:.1f} MB）")
    if a.max_mb and mb > a.max_mb:
        d = probe_dur(out); kbps = int((a.max_mb * 0.92 * 8000) / d) - 200
        small = out.with_name(out.stem + "_small.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-c:v", "libx264", "-preset", "medium", "-b:v", f"{kbps}k",
                        "-maxrate", f"{int(kbps * 1.5)}k", "-bufsize", f"{kbps * 3}k", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(small)], check=True)
        print(f"✓ 縮小版 {small}（{small.stat().st_size / 1e6:.1f} MB）")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(out), "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if line.strip().startswith("I:"): print("  響度", line.strip())


if __name__ == "__main__":
    main()
