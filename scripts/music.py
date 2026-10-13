#!/usr/bin/env python3
"""用 loop 素材編排背景音樂，段落起落綁在旁白時間軸上。

用法：
  python music.py music.json --timeline videos/demo/timeline_zh.json --out videos/demo/bgm.wav

music.json 範例（時間可以寫運算式，見 ppvslib.Timeline.ev；BAR = 一小節秒數）：
{
  "bpm": 100,
  "anchor": "S(1)+0.1",              // 讓某一小節的強拍剛好落在這個時間（通常是產品登場那一刻）
  "peak": 0.89,
  "tracks": [
    {"file": "loops/synth.wav", "gain": [[0,0],[1,0.55],["S(1)",0.7],["END-3.2",0.7],["END",0]],
     "lowpass": [[0,500],["S(1)-0.3",2600],["S(1)",18000]]},
    {"file": "loops/bass.wav",  "gain": [[0,0],["S(1)-2*BAR",0],["S(1)",0.8],["END-3",0.5],["END",0]]},
    {"file": "loops/beat.wav",  "gain": [[0,0],["S(1)-0.02",0],["S(1)",0.75],["L(4,2)-0.1",0.75],["L(4,2)",0],
                                         ["L(4,2)+2*BAR-0.1",0],["L(4,2)+2*BAR",0.75],["S(7)",0.75],["S(7)+0.3",0]]}
  ]
}
gain / lowpass 是 [時間, 值] 的折線，中間線性內插。所有 loop 必須同一個 BPM、同一個調（同一組 Apple Loops 名稱最保險）。
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ppvslib import Timeline, read_wav, write_wav   # noqa: E402


def resample(x, sr, target):
    if sr == target: return x
    n = int(len(x) * target / sr); t = np.linspace(0, len(x) - 1, n)
    return np.stack([np.interp(t, np.arange(len(x)), x[:, c]) for c in range(x.shape[1])], 1).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config"); ap.add_argument("--timeline", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8")); base = Path(a.config).parent
    tl = Timeline(a.timeline); SR = cfg.get("sr", 44100)
    BAR = 4 * 60 / cfg["bpm"]; ev = lambda e: tl.ev(e, {"BAR": BAR})
    N = int((tl.END + 0.5) * SR); tt = np.arange(N) / SR
    anchor = ev(cfg.get("anchor", 0))
    mix = np.zeros((N, 2), np.float32)
    for tr in cfg["tracks"]:
        x, sr = read_wav(base / tr["file"]); x = resample(x, sr, SR)
        # 由 anchor 往前回推，讓 loop 起點對齊小節
        start = int(round(anchor * SR)) % len(x) - len(x)
        lay = np.zeros((N, 2), np.float32); i = start
        while i < N:
            s0, s1 = max(i, 0), min(i + len(x), N)
            lay[s0:s1] += x[s0 - i:s1 - i]; i += len(x)
        if "lowpass" in tr:
            ts, vs = zip(*[(ev(p[0]), p[1]) for p in tr["lowpass"]])
            cut = np.interp(tt, ts, vs); al = 1 - np.exp(-2 * np.pi * cut / SR)
            z = np.zeros(2, np.float32); y = np.empty_like(lay)
            for k in range(N):
                z += al[k] * (lay[k] - z); y[k] = z
            lay = y
        ts, gs = zip(*[(ev(p[0]), p[1]) for p in tr["gain"]])
        mix += lay * np.interp(tt, ts, gs).astype(np.float32)[:, None]
        print(f"  + {tr['file']}")
    mix *= cfg.get("peak", 0.89) / (np.abs(mix).max() + 1e-9)
    write_wav(a.out, mix, SR)
    print(f"✓ {a.out}（{N / SR:.1f}s，BPM {cfg['bpm']}，強拍對齊 {anchor:.2f}s）")


if __name__ == "__main__":
    main()
