# 範例：CNC 工廠數位孿生 介紹影片（企業客戶版，90 秒）

產品：Three.js CNC 工廠數位孿生（模擬生產、電力、太陽能、碳排）。觀眾：企業客戶。片尾：ICMA Lab。

| 檔案 | 內容 |
|---|---|
| `script.json` | 8 場行銷腳本（痛點→登場→功能→圖層→情境→碳排→擴充→署名） |
| `shots.json` | 10 個鏡頭：5 個 3D 電影鏡頭（cine）＋5 個介面鏡頭（ui） |
| `index.html` | 完整動畫（瀏覽器框傾斜浮入、推鏡＋標註、公式卡、KPI 三卡、IoT 架構圖、Logo） |
| `music.json` | Apple Loops「Forward Progress」Synth/Bass/Guitar ＋「Matchbox Beat 01」，100 BPM |
| `sfx.json` | 11 個轉場 whoosh、3 個 boom、3 個 tick |

重現步驟（需要 factory-twin 產品本體，放在 http://localhost:8766）：
```bash
python <P>/scripts/new_promo.py videos/cnc-twin --mv <MV>
cp <P>/examples/cnc-twin/*.json <P>/examples/cnc-twin/index.html videos/cnc-twin/
python <P>/scripts/capture.py videos/cnc-twin/shots.json --out videos/cnc-twin/assets/clips --jobs 2
python <MV>/scripts/tts.py videos/cnc-twin --lang zh
python <P>/scripts/align_timeline.py videos/cnc-twin --mv <MV> --target 90
python <MV>/scripts/render.py videos/cnc-twin --preview && python <MV>/scripts/render.py videos/cnc-twin --sheet
python <P>/scripts/music.py videos/cnc-twin/music.json --timeline videos/cnc-twin/timeline_zh.json --out videos/cnc-twin/bgm.wav
python <P>/scripts/sfx.py videos/cnc-twin/sfx.json --timeline videos/cnc-twin/timeline_zh.json --out videos/cnc-twin/sfx.wav
python <MV>/scripts/render.py videos/cnc-twin --lang zh --crf 18
python <P>/scripts/mix.py videos/cnc-twin --lang zh --max-mb 30
```

製作時遇到並已寫進 skill 的坑：
- 圖層切換在小畫面看不出差異 → 請產品端加強 3D 顏色與粒子，再拍。
- 「場外太陽能」同時是清單項目與鏡頭按鈕 → 文字完全相同優先。
- `.glass` 的 `position:relative` 讓公式卡跑到畫面外 → `.card` 強制 absolute。
- TTS 比估計長 6% → `align_timeline.py --target 90`。
