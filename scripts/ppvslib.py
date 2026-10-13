"""product-promo-video-skill 共用函式：讀時間軸、時間運算式、讀寫 wav。"""
import json, wave, re
from pathlib import Path
import numpy as np


class Timeline:
    """讀 motion-video-skill 產生的 timeline_<lang>.json，提供跟 index.html 一樣的時間函式。

    S(i)      第 i 場開始（0 起算）       SE(i)  第 i 場結束
    L(i,j)    第 i 場第 j 句開始           LE(i,j) 第 i 場第 j 句結束
    LM(i,j,k) 第 i 場第 j 句講到 k 比例    END    影片總長
    """

    def __init__(self, path):
        self.d = json.loads(Path(path).read_text(encoding="utf-8"))
        self.sc = self.d["scenes"]
        self.END = self.d["total"]

    def S(self, i): return self.sc[i]["start"]
    def SE(self, i): return self.sc[i]["start"] + self.sc[i]["dur"]
    def L(self, i, j): return self.sc[i]["lines"][j]["start"]
    def LE(self, i, j): return self.sc[i]["lines"][j]["end"]
    def LM(self, i, j, k): return self.L(i, j) + (self.LE(i, j) - self.L(i, j)) * k

    def ev(self, expr, extra=None):
        """把 "L(4,2)-0.1"、"S(1)+2*BAR"、"END-3" 這類字串算成秒數。數字直接回傳。"""
        if isinstance(expr, (int, float)):
            return float(expr)
        if not re.fullmatch(r"[\sA-Za-z0-9_().,+\-*/]+", expr):
            raise ValueError(f"時間運算式只能有數字、+-*/ 和 S/L/LE/LM/SE/END：{expr}")
        ns = {"S": self.S, "SE": self.SE, "L": self.L, "LE": self.LE, "LM": self.LM, "END": self.END}
        ns.update(extra or {})
        return float(eval(expr, {"__builtins__": {}}, ns))


def read_wav(path, mono=False):
    with wave.open(str(path)) as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        assert w.getsampwidth() == 2, f"{path} 需要 16-bit PCM"
        x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32).reshape(-1, ch) / 32768
    if mono: x = x.mean(1)
    elif ch == 1: x = np.repeat(x, 2, axis=1)
    return x, sr


def write_wav(path, x, sr):
    x = np.clip(x, -1, 1)
    ch = 1 if x.ndim == 1 else x.shape[1]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
