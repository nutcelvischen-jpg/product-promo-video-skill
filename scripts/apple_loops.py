#!/usr/bin/env python3
"""（只能在 Mac 上用）從 GarageBand 內建的 Apple Loops 找配樂素材並轉成 wav。

Apple Loops 可免版稅用在自己的影片作品中（不能單獨轉售 loop 本身）。

  python apple_loops.py list                       # 列出各曲風的 loop「家族」與長度
  python apple_loops.py list --genre Chillwave     # 只看某曲風
  python apple_loops.py beats --bars-of 9.6        # 找跟 9.6 秒（100 BPM 四小節）同長度倍數的鼓組
  python apple_loops.py convert "07 Chillwave/Forward Progress Synth" "07 Chillwave/Matchbox Beat 01" --out loops/

選曲原則：
  - 同一家族（名稱前綴相同，例如 Forward Progress Bass / Synth / Guitar）= 同 BPM、同調，可以直接疊。
  - 鼓組另外找：長度必須是旋律 loop 的整數比（9.6 秒旋律 ↔ 4.8 或 9.6 秒鼓組）。
  - 企業／科技產品：Chillwave、Electro House 裡較平穩的家族；避開人聲（Vox）與太吵的 Dubstep。
"""
import argparse, subprocess, re
from collections import defaultdict
from pathlib import Path

ROOT = Path("/Library/Audio/Apple Loops/Apple")


def dur(f):
    r = subprocess.run(["afinfo", str(f)], capture_output=True, text=True).stdout
    m = re.search(r"estimated duration:\s*([\d.]+)", r)
    return float(m.group(1)) if m else 0.0


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list"); l.add_argument("--genre", default="")
    b = sub.add_parser("beats"); b.add_argument("--bars-of", type=float, required=True)
    c = sub.add_parser("convert"); c.add_argument("names", nargs="+"); c.add_argument("--out", default="loops")
    a = ap.parse_args()
    if a.cmd == "list":
        for g in sorted(ROOT.iterdir()):
            if not g.is_dir() or (a.genre and a.genre.lower() not in g.name.lower()): continue
            fam = defaultdict(list)
            for f in g.glob("*.caf"):
                fam[re.sub(r"\s+(Bass|Synth|Guitar|Beat|Keys|Lead|Pad|Vox|Drums?|Piano|Strings?)(\s+\d+)?$", "", f.stem)].append(f)
            print(f"== {g.name}")
            for k, fs in sorted(fam.items(), key=lambda kv: -len(kv[1])):
                if len(fs) >= 2:
                    print(f"  {k:28s} {len(fs)} 個  {dur(fs[0]):.2f}s  [{', '.join(sorted(x.stem[len(k):].strip() for x in fs))}]")
    elif a.cmd == "beats":
        want = [a.bars_of / 4, a.bars_of / 2, a.bars_of, a.bars_of * 2]
        for f in sorted(ROOT.rglob("*.caf")):
            if not re.search(r"beat|drum|groove|perc", f.stem, re.I): continue
            d = dur(f)
            if any(abs(d - w) < .02 for w in want): print(f"  {d:6.2f}s  {f.relative_to(ROOT)}")
    else:
        out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
        for n in a.names:
            src = ROOT / (n if n.endswith(".caf") else n + ".caf")
            dst = out / (Path(n).stem.replace(" ", "_") + ".wav")
            subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@44100", str(src), str(dst)], check=True)
            print(f"✓ {dst}（{dur(src):.2f}s）")


if __name__ == "__main__":
    main()
