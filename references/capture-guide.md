# 產品畫面擷取（capture.py）完整說明

## 1. 為什麼不用螢幕錄影

- 3D／WebGL 在沒有 GPU 的電腦上只有個位數 fps，錄出來卡頓。
- 錄影無法精準控制「第幾秒按下按鈕」，之後很難跟配音對齊。
- 本 skill 用**虛擬時鐘**：`vt.js` 在頁面載入前取代 `performance.now`、`Date.now`、`requestAnimationFrame`、`setTimeout`、`setInterval`。頁面時間只在 `__step(33.33ms)` 時前進，截完一張再前進下一格 → 不管電腦多慢都是平順 30fps，而且每次重拍結果一樣。

> ⚠ 不要用 Playwright 內建的 `page.clock.install()`：它會連瀏覽器自己的繪製排程一起凍結，`page.screenshot()` 會永遠卡住。

限制：CSS transition／animation 仍走真實時間（截圖慢時會變成瞬間完成，通常看不出來）；`<video>` 元素不受控制；Web Worker 裡的計時器不受控制。

## 2. shots.json 完整格式

```jsonc
{
  "url": "http://localhost:8766/",       // 產品網址（先自己啟動 server）
  "viewport": [1920, 1080],              // 一律 1920×1080，跟影片一樣大
  "fps": 30,
  "quality": 80,                         // JPG 品質（80 已足夠，檔案約 100～250KB／張）
  "warmup": 45,                          // 開拍前先跑幾格（讓場景載入、數字開始跳）
  "load_wait_ms": 1200,
  "clear_storage": true,                 // 每個鏡頭開始前清 localStorage（避免上次的設定殘留）
  "local_storage": {"key": "value"},     // 需要預設狀態時（例如已登入的 token、某個設定）
  "channel": "chrome", "gpu": true,      // （選用）Mac 上用本機 Chrome＋GPU，快很多
  "cine": {                              // 「電影鏡頭」模式：把 3D 畫布容器放大成全螢幕、隱藏其他東西
    "container": ".scene-area",          //   3D 區塊的外層容器
    "canvas_host": "#scene",             //   放 <canvas> 的那層（保留，其他兄弟元素隱藏）
    "background": "#18242a",
    "extra_css": ""
  },
  "ui_css": "#toast{transition:none!important}",   // 所有鏡頭都加的 CSS（例如隱藏游標提示）
  "setup": [ ... ],                      // 所有鏡頭開拍前都做的動作
  "shots": {
    "<鏡頭名稱>": {
      "mode": "cine" | "ui",
      "frames": 255,                     // 30 格 = 1 秒；建議 240～270
      "setup": [ ... ],                  // 開拍前（warmup 之前）做的動作，不會被拍到
      "actions": [ ... ],                // 拍攝中的動作
      "css": "",                         // 只有這個鏡頭加的 CSS
      "url": "",                         // 這個鏡頭用不同網址（例如直接開某個子頁）
      "warmup": 45,
      "quality": 80
    }
  }
}
```

找 `cine.container` 的方法：
```js
let e=document.querySelector('canvas'),out=[];while(e){out.push(e.tagName+'#'+e.id+'.'+[...e.classList].join('.'));e=e.parentElement}out
```
通常選 canvas 往上第 2 層（有圓角、標題、按鈕的那個面板）當 container，canvas 的直接父層當 canvas_host。

## 3. 動作（actions / setup）

| 動作 | 寫法 | 說明 |
|---|---|---|
| 點按鈕（用文字） | `{"at": 20, "click": "雲層遮蔽"}` | 先找文字**完全相同**，再找**開頭相同**；也比對 aria-label、title。`"scope": "button,a,li"` 可改搜尋範圍 |
| 點元素（用選擇器） | `{"at": 20, "click_sel": "#export"}` | 同名按鈕會按錯時用這個 |
| 環繞拖曳 | `{"drag": 220, "dy": 0, "from": 0, "to": 254, "x0": 860, "y": 540}` | OrbitControls：水平 1080px ≈ 360°，所以 220px ≈ 70°。預設 smoothstep 起停柔和；`"ease": false` 等速 |
| 滾輪縮放 | `{"zoom": -300, "from": 0, "to": 60}` | 負數＝拉近 |
| 逐字輸入 | `{"type": {"selector": "#device-name", "value": "CNC-07"}, "at": 42, "cps": 10}` | 每秒 10 個字；先用 fill 清空 |
| 直接填值 | `{"at": 40, "fill": {"selector": "#name", "value": ""}}` | 會觸發 input / change 事件（React/Vue 也吃得到） |
| 下拉選單 | `{"select": {"selector": "select", "index": -1, "label": "3×"}}` | index -1 = 最後一個 select |
| 任意 JS | `{"at": 10, "eval": "document.querySelector('#x').scrollIntoView()"}` | |
| 按鍵 | `{"at": 10, "key": "Escape"}` | |

## 4. 鏡頭設計原則

1. **一個鏡頭只做一件事**，對應一句台詞。
2. **關鍵動作放第 20～30 格**：前面留 0.7～1 秒讓觀眾看清楚「之前」，之後的「變化」才有對比。
3. 長度 = 該句台詞長度 + 2 秒以上餘裕（不夠時畫面會停在最後一格）。
4. 電影鏡頭（cine）的環繞：
   - 70° 以內，避免轉到背面；起點與終點都要好看（用 `--test` 看第 0、135、254 格）。
   - 會切換鏡頭預設（例如「廠房內部」）時，按鈕在第 4～6 格按下，相機飛行動畫被完整拍到；拖曳從第 80～90 格開始（等相機飛完）。
   - 3D 主體在畫面偏左或偏右沒關係，動畫裡可以用 `x` 位移與 `scale` 再構圖。
5. UI 鏡頭不用追求局部，拍整個介面，**推鏡在動畫裡做**（`zoomTo`），想放大哪裡都可以。
6. 模擬速度：電影鏡頭用 1×（機械動作自然）；要看數字跳動的 UI 鏡頭用 3×。
7. 同一個產品要拍「前後對比」時，拍同一個鏡頭、動作放中間，比拍兩個鏡頭好接。

## 5. 速度與平行

| 環境 | 3D 全螢幕 | UI |
|---|---|---|
| 雲端／無 GPU（SwiftShader） | 1～2.5 秒／格 | 0.8～1 秒／格 |
| Mac + `"channel":"chrome","gpu":true` | 0.1～0.2 秒／格 | 0.1 秒／格 |

- `--jobs 2`：兩個瀏覽器同時拍（雙核以上才有用）。
- `--only a,b`：只重拍某幾個鏡頭。
- 背景執行：`nohup python capture.py ... > capture.log 2>&1 &`，用 `tail capture.log` 看進度。

## 6. 檢查

```bash
python contact_sheet.py clips videos/<名稱>/assets/clips
```
每個鏡頭 4 格（頭、1/3、2/3、尾）。確認：動作有發生、沒有錯誤畫面、環繞終點好看、toast/彈窗沒有擋住重點。
