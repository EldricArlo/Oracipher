# core/database_migration.py

import os
import sqlite3
import logging

logger = logging.getLogger(__name__)


def check_and_migrate_schema(db_path: str) -> None:
    """
    检查数据库文件是否存在旧的、不兼容的架构。
    如果检测到旧架构，会备份旧数据库并允许程序创建一个新的空数据库。
    """
    if not os.path.exists(db_path):
        return

    try:
        conn_check = sqlite3.connect(db_path)
        cursor_check = conn_check.cursor()
        # 检查 'entries' 表的创建SQL语句
        cursor_check.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='entries'"
        )
        result = cursor_check.fetchone()
        conn_check.close()

        if result:
            create_sql = result[0]
            # 旧架构的特征是在 'name' 字段上有 UNIQUE 约束
            if "UNIQUE" in create_sql.upper():
                backup_path = db_path + ".backup_old_schema"
                logger.warning(
                    "Old database schema detected (with UNIQUE constraint on entries.name)."
                )
                logger.warning(f"Backing up old database to: {backup_path}")
                os.rename(db_path, backup_path)
                logger.warning(
                    "Backup complete. A new, compatible database will be created."
                )
    except Exception as e:
        logger.error(f"Error while checking database schema: {e}", exc_info=True)
