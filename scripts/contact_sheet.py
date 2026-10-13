#!/usr/bin/env python3
"""檢查用總覽圖。

  python contact_sheet.py clips videos/demo/assets/clips          # 每個鏡頭取 4 格（頭、1/3、2/3、尾），檢查拍得對不對
  python contact_sheet.py video videos/demo/out/demo_zh_final.mp4 --every 4   # 成片每 4 秒一張
  python contact_sheet.py video demo.mp4 --at 2,9,14.5,30          # 指定秒數
輸出：同資料夾的 sheet_clips.jpg / sheet_video.jpg（一定要打開來看）
"""
import argparse, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw

W, H = 480, 270


def grid(images, labels, cols, out):
    rows = (len(images) + cols - 1) // cols
    s = Image.new("RGB", (W * cols, H * rows), (10, 10, 10)); d = ImageDraw.Draw(s)
    for i, (im, lb) in enumerate(zip(images, labels)):
        x, y = (i % cols) * W, (i // cols) * H
        s.paste(im.resize((W, H)), (x, y)); d.rectangle([x, y, x + 9 * len(lb) + 10, y + 20], fill=(0, 0, 0)); d.text((x + 5, y + 4), lb, fill=(255, 255, 255))
    s.save(out, quality=82); print(f"✓ {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["clips", "video"]); ap.add_argument("path")
    ap.add_argument("--every", type=float, default=4); ap.add_argument("--at", default="")
    a = ap.parse_args(); p = Path(a.path)
    if a.kind == "clips":
        ims, lbs = [], []
        for d in sorted(x for x in p.iterdir() if x.is_dir()):
            fs = sorted(d.glob("*.jpg"))
            if not fs: continue
            for k in (0, len(fs) // 3, 2 * len(fs) // 3, len(fs) - 1):
                ims.append(Image.open(fs[k])); lbs.append(f"{d.name} {fs[k].stem}")
        grid(ims, lbs, 4, p / "sheet_clips.jpg")
    else:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)
        ts = [float(x) for x in a.at.split(",")] if a.at else [round(i * a.every, 2) for i in range(int(dur / a.every) + 1)]
        ims, lbs = [], []
        with tempfile.TemporaryDirectory() as td:
            for t in ts:
                o = Path(td) / f"{t:07.2f}.jpg"
                subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(min(t, dur - .05)), "-i", str(p), "-frames:v", "1", "-vf", f"scale={W}:{H}", str(o)], check=True)
                ims.append(Image.open(o).copy()); lbs.append(f"{t:.1f}s")
        grid(ims, lbs, 4, p.with_name("sheet_video.jpg"))


if __name__ == "__main__":
    main()
