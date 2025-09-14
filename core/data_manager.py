# core/data_manager.py

import os
import sqlite3
import json
import logging
from cryptography.fernet import InvalidToken
from .crypto import CryptoHandler

logger = logging.getLogger(__name__)


class DataManager:
    """
    管理所有针对加密数据库的读写操作。

    此类封装了所有与 SQLite 数据库的交互，确保数据以原子方式、
    安全地存储和检索。它与 CryptoHandler 协作，在写入数据库前加密数据，
    在从数据库读取后解密数据。

    数据库结构:
    - `entries`: 存储非敏感的元数据，如 id, category, name。
                `name` 字段是唯一的。
    - `details`: 存储加密后的敏感数据（用户名、密码、备注等）。
                通过 `entry_id` 与 `entries` 表关联。
    """

    def __init__(self, data_dir: str, crypto_handler: CryptoHandler):
        """
        初始化 DataManager。

        Args:
            data_dir (str): 存放数据库文件的目录。
            crypto_handler (CryptoHandler): 用于加密和解密的实例。
        """
        db_path = os.path.join(data_dir, "safekey.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.crypto = crypto_handler

        self._create_tables()
        logger.info(f"DataManager 初始化成功，已连接到数据库: {db_path}")

    def _create_tables(self):
        """
        创建数据库表（如果它们不存在）。
        启用外键约束以保证数据完整性。
        """
        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL UNIQUE
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS details (
                entry_id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                FOREIGN KEY (entry_id) REFERENCES entries (id) ON DELETE CASCADE
            )
            """
        )
        self.conn.commit()

    def save_entry(self, category: str, name: str, details: dict):
        """
        以原子方式（UPSERT）保存或更新一个条目。

        如果具有相同 `name` 的条目已存在，则更新其 `category` 和 `details`。
        如果不存在，则插入一个新条目。所有操作都在一个事务中完成。

        Args:
            category (str): 条目的分类。
            name (str): 条目的名称（必须唯一）。
            details (dict): 包含敏感信息（如用户名、密码）的字典。
        """
        try:
            data_json = json.dumps(details)
            encrypted_data = self.crypto.encrypt(data_json)

            self.cursor.execute("BEGIN")

            # UPSERT 操作: 插入或更新 entries 表
            self.cursor.execute(
                """
                INSERT INTO entries (category, name) VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET category=excluded.category
                """,
                (category, name),
            )

            # 获取刚插入或已存在的条目的ID
            self.cursor.execute("SELECT id FROM entries WHERE name=?", (name,))
            entry_id = self.cursor.fetchone()[0]

            # UPSERT 操作: 插入或更新 details 表
            self.cursor.execute(
                """
                INSERT INTO details (entry_id, data) VALUES (?, ?)
                ON CONFLICT(entry_id) DO UPDATE SET data=excluded.data
                """,
                (entry_id, encrypted_data),
            )

            self.conn.commit()
            logger.info(f"成功保存条目: '{name}' (ID: {entry_id})")

        except Exception as e:
            logger.error(f"保存条目 '{name}' 时发生数据库错误: {e}", exc_info=True)
            self.conn.rollback()

    def get_entries(self) -> list[dict]:
        """
        检索并解密数据库中的所有条目。

        Returns:
            list[dict]: 一个包含所有条目数据的字典列表。
                        如果某个条目解密失败，它将被跳过并记录错误。
        """
        query = "SELECT e.id, e.category, e.name, d.data FROM entries e JOIN details d ON e.id = d.entry_id"
        self.cursor.execute(query)
        entries = []
        for row in self.cursor.fetchall():
            try:
                decrypted_data_json = self.crypto.decrypt(row[3])
                details = json.loads(decrypted_data_json)
                entries.append(
                    {
                        "id": row[0],
                        "category": row[1],
                        "name": row[2],
                        "details": details,
                    }
                )
            except InvalidToken:
                logger.error(
                    f"无法解密条目 (ID: {row[0]})。可能是密钥不匹配或数据已损坏。"
                )
            except json.JSONDecodeError:
                logger.error(
                    f"无法解析条目 (ID: {row[0]}) 的JSON数据。数据可能已损坏。"
                )
            except Exception as e:
                logger.error(
                    f"加载条目 (ID: {row[0]}) 时发生未知错误: {e}", exc_info=True
                )

        logger.info(f"成功加载并解密 {len(entries)} 个条目。")
        return entries

    def delete_entry(self, entry_id: int):
        """
        根据ID删除一个条目。
        由于设置了 ON DELETE CASCADE，`details` 表中的相关数据也会被自动删除。

        Args:
            entry_id (int): 要删除的条目的ID。
        """
        try:
            self.cursor.execute("DELETE FROM entries WHERE id=?", (entry_id,))
            self.conn.commit()
            logger.info(f"成功删除条目 (ID: {entry_id})。")
        except Exception as e:
            logger.error(f"删除条目 (ID: {entry_id}) 时发生错误: {e}", exc_info=True)

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """
        更改主密码并重新加密所有数据。

        这是一个关键的事务性操作：
        1. 从数据库读取所有加密数据。
        2. 在内存中使用当前（旧）密钥解密所有数据。
        3. 调用 CryptoHandler 更改主密钥（此步骤会验证旧密码）。
        4. 如果密钥更换成功，则启动一个数据库事务。
        5. 在事务中，用新密钥重新加密所有内存中的数据，并更新数据库。
        6. 如果任何步骤失败，将回滚所有更改。

        Args:
            old_password (str): 当前的主密码。
            new_password (str): 新的主密码。

        Returns:
            bool: 如果整个过程成功，返回 True；否则返回 False。
        """
        logger.info("开始更改主密码并重加密所有数据...")
        # 1. 获取所有当前加密的数据
        query = "SELECT entry_id, data FROM details"
        self.cursor.execute(query)
        all_encrypted_data = self.cursor.fetchall()

        decrypted_entries = []
        try:
            # 2. 用当前（旧）密钥在内存中解密所有数据
            logger.info(f"正在内存中解密 {len(all_encrypted_data)} 个条目...")
            for entry_id, encrypted_data in all_encrypted_data:
                decrypted_json = self.crypto.decrypt(encrypted_data)
                decrypted_entries.append({"id": entry_id, "json_data": decrypted_json})
        except InvalidToken:
            logger.error(
                "在密码更改前使用当前密钥解密失败。旧密码可能不正确或数据已损坏。操作中止。"
            )
            return False

        # 3. 尝试在加密层更换密钥（此步骤会验证旧密码）
        logger.info("正在验证旧密码并更新加密密钥...")
        if not self.crypto.change_master_password(old_password, new_password):
            # 失败信息已在 crypto_handler 中记录
            logger.error("CryptoHandler 未能更改主密码。操作中止。")
            return False

        # 4. 启动事务，用新密钥重加密并更新数据库
        logger.info("密钥更新成功。正在用新密钥重加密数据并更新数据库...")
        try:
            self.cursor.execute("BEGIN")

            for entry in decrypted_entries:
                new_encrypted_data = self.crypto.encrypt(entry["json_data"])
                self.cursor.execute(
                    "UPDATE details SET data = ? WHERE entry_id = ?",
                    (new_encrypted_data, entry["id"]),
                )

            self.conn.commit()
            logger.info("所有条目已成功重加密。主密码更改完成！")
            return True

        except Exception as e:
            logger.critical(
                f"在数据重加密的关键阶段发生错误: {e}。正在回滚数据库...", exc_info=True
            )
            self.conn.rollback()
            # 这是一个严重问题，可能导致状态不一致，需要提醒用户
            # 在实际产品中，这里可能需要更复杂的恢复逻辑
            return False

    def close(self):
        """
        提交任何待处理的更改并关闭数据库连接。
        """
        if self.conn:
            self.conn.commit()
            self.conn.close()
            logger.info("数据库连接已成功关闭。")
