# Mazda Connect v2 Gracenote 更新チェッカー

マツダ公式ウェブサイト（[Mazda Connect v2 ページ](https://www.mazda.co.jp/owner_support/mazda-connect/v2/)）で公開されている Gracenote メディアデータベース更新ファイル（`.mcg`）のリンクおよびバージョン番号を定期チェックし、更新があった際に **Discord** へ自動通知するシステムです。

検知した新バージョン情報は `state.json` に保存され、自動コミット機能によりノーメンテナンスで次回の監視基準へと自律更新されます。

---

## 主な機能

- **更新自動検知**: Mazda Connect v2 ページを自動解析し、`Gracenote_[バージョン]_JP.mcg` の更新を検知
- **Discord 通知**: 新旧バージョン・ファイル名・ダウンロードURLをリッチな Embed メッセージで通知
- **ノーメンテナンス運用**: 検知した最新情報を `state.json` に保存
- **GitHub Actions 自動化**: 1日1回の定時実行と、`state.json` の自動 Push に対応

---

## セットアップ & ローカルでのテスト

### 1. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定 (ローカルテスト用)
`.env` ファイルを作成し、Discord Webhook URL を登録します。
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

### 3. 動作確認コマンド

#### 現在のページ情報の取得確認 (Dry-run)
```bash
python check_gracenote.py --dry-run
```

#### 通常実行 (更新有無のチェック)
```bash
python check_gracenote.py
```

#### テスト通知の送信 (`state.json` の状態に関わらず Discord 通知を送る)
```bash
python check_gracenote.py --force-notify
```

---

## GitHub Actions での自動化手順

`.github/workflows/` へのファイル配置制限に対応するため、ワークフロー定義テンプレートは `templates/check_update.yml` に配置されています。

1. **ワークフローファイルの配置**:
   `templates/check_update.yml` を `.github/workflows/check_update.yml` としてコミット・配置してください。

2. **GitHub Secrets の設定**:
   リポジトリの `Settings` -> `Secrets and variables` -> `Actions` に移動し、`Repository secret` を追加します。
   - **Name**: `DISCORD_WEBHOOK_URL`
   - **Secret**: ご自身の Discord Webhook URL

3. **リポジトリ設定 (自動 Push 許可)**:
   `Settings` -> `Actions` -> `General` -> `Workflow permissions` にて **Read and write permissions** にチェックを入れ保存してください。

---

## ファイル構成

- `check_gracenote.py`: メイン監視スクリプト
- `notifier.py`: Discord Webhook 送信処理
- `config.py`: 設定ファイル
- `state.json`: 現在の Gracenote バージョン情報保持用ファイル
- `templates/check_update.yml`: GitHub Actions 用ワークフロー定義
