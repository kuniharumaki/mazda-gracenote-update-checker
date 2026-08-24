import logging
from pathlib import Path
from typing import Optional

from config import HISTORY_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Markdown テーブルヘッダー
_TABLE_HEADER = (
    "| チェック日時 | ステータス | バージョン | 旧バージョン | ファイル名 | ダウンロードURL | トリガー | Run ID | エラー |\n"
    "|---|---|---|---|---|---|---|---|---|"
)

_FILE_HEADER = "# Gracenote Update Check History\n\n"


def _status_label(status: str) -> str:
    """ステータス文字列を絵文字付きラベルに変換する"""
    labels = {
        "updated": "✅ updated",
        "no_change": "➖ no_change",
        "error": "❌ error",
    }
    return labels.get(status, status)


def _make_row(
    checked_at: str,
    status: str,
    version: str = "-",
    previous_version: str = "-",
    filename: str = "-",
    download_url: str = "",
    trigger: str = "-",
    run_id: str = "-",
    error_message: str = "-",
) -> str:
    """Markdown テーブルの1行を生成する"""
    url_cell = f"[link]({download_url})" if download_url else "-"
    # エラーメッセージ内のパイプ文字をエスケープ
    safe_error = error_message.replace("|", "\\|") if error_message else "-"
    return (
        f"| {checked_at} "
        f"| {_status_label(status)} "
        f"| {version} "
        f"| {previous_version} "
        f"| {filename} "
        f"| {url_cell} "
        f"| {trigger} "
        f"| {run_id} "
        f"| {safe_error} |"
    )


def append_history(
    checked_at: str,
    status: str,
    version: str = "-",
    previous_version: str = "-",
    filename: str = "-",
    download_url: str = "",
    trigger: str = "-",
    run_id: str = "-",
    error_message: str = "-",
) -> None:
    """
    HISTORY.md に1行追記する。
    新しいレコードはテーブルヘッダー直下（最上部）に挿入され、
    最新の結果がすぐ見えるようにする。
    """
    new_row = _make_row(
        checked_at=checked_at,
        status=status,
        version=version,
        previous_version=previous_version,
        filename=filename,
        download_url=download_url,
        trigger=trigger,
        run_id=run_id,
        error_message=error_message,
    )

    history_path: Path = HISTORY_FILE

    if not history_path.exists():
        # ファイルが存在しない場合は新規作成
        content = _FILE_HEADER + _TABLE_HEADER + "\n" + new_row + "\n"
        history_path.write_text(content, encoding="utf-8")
        logger.info("HISTORY.md を新規作成しました。")
    else:
        # 既存ファイルを読み込み、ヘッダー直下に行を挿入
        lines = history_path.read_text(encoding="utf-8").splitlines()

        # テーブル区切り行 (|---|...) の位置を探す
        separator_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("|---"):
                separator_idx = i
                break

        if separator_idx is not None:
            # 区切り行の直後に新しい行を挿入
            lines.insert(separator_idx + 1, new_row)
        else:
            # 区切り行が見つからない場合はファイル末尾に追加
            logger.warning("HISTORY.md のテーブル区切り行が見つかりません。末尾に追記します。")
            lines.append(new_row)

        history_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        logger.info(f"HISTORY.md に履歴を追記しました: status={status}")
