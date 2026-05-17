# paper2poster

研究報告書や論文のPDFを入力に、社内討論会向けポスターの草案を作るためのリポジトリ。
このプロジェクトの出力は完成版ではなく草案であり、最終仕上げはPowerPointで人が行う前提。

主な役割は次の2つ。

- 内容設計: paper-to-poster-drafter スキルで、セクションを対話で確定
- レイアウト変換: poster-layout-extractor スキルで、PPTXレイアウトをHTMLへ変換

対象環境は VS Code 上の Codex、GitHub Copilot Chat、Claude 系ワークフロー。

## クイックスタート

clone 直後に次の手順を実行する。

    uv sync
    uv run playwright install chromium

上記が完了していれば、Playwright視覚確認を含むポスター生成フローを再現できる。

VS Code のエージェントチャットで、次のように依頼するとポスター作成フェーズを開始できる。

    paper-to-poster-drafterスキルを使ってdata/paperにある研究報告書からポスター作成フェーズを開始して

## 何ができるか

paper-to-poster-drafter でできること。

- PDF内容をもとに、ポスターの各セクション文案を選択肢形式で確定
- 既存HTMLテンプレートへ確定文言を差し込み
- 概要領域にインラインSVGを埋め込み、プレビュー可能な状態を作成
- Markdown草案とHTML草案を同時に出力

poster-layout-extractor でできること。

- 単一スライドのPPTXポスターから、配置と見た目を再現したHTMLテンプレートを生成

## 標準入出力

paper-to-poster-drafter の標準パス。

- 入力PDF: data/paper/<paper>.pdf
- 入力テンプレート: templates/html/research-template/preview.html
- 出力Markdown: docs/<slug>/poster-draft.md
- 出力HTML: outputs/posters/<slug>/preview.html

必要に応じて、追加観点ファイルを使って候補生成の方向づけを上書きできる。
各ハーネスでは、自分のスキルフォルダ配下にある additional-considerations.md を読む。

## 再現運用の前提

このリポジトリでは、環境セットアップとスキル実行を分離している。

- 環境構築はREADMEで一元管理
- スキルは内容設計と変換フローに集中

ただし配布性のため、paper-to-poster-drafter 側にも最小限の環境前提は記載している。

## 推奨ワークフロー

1. テンプレートが未整備なら、poster-layout-extractor でHTMLテンプレートを作る
2. paper-to-poster-drafter でセクションを順に確定する
3. outputs/posters/<slug>/preview.html を生成し、視覚確認する
4. docs/<slug>/poster-draft.md をレビューしてPowerPoint仕上げに渡す

## 依存関係

Python依存は pyproject.toml で管理する。
ブラウザ実体は Playwright の install コマンドで取得する。

## 既知の運用ポイント

- 初回セットアップで playwright install を省略すると、視覚確認時にブラウザ実体不足で失敗する
- outputs は生成物置き場。テンプレート本体は templates 側を直接編集しない
- 既存出力を更新する場合はバックアップを残す

## 参考資料

- README_参考.md は初期検討メモ
- 実運用の正本はこの README
