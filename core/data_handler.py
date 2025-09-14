# core/data_handler.py

import csv
import io
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DataHandler:
    """
    负责处理数据的导入和导出，主要是与CSV格式的转换。
    """
    
    CSV_FIELDNAMES: List[str] = [
        'name', 'username', 'password', 'url', 'notes', 'category'
    ]

    @staticmethod
    def export_to_csv(entries: List[Dict[str, Any]]) -> str:
        """
        将条目数据列表转换为CSV格式的字符串。
        """
        logger.info(f"准备导出 {len(entries)} 个条目到 CSV...")
        try:
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=DataHandler.CSV_FIELDNAMES)
            writer.writeheader()
            for entry in entries:
                details = entry.get('details', {})
                row = {
                    'name': entry.get('name', ''),
                    'username': details.get('username', ''),
                    'password': details.get('password', ''),
                    'url': details.get('url', ''),
                    'notes': details.get('notes', ''),
                    'category': entry.get('category', '')
                }
                writer.writerow(row)
            logger.info("CSV 内容已在内存中成功生成。")
            return output.getvalue()
        except Exception as e:
            logger.error(f"导出到CSV时发生错误: {e}", exc_info=True)
            raise

    @staticmethod
    def import_from_csv(file_path: str) -> List[Dict[str, Any]]:
        """
        从CSV文件路径读取数据，并将其解析为应用程序内部格式的条目列表。
        """
        logger.info(f"准备从 CSV 文件导入: {file_path}")
        imported_entries: List[Dict[str, Any]] = []
        try:
            with open(file_path, mode='r', encoding='utf-8', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                if 'name' not in (reader.fieldnames or []):
                    raise ValueError("导入失败：CSV文件必须包含 'name' 列。")
                for row in reader:
                    if not row.get('name'):
                        logger.warning(f"跳过CSV中的一行，因为'name'字段为空。行内容: {row}")
                        continue
                    entry: Dict[str, Any] = {
                        "name": row.get('name', '').strip(),
                        "category": row.get('category', '').strip(),
                        "details": {
                            "username": row.get('username', '').strip(),
                            "password": row.get('password', ''),
                            "url": row.get('url', '').strip(),
                            "notes": row.get('notes', '').strip(),
                            "icon_data": None 
                        }
                    }
                    imported_entries.append(entry)
            logger.info(f"成功从CSV文件解析了 {len(imported_entries)} 个条目。")
            return imported_entries
        except FileNotFoundError:
            logger.error(f"导入失败：找不到文件 {file_path}")
            raise
        except Exception as e:
            logger.error(f"导入CSV时发生错误: {e}", exc_info=True)
            raise