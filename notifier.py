import logging
import requests
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def send_discord_notification(
    webhook_url: str,
    old_info: Optional[Dict[str, Any]],
    new_info: Dict[str, Any]
) -> bool:
    """
    Discord Webhook へ Gracenote 更新検出通知を送信する
    """
    if not webhook_url:
        logger.warning("Discord Webhook URL が設定されていません。通知をスキップします。")
        return False

    old_version = old_info.get("version", "不明") if old_info else "初検知"
    new_version = new_info.get("version", "不明")
    download_url = new_info.get("url", "")
    filename = new_info.get("filename", "")
    checked_at = new_info.get("last_updated", "")

    embed = {
        "title": "🚗 Mazda Connect v2 Gracenote 新バージョン公開！",
        "description": "Mazda Connect v2 ページにて新しい Gracenote メディアデータベースが更新されました。",
        "url": "https://www.mazda.co.jp/owner_support/mazda-connect/v2/",
        "color": 15073298,  # マツダレッド風 (#E60012)
        "fields": [
            {
                "name": "旧バージョン",
                "value": f"`{old_version}`",
                "inline": True
            },
            {
                "name": "新バージョン",
                "value": f"**`{new_version}`**",
                "inline": True
            },
            {
                "name": "ファイル名",
                "value": f"`{filename}`",
                "inline": False
            },
            {
                "name": "ダウンロードリンク",
                "value": f"[ファイルダウンロード ({filename})]({download_url})",
                "inline": False
            },
            {
                "name": "検知日時",
                "value": checked_at,
                "inline": False
            }
        ],
        "footer": {
            "text": "Mazda Gracenote Update Checker"
        }
    }

    payload = {
        "username": "Mazda Gracenote Checker",
        "avatar_url": "https://www.mazda.co.jp/favicon.ico",
        "embeds": [embed]
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Discord への通知送信が成功しました。")
        return True
    except Exception as e:
        logger.error(f"Discord への通知送信に失敗しました: {e}")
        return False
