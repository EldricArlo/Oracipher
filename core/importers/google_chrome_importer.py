# core/importers/google_chrome_importer.py

import csv
import io
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# 定义此导入器能识别的CSV表头 (小写)
EXPECTED_HEADER = ["name", "url", "username", "password"]


def parse(file_content: str) -> List[Dict[str, Any]]:
    """
    解析从谷歌密码/Chrome导出的CSV文件内容。
    """
    logger.info("Attempting to parse file using Google Chrome importer...")
    imported_entries: List[Dict[str, Any]] = []

    try:
        f = io.StringIO(file_content)
        reader = csv.DictReader(f)

        # 验证表头是否符合预期
        if (
            not reader.fieldnames
            or [h.lower().strip() for h in reader.fieldnames] != EXPECTED_HEADER
        ):
            raise ValueError("CSV header does not match Google Chrome format.")

        for row in reader:
            name = row.get("name", "").strip()
            if not name:
                continue

            entry: Dict[str, Any] = {
                "name": name,
                "category": "",  # 谷歌导出文件没有分类信息
                "details": {
                    "username": row.get("username", "").strip(),
                    "password": row.get("password", ""),
                    "url": row.get("url", "").strip(),
                    "notes": "",  # 谷歌导出文件没有备注信息
                    "icon_data": None,
                    "totp_secret": None,
                    "backup_codes": "",
                },
            }
            imported_entries.append(entry)

        logger.info(
            f"Successfully parsed {len(imported_entries)} entries with Google Chrome importer."
        )
        return imported_entries

    except Exception as e:
        logger.error(f"Failed to parse with Google Chrome importer: {e}", exc_info=True)
        raise
