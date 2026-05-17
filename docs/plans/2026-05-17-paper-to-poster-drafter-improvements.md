# paper-to-poster-drafter SKILL.md 改善設計

## 対象ファイル

`.codex/skills/paper-to-poster-drafter/SKILL.md`

## 変更概要

4箇所を変更し、出力品質とプロセス安定性を向上させる。
いずれの変更も特定の論文・テンプレートに依存しない汎用ルールとして記述する。

---

## ① 概要ビジュアル指示 — SVG生成フローを追加

### 変更方針

- 3ステップ対話フロー（図の主役・構成・成果）は変えない
- Markdownにはテキスト作図指示を**必ず残す**（PowerPoint仕上げ作業者の参考）
- HTMLのshape_19にはSVGを埋め込む（テキストは除く）

### SVG埋め込みルール

section要素のstyleに `padding:0;white-space:normal;` を追加し、SVGを直接子要素として置く。

```html
<section class="... shape_19"
  style="...既存スタイル...;padding:0;white-space:normal;">
  <svg xmlns="http://www.w3.org/2000/svg"
       viewBox="0 0 {W} {H}"
       preserveAspectRatio="xMidYMid meet"
       style="display:block;width:100%;height:100%;
              font-family:'Noto Sans JP','Yu Gothic',sans-serif;">
    <defs><!-- 矢印マーカー等 --></defs>
    ...
  </svg>
</section>
```

### viewBoxの計算

shape_19のwidthパーセンテージとheightパーセンテージ、およびキャンバスのアスペクト比から逆算する。

```
canvas_ratio = template の aspect-ratio 値（例: 6858000/9701213）
shape_ratio  = (shape_width% / shape_height%) × canvas_ratio
W = 900（固定基準）
H = round(W / shape_ratio)
→ viewBox="0 0 {W} {H}"
```

### 図タイプ別SVG骨格（例示、論文内容に応じて選択）

| 対話で選んだ構成 | SVGの方針 |
|---|---|
| 左右比較型 | 等幅カラムを横並び、各カラムに矩形＋矢印 |
| 中央ループ型 | 中央ループ＋周辺要素への双方向矢印 |
| 上から下プロセス型 | 縦フロー＋段階ごとの矩形 |
| 中央システム＋周辺型 | 中央ハブ＋衛星配置 |

成果バナーは図の下部に暗色背景の帯として配置し、3点以内の数値成果を記載する。

---

## ② HTML生成 — フォント設定・タイトルサイズルール

### フォント設定（`<head>`に必ず追加）

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
```

```css
body {
  font-family: "Noto Sans JP", "Yu Gothic", "Hiragino Kaku Gothic ProN",
               "Meiryo", "WenQuanYi Zen Hei", "IPAPGothic", sans-serif;
}
```

フォールバック順は変えない。ヘッドレスChrome環境ではIPAPGothicが一部の日本語字形を誤描画するため、Noto Sans JPを先頭にする必要がある。

### タイトルのオーバーフロー対策

shape_02にテキストを入れた後、以下を確認する。

1. コンテナの実高さ（`height%` × キャンバス高さ）を計算する
2. 行数 × font-size実寸 × line-height ≤ コンテナ実高さ になるか確認する
3. はみ出る場合は `clamp` の最大値を下げるか、`<br>` で行を分割して調整する

---

## ③ Markdown保存 — テキスト作図指示の保持ルール

追加ルール：
- 概要ビジュアル指示のテキスト（PowerPoint作図指示）はMarkdownに**必ず残す**
- HTMLにSVGを埋め込んだ場合でも、Markdownのテキスト指示は削除しない
- 最終的なパワポ仕上げは人間が行う前提のため、SVGはHTML確認用プレビューに留まる

---

## ④ 完了前チェック — Playwright確認ステップ

HTML生成後、以下の手順で視覚確認を行う。

1. 出力ディレクトリで `python3 -m http.server 8765` を起動する
2. Playwrightで `http://localhost:8765/preview.html` にナビゲートする
3. 全体スクリーンショットと shape_19 の拡大スクリーンショットを撮る
4. 確認項目：
   - 日本語の文字化けがない
   - 主要セクション（タイトル・箇条書き）がコンテナからはみ出ていない
   - shape_19のSVGが描画されている
   - 空のshapeがない
5. 問題があれば修正してから再確認する
6. 確認後はサーバーを終了する
7. スクリーンショットは `outputs/posters/<slug>/` に保存する
