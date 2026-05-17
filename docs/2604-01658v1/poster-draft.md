# ポスター草案: CORAL

## 入力

- PDF: data/paper/2604.01658v1.pdf
- HTMLテンプレート: templates/html/research-template/preview.html
- 出力HTML: outputs/posters/2604-01658v1/preview.html

## 確定内容

### 研究タイトル（shape_02）

CORAL 固定探索を超える自律マルチエージェント進化

### 英語タイトルまたはサブタイトル（shape_03）

CORAL: Beyond Fixed Heuristics with Autonomous Multi-Agent Evolution

### 概要リード（shape_06）

既存の LLM 進化探索は固定ヒューリスティクス依存が強く、長期探索で自律性が制限される。CORAL は共有永続メモリと非同期マルチエージェント実行により、開放型発見の探索効率を大幅に高める。11タスクでベースラインを上回り、主要タスクで新SOTAを達成した。

### 対応する課題（shape_10）

課題①：Open-ended課題では一発生成で最適解に到達しにくい
課題②：固定進化探索は評価コストが膨らみやすく改善効率が低い
課題③：探索の有望知見が個別試行に閉じ、組織的な知識資産化が進まない

### 提供する価値（shape_14）

価値①：探索判断をエージェントへ委譲し、固定ルール依存を低減
価値②：改善率を3〜10倍へ向上し、評価回数を削減
価値③：4エージェント協調で1103 cyclesを達成し、従来記録を更新

### 概要ビジュアル指示（shape_19）

【PowerPoint作図指示】中央システム＋周辺要素型（固定探索 vs CORAL自律進化）

中央に「CORAL Autonomous Evolution Engine」を配置し、内部に Shared Persistent Memory・Heartbeat Intervention・Async Multi-Agent Scheduler の3要素を並列配置する。

左上に「固定探索」を置き、固定ルール主導・単一ループ・知識再利用が弱い点を小ボックスで示し、中央へ破線矢印で比較導線を引く。

右上に「自律進化」を置き、Agent decides what to retrieve/propose/evaluate/update を4ステップで示し、中央へ実線矢印を接続する。

下部左右に4エージェントの並列探索ノードを配置し、中央メモリと双方向矢印で接続して attempts/notes/skills の共有を明示する。

右下に成果注釈として「3〜10x higher improvement rate」「Far fewer evaluations」を配置し、比較結果がどこから生まれるかを中央要素へ矢印で紐付ける。

図下部に暗色バナーを敷き、「Autonomy shift from fixed heuristics to agent-driven evolution」を短文で記載する。

### 適用分野・事業機会（shape_23）

分野①：GPUカーネル・コンパイラ最適化への適用
分野②：物流・スケジューリング等の反復最適化業務
分野③：AI研究開発の自動化（実験設計・探索ループ）

### 現況と予定（shape_27）

現況①：arXiv公開済み（2604.01658）・コード公開済み
予定①：社内タスクへの試行適用（性能最適化・探索業務）を設計
予定②：小規模モデル対応と評価設計の自動化を継続研究

### 討論事項（shape_31）

討論①：自律マルチエージェント進化を、どの社内探索業務へ優先適用すべきでしょうか？
討論②：改善率向上と評価コスト削減のどちらを主KPIに置くべきでしょうか？

### フッター

- 代表発表者（shape_33）：X（X部署）
- 連携部署（shape_34）：連携先調整中
- 略語（shape_35）：LLM：大規模言語モデル　SOTA：最高性能記録　GPU：Graphics Processing Unit

## HTML差し込み対応

| shape | セクション |
| --- | --- |
| shape_02 | 研究タイトル |
| shape_03 | 英語タイトルまたはサブタイトル |
| shape_06 | 概要リード |
| shape_10 | 対応する課題 |
| shape_14 | 提供する価値 |
| shape_19 | 概要ビジュアル指示 |
| shape_23 | 適用分野・事業機会 |
| shape_27 | 現況と予定 |
| shape_31 | 討論事項 |
| shape_33 | 代表発表者 |
| shape_34 | 連携部署 |
| shape_35 | 略語 |
