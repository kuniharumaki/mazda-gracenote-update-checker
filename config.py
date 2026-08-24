import os
from pathlib import Path
from dotenv import load_dotenv

# .env ファイルの読み込み（ローカル実行時用）
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# 監視対象URL
TARGET_URL = "https://www.mazda.co.jp/owner_support/mazda-connect/v2/"

# 状態保持ファイル
STATE_FILE = BASE_DIR / "state.json"

# チェック履歴ファイル
HISTORY_FILE = BASE_DIR / "HISTORY.md"

# Discord Webhook URL
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

# リクエストヘッダー (User-Agent)
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
