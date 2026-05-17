---
name: paper-to-poster-drafter
description: Use when 研究論文・研究報告書PDFをもとに、社内討論会向けポスターの各セクション内容をユーザーと対話で決め、既存HTMLテンプレートへ反映する必要があるとき。
---

# 研究報告書からポスター草案を作る

## 目的

研究論文または研究報告書PDFを読み、ユーザーと選択肢形式で内容を固め、社内討論会向けポスター草案を作る。既存のHTMLテンプレートはレイアウトとして使い、そこに入っている文章は例文として扱う。

このスキルはレイアウト抽出ではなく、内容設計とHTML差し込みを担当する。PPTXからHTMLテンプレートを作る場合は `poster-layout-extractor` を使う。

## 入力

標準の入力:
- 研究報告書PDF: `data/paper/<paper>.pdf`
- HTMLテンプレート: `templates/html/research-template/preview.html`

任意の追加入力:
- 追加観点ファイル: `.claude/skills/paper-to-poster-drafter/additional-considerations.md`

環境前提（配布向け）:
- clone 直後に `uv sync` を実行し、Python依存をそろえる。
- Playwright視覚確認の前に `uv run playwright install chromium` を1回実行する。
- このスキルの内容設計・HTML差し込みフローは、上記セットアップ完了を前提とする。

PDFはarXiv論文のような研究論文に限らない。社内報告書、技術調査レポート、実証報告書、PoC報告書でもよい。論文なら課題、提案手法、実験結果、限界を拾う。報告書なら背景、現状、提案、検証結果、今後の予定を拾う。

`preview.html` の既存文言はサンプルであり、研究内容に合わせて自由に置き換える。既存の例文の要素や表現に従いすぎない。

ただし、各セクションの箇条書き数はテンプレート内の例文に合わせる。例文の中身は参考程度にし、個数と文量感だけを守る。

## 出力

標準の出力:
- 確定内容Markdown: `docs/<slug>/poster-draft.md`
- 生成済みポスターHTML: `outputs/posters/<slug>/preview.html`

`templates/` はテンプレート置き場であり、完成物の出力先にしない。HTMLへ反映するときは、テンプレートを `outputs/posters/<slug>/preview.html` にコピーしてから、そのコピーを更新する。

## 対話ルール

- セッション開始時に、`.claude/skills/paper-to-poster-drafter/additional-considerations.md` が存在すれば必ず読む。
- 追加観点ファイルの `全体` は全セクションに適用する。
- 追加観点ファイルに各セクション名（例: `研究タイトル`、`概要リード`）の見出しがあれば、そのセクション候補作成時に反映する。
- 追加観点は「候補文の方向づけ」に使い、出力Markdownへ「追加観点ファイルの本文」をそのまま転載しない。
- 追加観点ファイルの該当見出しが空なら、通常ルールのみで進行する。

- テンプレート順に、1セクションずつ確定する。
- 各セクションではPDFから候補を2〜3個出し、ユーザーに選ばせる。
- 各候補には、1文で「この候補の狙い」を添える。
- 候補を出したら、推奨案を1つ明示し、理由を1文で説明する。
- 候補が合わない場合は、ユーザーが普通のチャットで自由回答してよい。
- PDFから情報が足りない場合は、不足しているセクションだけ質問する。
- 候補や選択履歴は最終Markdownに残さない。保存するのは完成内容だけ。
- 各候補はPowerPointに載せる前提で簡潔に書く。説明文ではなく、ポスター上で一目で読める短い文にする。
- 箇条書きセクションは、テンプレート例と同じ個数を維持する。例が3項目なら3項目、例が2項目なら2項目にする。
- ただし、`概要ビジュアル指示` は大きい領域なので例外とし、テンプレート例の行数へ無理に圧縮しない。

## セクション順

1. 研究タイトル
2. 英語タイトルまたはサブタイトル
3. 概要リード
4. 対応する課題
5. 提供する価値
6. 概要ビジュアル指示
7. 適用分野・事業機会
8. 現況と予定
9. 討論事項
10. フッター情報

## 概要ビジュアル指示

最終的なビジュアルは人間がPowerPointで作る前提にする。ただしHTMLプレビュー用にインラインSVGを生成してshape_19に埋め込む。テキスト作図指示はMarkdownに必ず残す。

ここはポスター中央の大きな情報領域として扱う。通常セクションより深く対話し、PowerPoint作業者が図に起こせる作図指示を残す。テンプレート例の行数には縛られず、4〜8行程度まで許容する。ただし長文の本文説明ではなく、図の構成指示として書く。

概要は次の3段階で決める:

1. 図の主役を選ぶ。
   - 例: 提案手法の仕組み、従来方式との比較、検証結果の流れ、業務適用プロセス、意思決定の全体像。
2. 図の構成を選ぶ。
   - 例: 中央ループ型、左右比較型、上から下へのプロセス型、中央システム + 周辺要素型、左に課題・中央に解決策・右に効果を置く型。
3. 強調する根拠や成果を選ぶ。
   - 論文なら、主要実験結果、改善率、比較対象、アブレーション、代表タスクを入れる。
   - 報告書なら、検証結果、現場課題、導入効果、コスト・期間・リスク、今後の予定を入れる。

作図指示には、可能な範囲で次を含める:
- 図の中心に置く概念やプロセス。
- 入力、処理、出力、関係者、システム構成などの主要要素。
- 比較対象や従来方式との差分。
- 根拠となる数値、結果、観察事項。
- 右側または下部に添える成果・示唆・討論につながる論点。

### SVG生成

対話で決めた構成をもとに、shape_19にインラインSVGを埋め込む。section要素のstyleに `padding:0;white-space:normal;` を追加する。

SVGの基本構造:

```html
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {W} {H}"
     preserveAspectRatio="xMidYMid meet"
     style="display:block;width:100%;height:100%;
            font-family:'Noto Sans JP','Yu Gothic',sans-serif;">
  <defs><!-- 矢印マーカー等 --></defs>
  ...
</svg>
```

viewBoxの計算: テンプレートのshape_19のwidthパーセンテージとheightパーセンテージ、およびキャンバスのaspect-ratio値から算出する。

```
canvas_ratio = aspect-ratio の幅 ÷ 高さ
shape_ratio  = (shape_width% ÷ shape_height%) × canvas_ratio
W = 900（基準値）
H = round(W ÷ shape_ratio)
```

構成タイプ別のSVG方針（例）:

| 構成タイプ | SVGの方針 |
|---|---|
| 左右比較型 | 等幅カラムを横並び、各カラムに矩形＋矢印 |
| 中央ループ型 | 中央ループ＋周辺要素への双方向矢印 |
| 上から下プロセス型 | 縦フロー＋段階ごとの矩形 |
| 中央システム＋周辺型 | 中央ハブ＋衛星配置 |

成果バナーは図下部に暗色背景の帯として配置し、数値成果を3点以内で示す。

## HTML差し込み先

`templates/html/research-template/preview.html` を元テンプレートとして読み、`outputs/posters/<slug>/preview.html` にコピーしたうえで、主に次の要素を置き換える。

| 要素 | 内容 |
| --- | --- |
| `shape_02` | 研究タイトル |
| `shape_03` | 英語タイトルまたはサブタイトル |
| `shape_06` | 概要リード |
| `shape_10` | 対応する課題 |
| `shape_14` | 提供する価値 |
| `shape_19` | 概要ビジュアル指示 |
| `shape_23` | 適用分野・事業機会 |
| `shape_27` | 現況と予定 |
| `shape_31` | 討論事項 |
| `shape_33` | 代表発表者 |
| `shape_34` | 連携部署 |
| `shape_35` | 略語 |

セクション見出しである `shape_09`、`shape_13`、`shape_17`、`shape_22`、`shape_26`、`shape_30` は原則維持する。研究内容に合わせて見出し自体を変える必要がある場合だけ、ユーザーに確認してから変更する。

## Markdown保存

確定内容は `docs/<slug>/poster-draft.md` に保存する。`<slug>` はPDF名または研究テーマから短く作る。例: `docs/2604-01658v1/poster-draft.md`

Markdownには次だけを書く:
- 入力PDF
- 使用したHTMLテンプレート
- 確定した各セクションの文言（概要ビジュアル指示のテキスト作図指示を含む）
- HTML差し込み対応

shape_19にSVGを埋め込んだ場合でも、概要ビジュアル指示のテキスト作図指示はMarkdownから削除しない。SVGはHTML確認用プレビューであり、テキスト指示はPowerPoint作業者の参考資料として残す。

候補案、選択履歴、長いPDF要約は保存しない。

## HTML生成

`templates/html/research-template/preview.html` は直接更新しない。テンプレートを `outputs/posters/<slug>/preview.html` にコピーし、そのコピーを更新する。

`outputs/posters/<slug>/preview.html` がすでに存在する場合は、更新前に同じフォルダへバックアップを作る。初回生成で出力先が存在しない場合、バックアップは不要。

バックアップ名:

```text
outputs/posters/<slug>/preview.backup-YYYYMMDD-HHMMSS.html
```

HTML生成時は次を守る:
- **HTMLファイルは Read ツールで読んでから Edit ツールで直接更新する。中間スクリプト（`generate.py` 等）は作らない。**
- 既存のレイアウト、CSS、スクリプトは維持する。
- 対象 `shape_XX` の中身だけを置き換える。
- 日本語本文の箇条書きは、HTML上では `<br>` 区切りにする。
- 箇条書きの個数は、置き換え前のテンプレート例と同じにする。
- 例外として、概要ビジュアル指示の `shape_19` は大きい領域なので、テンプレート例の行数へ無理に合わせない。
- 各項目はPowerPoint用に短くし、長い説明や論文調の文を詰め込まない。
- 特殊文字はHTMLとして壊れないようにエスケープする。
- `preview copy.html` のような手動コピーがあっても、標準の読み取り元は `templates/html/research-template/preview.html`、標準の書き込み先は `outputs/posters/<slug>/preview.html` とする。

**フォント設定（必須）**

`<head>` に次を追加する。追加しないとヘッドレスChrome環境で日本語が文字化けする。

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
```

`body` の `font-family` を次の順で設定する（順序を変えない）:

```css
font-family: "Noto Sans JP", "Yu Gothic", "Hiragino Kaku Gothic ProN",
             "Meiryo", "WenQuanYi Zen Hei", "IPAPGothic", sans-serif;
```

**タイトルのオーバーフロー対策**

shape_02にテキストを入れた後、コンテナ高さに収まるか確認する。

1. コンテナの実高さ（`height%` × キャンバス高さ）を計算する。
2. 行数 × font-size実寸 × line-height がコンテナ実高さ以下になるか確認する。
3. はみ出る場合は `clamp` の最大値を下げるか、`<br>` で行分割して調整する。

## 完了前チェック

報告前に確認する:

**ファイル確認**
- `docs/<slug>/poster-draft.md` が作成されている。
- `outputs/posters/<slug>/preview.html` が作成されている。
- 既存の出力HTMLを上書きした場合、更新前のバックアップが存在する。
- `templates/html/research-template/preview.html` が直接変更されていない。
- `outputs/posters/<slug>/preview.html` の対象 `shape_XX` が確定文言に置き換わっている。
- 概要以外の箇条書きセクションの項目数が、テンプレート例と同じである。
- 概要ビジュアル指示のテキスト作図指示が `docs/<slug>/poster-draft.md` に残っている。

**Playwright視覚確認（必須）**

1. 出力ディレクトリで `python3 -m http.server 8765` を起動する。
2. Playwrightで `http://localhost:8765/preview.html` にナビゲートする。
3. 全体スクリーンショットと shape_19 の拡大スクリーンショットを撮る。
4. 次を確認する:
   - 日本語の文字化けがない
   - 主要セクション（タイトル・箇条書き）がコンテナからはみ出ていない
   - shape_19のSVGが正しく描画されている
   - 空のshapeがない
5. 問題があれば修正して再確認する。
6. 確認後はサーバーを終了する。
7. スクリーンショットは `outputs/posters/<slug>/` に保存する。

**内容確認**
- 文字量が多すぎて主要セクションが読めなくなっていない。
- ユーザーに、最終的な図の作成とPowerPoint仕上げは人間作業であることが伝わっている。
