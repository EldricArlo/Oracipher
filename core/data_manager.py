# core/data_manager.py

import os
import sqlite3
import json
import logging
from typing import List, Dict, Any

from cryptography.fernet import InvalidToken
from .crypto import CryptoHandler

logger = logging.getLogger(__name__)

class DataManager:
    """
    管理所有针对加密数据库的读写操作。
    """
    def __init__(self, data_dir: str, crypto_handler: CryptoHandler):
        db_path: str = os.path.join(data_dir, "safekey.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn: sqlite3.Connection = sqlite3.connect(db_path)
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        self.crypto: CryptoHandler = crypto_handler
        self._create_tables()
        logger.info(f"DataManager 初始化成功，已连接到数据库: {db_path}")

    def _create_tables(self) -> None:
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
    
    def save_entry(self, category: str, name: str, details: Dict[str, Any]) -> None:
        try:
            data_json: str = json.dumps(details)
            encrypted_data: str = self.crypto.encrypt(data_json)
            self.cursor.execute('BEGIN')
            self.cursor.execute(
                """
                INSERT INTO entries (category, name) VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET category=excluded.category
                """,
                (category, name)
            )
            self.cursor.execute("SELECT id FROM entries WHERE name=?", (name,))
            result = self.cursor.fetchone()
            if result is None:
                raise Exception(f"Failed to retrieve ID for entry with name '{name}'")
            entry_id: int = result[0]
            self.cursor.execute(
                """
                INSERT INTO details (entry_id, data) VALUES (?, ?)
                ON CONFLICT(entry_id) DO UPDATE SET data=excluded.data
                """,
                (entry_id, encrypted_data)
            )
            self.conn.commit()
            logger.info(f"成功保存条目: '{name}' (ID: {entry_id})")
        except Exception as e:
            logger.error(f"保存条目 '{name}' 时发生数据库错误: {e}", exc_info=True)
            self.conn.rollback()

    def get_entries(self) -> List[Dict[str, Any]]:
        query = "SELECT e.id, e.category, e.name, d.data FROM entries e JOIN details d ON e.id = d.entry_id"
        self.cursor.execute(query)
        entries: List[Dict[str, Any]] = []
        for row in self.cursor.fetchall():
            entry_id, category, name, encrypted_data_str = row
            try:
                decrypted_data_json: str = self.crypto.decrypt(encrypted_data_str)
                details: Dict[str, Any] = json.loads(decrypted_data_json)
                entries.append({
                    "id": entry_id, 
                    "category": category, 
                    "name": name, 
                    "details": details
                })
            except InvalidToken:
                logger.error(f"无法解密条目 (ID: {entry_id})。可能是密钥不匹配或数据已损坏。")
            except json.JSONDecodeError:
                logger.error(f"无法解析条目 (ID: {entry_id}) 的JSON数据。数据可能已损坏。")
            except Exception as e:
                 logger.error(f"加载条目 (ID: {entry_id}) 时发生未知错误: {e}", exc_info=True)
        logger.info(f"成功加载并解密 {len(entries)} 个条目。")
        return entries

    def delete_entry(self, entry_id: int) -> None:
        try:
            self.cursor.execute("DELETE FROM entries WHERE id=?", (entry_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                logger.info(f"成功删除条目 (ID: {entry_id})。")
            else:
                logger.warning(f"尝试删除条目 (ID: {entry_id})，但未找到该条目。")
        except Exception as e:
            logger.error(f"删除条目 (ID: {entry_id}) 时发生错误: {e}", exc_info=True)

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        logger.info("开始更改主密码并重加密所有数据...")
        query = "SELECT entry_id, data FROM details"
        self.cursor.execute(query)
        all_encrypted_data = self.cursor.fetchall()
        decrypted_entries: List[Dict[str, Any]] = []
        try:
            logger.info(f"正在内存中解密 {len(all_encrypted_data)} 个条目...")
            for entry_id, encrypted_data in all_encrypted_data:
                decrypted_json: str = self.crypto.decrypt(encrypted_data)
                decrypted_entries.append({'id': entry_id, 'json_data': decrypted_json})
        except InvalidToken:
            logger.error("在密码更改前使用当前密钥解密失败。旧密码可能不正确或数据已损坏。操作中止。")
            return False
        logger.info("正在验证旧密码并更新加密密钥...")
        if not self.crypto.change_master_password(old_password, new_password):
            logger.error("CryptoHandler 未能更改主密码。操作中止。")
            return False
        logger.info("密钥更新成功。正在用新密钥重加密数据并更新数据库...")
        try:
            self.cursor.execute('BEGIN')
            for entry in decrypted_entries:
                new_encrypted_data: str = self.crypto.encrypt(entry['json_data'])
                self.cursor.execute(
                    "UPDATE details SET data = ? WHERE entry_id = ?",
                    (new_encrypted_data, entry['id'])
                )
            self.conn.commit()
            logger.info("所有条目已成功重加密。主密码更改完成！")
            return True
        except Exception as e:
            logger.critical(f"在数据重加密的关键阶段发生错误: {e}。正在回滚数据库...", exc_info=True)
            self.conn.rollback()
            return False

    def close(self) -> None:
        if self.conn:
            self.conn.commit()
            self.conn.close()
            logger.info("数据库连接已成功关闭。")