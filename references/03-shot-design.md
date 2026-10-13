# 03 設計鏡頭：從台詞到畫面

## 1. 為什麼用逐格擷取，而不是螢幕錄影

- 3D／WebGL 在沒有 GPU 的電腦上只有幾 fps，錄影會卡。
- 錄影無法精準控制「第幾秒按下按鈕」，之後很難跟台詞對齊。
- `capture.py` 注入 `vt.js`（虛擬時鐘）：頁面的 `performance.now`、`requestAnimationFrame`、`setTimeout` 等都只在 `__step()` 時前進。截一張、推進 1/30 秒、再截一張 → 任何電腦都是平順 30fps，而且每次重拍結果一樣。

> 不要用 Playwright 的 `page.clock.install()`，它會凍結瀏覽器本身的繪製，截圖會永遠卡住。
> 限制：CSS transition 仍走真實時間（截圖慢時看起來瞬間完成）、`<video>` 與 Web Worker 不受控制。

## 2. 從 beat 推導鏡頭

對每一句台詞問三個問題：

1. **觀眾要看到什麼才會相信這句話？**（一個狀態、一個變化、一個關係）
2. **那個東西在產品的哪裡？**（3D 場景／某個面板／某個數字）
3. **它需要多少「上下文」？**（要看到整個介面才懂，還是只看局部就懂）

| 需要的畫面 | 鏡頭模式 | 之後在動畫裡 |
|---|---|---|
| 氣勢、整體感、3D 美感 | `cine`（只留 3D 畫布、全螢幕） | 緩慢推近、文字放在留白處 |
| 一個操作引發的變化 | `ui`（整個介面） | 推鏡到變化的地方 |
| 介面全貌、「這是一個真的系統」 | `ui` | 放進傾斜的瀏覽器框、或全螢幕 |
| 看不見的機制（資料流、計算） | 不拍，用動畫畫 | 圖解、公式、架構圖 |

一個鏡頭只做一件事。UI 鏡頭拍整個介面就好，**推鏡在動畫裡做**——想放大哪裡都可以，不用重拍。

## 3. 動作的時間

- 關鍵動作放在**第 20～30 格**：先讓觀眾看 0.7～1 秒「之前」，「之後」的變化才有對比。
- 鏡頭長度 ≥ 該句台詞長度 + 2 秒（不夠時畫面會停在最後一格）。通常 240～270 格。
- 記下每個動作的格數，動畫對時要用（見 05）。
- 前後對比用同一個鏡頭、動作放中間，比拍兩個鏡頭好接。

## 4. 運鏡（cine 鏡頭）

- 用滑鼠拖曳做環繞（OrbitControls：水平約 1080px ≈ 360°）。70° 以內（約 200px）最安全，不會轉到背面。
- 起點和終點都要是好看的構圖——用 `--test` 看第 0、中間、最後一格。
- 要切換相機預設（例如「內部視角」）時，在第 4～6 格按下，讓飛行過程被完整拍到；拖曳從飛行結束後開始。
- 速度：機械或角色動作用產品的 1× 速度才自然；需要數字明顯變化的 UI 鏡頭可以加快模擬速度。

## 5. shots.json 規格

```jsonc
{
  "url": "http://localhost:8766/",
  "viewport": [1920, 1080], "fps": 30, "quality": 80,
  "warmup": 45,                       // 開拍前先跑的格數（場景載入、數字開始動）
  "load_wait_ms": 1200,
  "clear_storage": true,              // 每個鏡頭前清 localStorage
  "local_storage": {"k": "v"},        // 需要預設狀態時
  "channel": "chrome", "gpu": true,   // （選用）Mac 本機 Chrome＋GPU，快 5～10 倍
  "cine": { "container": ".scene-panel", "canvas_host": "#canvas-wrap", "background": "#101820", "extra_css": "" },
  "ui_css": "",                       // 所有鏡頭都套的 CSS（例如隱藏提示文字）
  "setup": [],                        // 所有鏡頭開拍前的動作
  "shots": {
    "<名稱>": {
      "mode": "cine" | "ui",
      "frames": 255,
      "setup": [],                    // 開拍前（不會被拍到）
      "actions": [],                  // 拍攝中
      "css": "", "url": "", "warmup": 45
    }
  }
}
```

### 動作

| 動作 | 寫法 | 說明 |
|---|---|---|
| 點按鈕（文字） | `{"at": 20, "click": "按鈕文字"}` | 先比對完全相同，再比對開頭相同；也比對 aria-label、title。`"scope"` 可改搜尋範圍 |
| 點元素（選擇器） | `{"at": 20, "click_sel": "#id"}` | 同名按鈕時用 |
| 環繞拖曳 | `{"drag": 200, "dy": 0, "from": 0, "to": 254, "x0": 960, "y": 540}` | 預設 smoothstep 起停；`"ease": false` 等速 |
| 滾輪縮放 | `{"zoom": -300, "from": 0, "to": 60}` | 負數拉近 |
| 逐字輸入 | `{"type": {"selector": "#name", "value": "文字"}, "at": 40, "cps": 10}` | 先用 fill 清空 |
| 填值 | `{"at": 40, "fill": {"selector": "#name", "value": ""}}` | 會觸發 input/change（React/Vue 可用） |
| 下拉選單 | `{"select": {"selector": "select", "index": -1, "label": "3×"}}` | |
| 執行 JS | `{"at": 10, "eval": "..."}` | |
| 按鍵 | `{"at": 10, "key": "Escape"}` | |

## 6. 流程

```bash
python <P>/scripts/capture.py shots.json --out /tmp/test --test     # 每 45 格存一張
python <P>/scripts/contact_sheet.py clips /tmp/test                  # 看 sheet_clips.jpg
python <P>/scripts/capture.py shots.json --out videos/<名稱>/assets/clips --jobs 2   # 正式
```
- log 出現「找不到按鈕文字」= 沒按到。
- 沒有 GPU：3D 全螢幕約 1～2.5 秒／格、UI 約 1 秒／格。背景執行，同時做配音與動畫。
- 只重拍某幾個：`--only a,b`。
