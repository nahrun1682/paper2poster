---
tags: [lab, agent, poster, skill, langgraph, deep-agent, mermaid]
created: 2026-05-15
status: 設計中
---

# 🎨 討論会用ポスター生成エージェント

> 研究報告書（PDF）から社内討論会用ポスター草案をHTMLで生成するエージェント。人間がパワポで仕上げることを前提とした「草案サポーター」。

## 📋 TL;DR

- **インプット**：研究報告書PDF
- **アウトプット**：討論会用HTMLポスター草案（mermaid図入り）
- **使い方**：VSCodeでSKILL.md（Claude Code / Codex）、またはお試しチャットUI（LangGraph Deep Agent）
- **スコープ**：完成品ではなく「草案」。最終仕上げは人間がパワポで行う

---

## 🗺 全体設計

```
【本番】
Claude Code / Codex + SKILL.md
└ VSCodeでローカル動作
  PDFはファイルシステムから直接読み込み

【お試しUI】
LangGraph Deep Agent
└ SKILL.mdをシステムプロンプトに流用
  PDFアップロードはWebUI経由
  本番と完全一致しなくてOK（お試し割り切り）
```

---

## 🔄 エージェントのワークフロー

```
① PDF投入
   └ 自動で要約 ＋ 3パターンの切り口を提示

② ユーザーがテキストで選択・調整
   例：「Bで、ただし手法の部分は省いて」
   例：「Aベースで結論も入れて」

③ Claudeが構造化JSON生成
   └ 足りない情報は「ここ追記できますか？」と聞く

④ mermaid図の生成（シンプル限定）
   └ ノード数10以内、3種類から選択

⑤ HTMLテンプレートに差し込んでポスター出力
```

### ポスターの切り口パターン（案）

| パターン | 前面に出すもの | 向いているケース |
|---------|-------------|----------------|
| A) 課題提起型 | 「なぜこれが問題か」 | 問題認識を共有したいとき |
| B) 結果訴求型 | 「何がわかったか」 | 成果を伝えたいとき |
| C) 提言型 | 「何をすべきか」 | アクションを促したいとき |

---

## 🧩 SKILL.mdの構成（予定）

```
SKILL.md
├── WORKFLOW       ← ①〜⑤の手順
├── EXTRACTION_RULES  ← 報告書から何をどう抜くか
└── POSTER_FIELDS     ← テンプレートのプレースホルダー定義
```

`POSTER_FIELDS`はHTMLテンプレートのプレースホルダーと1対1対応させる。

---

## 🖼 mermaid図の方針

シンプル限定（ノード数10以内）：

```
flowchart型  → 研究プロセス・手順系
graph型      → 関係性・因果系
quadrant型   → 比較・マッピング系
```

- 複雑な図は作らない（崩れるため）
- あくまで草案。細部は人間がパワポで仕上げる
- SKILL.mdに「シンプルに絞る」制約を明記する

---

## 🔧 技術スタック

### テンプレート生成
- **frontend-slides**スキル（PPTX→HTML変換）
  - `npx claudepluginhub burgebj/claude_everything`
  - `/frontend-slides`コマンドで起動
  - `python-pptx`でPPTXからレイアウト・色・フォントを抽出

### 参考リポジトリ
- **posterskill**（ethanweber/posterskill）
  - https://github.com/ethanweber/posterskill
  - ⭐142、フォーク15
  - ブラウザが編集UIになる単一HTMLファイル
  - Overleaf（LaTeX）前提なのでそのままは使えない
  - **思想・HTMLエディタ構造を参考にする**
  - 入力をPDFに差し替えるカスタマイズが必要
- **pptx-postersスキル**
  - HTML/CSS → PDF/PPTX変換まで対応

### お試しUI
- **LangGraph Deep Agent**
  - `uv add deepagents`
  - SKILL.mdをシステムプロンプトに流用
  - メモリ：`InMemorySaver` + `InMemoryStore`（DBなし、セッション内のみ）

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

agent = create_deep_agent(
    skills=["./skills/poster-generator"],
    checkpointer=InMemorySaver(),
    store=InMemoryStore(),
    system_prompt="社内討論会ポスター生成エージェント"
)
```

---

## 📂 インプット形式

- **メイン**：PDF（研究報告書）
- 報告書のフォーマットは大体決まっている → 抽出精度が上がる
- 将来的に複数PDFや他形式も受け付けられるようにしたい

---

## ⚠️ 未確定事項（休み明けに確認）

- [ ] **ポスターのセクション構成**（テンプレートPPTXから確認）
  - セクションが固まったらPOSTER_FIELDSを定義できる
  - HTMLプレースホルダーとの1対1対応を設計する

---

## 🚀 優先順位・ToDoリスト

```
① セクション確認（休み明け）← ここが最優先
② テンプレートHTML + プレースホルダー定義
③ SKILL.md作成（WORKFLOW / EXTRACTION_RULES / POSTER_FIELDS）
④ frontend-slidesでPPTX→HTML変換を試す
⑤ posterskillをcloneして感触を掴む
⑥ お試しDeep Agentはその後
```

---

## 💡 設計メモ・判断ログ

### なぜパワポ直接生成でなくHTML草案か
- パワポをLLMに直接作らせるのはハード（レイアウト崩れやすい）
- HTML→ブラウザプレビュー→人間がパワポで仕上げる方が現実的
- 「完成品」ではなく「草案で作業を10分の1にする」がスコープ

### なぜDeep Agentをお試しUIに選んだか
- SKILL.md形式をネイティブサポートしている
- 本番（Claude Code/Codex）とSKILL.mdを共有できる
- メモリ・サブエージェント・ファイル操作が最初から入っている
- DB不要（InMemory実装がある）

### mermaidをシンプルに限定する理由
- 複雑な図はレイアウトが崩れやすい
- 最終仕上げは人間がパワポでやる前提
- 「草案が出力されること」が目的であり、図の完成度は問わない

### MCPについて
- posterskillはSKILL.mdのみ（MCPなし）→ Codexでもそのまま使える
- SKILLさえ書ければエージェントフレームワーク側で動く設計

---

## 📚 参考リンク

- [posterskill GitHub](https://github.com/ethanweber/posterskill)
- [pptx-posters skill](https://mcpmarket.com/tools/skills/pptx-research-posters-2)
- [frontend-slides skill](https://github.com/zarazhangrui/frontend-slides)
- [Deep Agents docs](https://docs.langchain.com/oss/python/deepagents/overview)
- [LangGraph Deep Agent skills](https://docs.langchain.com/oss/python/deepagents/skills)

---
