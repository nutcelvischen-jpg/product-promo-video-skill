#!/usr/bin/env python3
"""用程式合成轉場音效（whoosh / boom / tick / riser），不需要下載任何音效素材。

用法：
  python sfx.py sfx.json --timeline videos/demo/timeline_zh.json --out videos/demo/sfx.wav

sfx.json 範例：
{
  "cues": [
    {"type": "whoosh", "at": "S(1)-0.3", "gain": 0.2},
    {"type": "boom",   "at": "S(1)+0.15", "gain": 0.5},
    {"type": "tick",   "at": "LM(0,1,0.05)", "gain": 0.22, "pan": -0.4},
    {"type": "whoosh", "at": ["S(2)", "L(2,1)-0.35", "S(3)-0.3"], "gain": 0.16, "offset": -0.25, "alt_pan": 0.3}
  ]
}
- at 可以是一個運算式或清單（同一種音效放很多次）。
- offset：整體再提前/延後（whoosh 建議 -0.25，讓峰值落在畫面切換點）。
- alt_pan：清單中的音效左右交替。
- dur：whoosh/riser 長度（預設 0.8 / 2.0 秒）。
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ppvslib import Timeline, write_wav   # noqa: E402

SR = 44100
rng = np.random.default_rng(7)


def bp_noise(dur, f0, f1, q=3.0):
    n = int(dur * SR); x = rng.standard_normal(n).astype(np.float32)
    f = np.geomspace(f0, f1, n); y = np.zeros(n, np.float32); s1 = s2 = 0.0
    for i in range(n):
        fc = 2 * np.sin(np.pi * f[i] / SR); s1 += fc * (x[i] - s1 - s2 / q); s2 += fc * s1; y[i] = s2
    return y / (np.abs(y).max() + 1e-9)


def whoosh(dur=.8):
    a = bp_noise(dur, 300, 4500); return a * np.sin(np.linspace(0, np.pi, len(a))) ** 2


def riser(dur=2.0):
    a = bp_noise(dur, 200, 6000, q=5); e = np.linspace(0, 1, len(a)) ** 2.2; e[-int(.05 * SR):] *= np.linspace(1, 0, int(.05 * SR)); return a * e


def boom(dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * (48 + 30 * np.exp(-t * 12)) * t) * np.exp(-t * 3.2)
    return (s + rng.standard_normal(len(t)) * np.exp(-t * 40) * .25).astype(np.float32)


def tick(dur=.09):
    t = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * 1650 * t) * np.exp(-t * 60) + .4 * np.sin(2 * np.pi * 3300 * t) * np.exp(-t * 90)).astype(np.float32)


GEN = {"whoosh": whoosh, "riser": riser, "boom": boom, "tick": tick}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config"); ap.add_argument("--timeline", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8")); tl = Timeline(a.timeline)
    N = int((tl.END + .5) * SR); out = np.zeros((N, 2), np.float32); n = 0
    for c in cfg["cues"]:
        ats = c["at"] if isinstance(c["at"], list) else [c["at"]]
        for k, at in enumerate(ats):
            sig = GEN[c["type"]](c["dur"]) if "dur" in c else GEN[c["type"]]()
            pan = c.get("pan", 0.0)
            if "alt_pan" in c: pan = c["alt_pan"] * (1 if k % 2 else -1)
            t = tl.ev(at) + c.get("offset", 0); i = max(0, int(t * SR)); j = min(N, i + len(sig))
            g = c.get("gain", .2)
            out[i:j, 0] += sig[:j - i] * g * (1 - max(0, pan)); out[i:j, 1] += sig[:j - i] * g * (1 + min(0, pan)); n += 1
    write_wav(a.out, out, SR)
    print(f"✓ {a.out}（{n} 個音效）")


if __name__ == "__main__":
    main()
