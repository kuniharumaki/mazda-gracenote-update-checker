import json
import logging
import re
import sys
import argparse
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup

from config import TARGET_URL, STATE_FILE, DISCORD_WEBHOOK_URL, HTTP_HEADERS
from notifier import send_discord_notification, send_discord_error_notification

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 日本標準時 JST (UTC+9)
JST = timezone(timedelta(hours=9))


def fetch_gracenote_info() -> dict:
    """
    Mazda Connect v2 ページを取得し、Gracenote のダウンロードURLとバージョン情報を抽出する
    """
    logger.info(f"ページを取得中: {TARGET_URL}")
    response = requests.get(TARGET_URL, headers=HTTP_HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # 1. mcg 拡張子を含むリンクタグを探す
    mcg_link = None
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if ".mcg" in href:
            mcg_link = href
            break

    # 2. 見つからない場合は全体のテキスト/HTMLから正規表現で検索
    if not mcg_link:
        match = re.search(r'https?://[^\s"\'<>]+Gracenote_[0-9\.]+_JP\.mcg[^\s"\'<>]*', response.text)
        if match:
            mcg_link = match.group(0)

    if not mcg_link:
        raise ValueError("Gracenote 更新ファイル (.mcg) のダウンロードリンクが見つかりませんでした。")

    # クエリパラメータを除去したベースURLを作成
    clean_url = mcg_link.split("?")[0]
    filename = clean_url.split("/")[-1]

    # バージョン番号の抽出 (例: Gracenote_1.1.1.03656_JP.mcg -> 1.1.1.03656)
    version_match = re.search(r"Gracenote_([0-9\.]+)_JP\.mcg", filename)
    version = version_match.group(1) if version_match else "unknown"

    now_jst = datetime.now(JST).isoformat()

    return {
        "version": version,
        "url": clean_url,
        "filename": filename,
        "last_updated": now_jst
    }

def load_state() -> dict:
    """保存済みの状態を読み込む"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"state.json の読み込みに失敗しました: {e}")
    return {}

def save_state(state: dict) -> None:
    """状態を state.json に保存する"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    logger.info(f"state.json を更新しました: バージョン {state.get('version')}")

def main():
    parser = argparse.ArgumentParser(description="Mazda Connect v2 Gracenote 更新チェッカー")
    parser.add_argument("--force-notify", action="store_true", help="バージョン変更有無に関わらずテスト通知を送信する")
    parser.add_argument("--dry-run", action="store_true", help="取得のみ行い、状態更新や通知は行わない")
    args = parser.parse_args()

    try:
        current_info = fetch_gracenote_info()
        logger.info(f"最新取得結果: バージョン={current_info['version']}, ファイル名={current_info['filename']}")
        logger.info(f"URL: {current_info['url']}")
    except Exception as e:
        error_msg = str(e)
        now_jst = datetime.now(JST).isoformat()
        logger.error(f"Gracenote 情報の取得に失敗しました: {error_msg}")
        send_discord_error_notification(DISCORD_WEBHOOK_URL, error_msg, now_jst)
        sys.exit(1)


    if args.dry_run:
        logger.info("Dry-run モードのため終了します。")
        return

    saved_state = load_state()
    saved_version = saved_state.get("version")
    saved_url = saved_state.get("url")
    logger.info(f"保存済み状態 (state.json): バージョン={saved_version}, URL={saved_url}")

    is_updated = (
        current_info["version"] != saved_version or
        current_info["url"] != saved_url
    )


    if is_updated or args.force_notify:

        if is_updated:
            logger.info(f"🎉 新しいバージョンを検知しました！ (旧: {saved_version} -> 新: {current_info['version']})")
        else:
            logger.info("強制通知モード (--force-notify) で実行しています。")

        # Discord 通知送信
        send_discord_notification(DISCORD_WEBHOOK_URL, saved_state, current_info)

        # 状態保存 (最新情報で上書き)
        save_state(current_info)
    else:
        logger.info(f"更新はありませんでした。（現在のバージョン: {saved_version}）")

if __name__ == "__main__":
    main()
