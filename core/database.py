# core/database.py

import os
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional, Tuple

from cryptography.fernet import InvalidToken
from .crypto import CryptoHandler
# 新增: 从分离的文件中导入架构迁移函数
from .database_migration import check_and_migrate_schema

logger = logging.getLogger(__name__)

class DataManager:
    """
    数据库管理器，封装所有与 SQLite 数据库的交互。
    """

    def __init__(self, data_dir: str, crypto_handler: CryptoHandler):
        self.db_path: str = os.path.join(data_dir, "safekey.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.crypto: CryptoHandler = crypto_handler
        self.conn: Optional[sqlite3.Connection] = None

        # 修改: 调用外部的迁移检查函数
        check_and_migrate_schema(self.db_path)
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        
        self._create_tables()
        logger.info(f"DataManager initialized. Database connection established: {self.db_path}")

    def _create_tables(self) -> None:
        if not self.conn: return
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL
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
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                name TEXT PRIMARY KEY NOT NULL,
                icon_data TEXT
            )
            """
        )
        self.conn.commit()
    
    def save_entry_and_category_icon(
        self,
        entry_id: Optional[int],
        category: str,
        name: str,
        details: Dict[str, Any],
        category_icon_data: Optional[Tuple[str, str]]
    ) -> None:
        if not self.conn: return
        try:
            self.cursor.execute('BEGIN')
            
            data_json: str = json.dumps(details)
            encrypted_data: str = self.crypto.encrypt(data_json)

            if entry_id is not None:
                self.cursor.execute("UPDATE entries SET category=?, name=? WHERE id=?", (category, name, entry_id))
                self.cursor.execute("UPDATE details SET data=? WHERE entry_id=?", (encrypted_data, entry_id))
                logger.info(f"Updated entry '{name}' (ID: {entry_id}) in transaction.")
            else:
                self.cursor.execute("INSERT INTO entries (category, name) VALUES (?, ?)", (category, name))
                new_entry_id = self.cursor.lastrowid
                if new_entry_id is None:
                    raise sqlite3.Error("Failed to retrieve last row ID after insertion.")
                self.cursor.execute("INSERT INTO details (entry_id, data) VALUES (?, ?)", (new_entry_id, encrypted_data))
                logger.info(f"Created new entry '{name}' (ID: {new_entry_id}) in transaction.")

            if category_icon_data:
                cat_name, icon_data = category_icon_data
                self.cursor.execute(
                    """
                    INSERT INTO categories (name, icon_data) VALUES (?, ?)
                    ON CONFLICT(name) DO UPDATE SET icon_data=excluded.icon_data
                    """,
                    (cat_name, icon_data)
                )
                logger.info(f"Upserted icon for category '{cat_name}' in transaction.")

            self.conn.commit()
            logger.info(f"Transaction for saving entry '{name}' and icon was successful.")
        except Exception as e:
            logger.error(f"Transaction failed for saving entry '{name}'. Rolling back. Error: {e}", exc_info=True)
            self.conn.rollback()
            raise

    def save_multiple_entries(self, entries: List[Dict[str, Any]]) -> int:
        """
        Saves a list of entries to the database within a single transaction.
        """
        if not self.conn or not entries:
            return 0
        
        count = 0
        try:
            logger.info(f"Starting bulk save of {len(entries)} entries...")
            self.cursor.execute('BEGIN')
            
            for entry in entries:
                if 'name' not in entry or 'details' not in entry:
                    logger.warning(f"Skipping malformed entry during bulk import: {entry}")
                    continue

                details = entry.get('details', {})
                category = entry.get('category', '')
                name = entry.get('name', '')
                
                data_json: str = json.dumps(details)
                encrypted_data: str = self.crypto.encrypt(data_json)
                
                self.cursor.execute("INSERT INTO entries (category, name) VALUES (?, ?)", (category, name))
                new_entry_id = self.cursor.lastrowid
                if new_entry_id is None:
                    raise sqlite3.Error(f"Failed to retrieve last row ID for entry '{name}'.")
                
                self.cursor.execute("INSERT INTO details (entry_id, data) VALUES (?, ?)", (new_entry_id, encrypted_data))
                count += 1

            self.conn.commit()
            logger.info(f"Bulk save successful. Committed {count} new entries.")
            return count
        except Exception as e:
            logger.error(f"Transaction failed during bulk save. Rolling back. Error: {e}", exc_info=True)
            self.conn.rollback()
            raise

    def get_entries(self) -> List[Dict[str, Any]]:
        if not self.conn: return []
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
                logger.error(f"Decryption failed for entry (ID: {entry_id}). Key mismatch or data corruption.")
            except json.JSONDecodeError:
                logger.error(f"JSON parsing failed for entry (ID: {entry_id}). Data may be corrupt.")
            except Exception as e:
                 logger.error(f"Unknown error loading entry (ID: {entry_id}): {e}", exc_info=True)
        
        logger.info(f"Successfully loaded and decrypted {len(entries)} entries.")
        return entries

    def delete_entry(self, entry_id: int) -> None:
        if not self.conn: return
        try:
            self.cursor.execute("DELETE FROM entries WHERE id=?", (entry_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                logger.info(f"Successfully deleted entry (ID: {entry_id}).")
            else:
                logger.warning(f"Attempted to delete non-existent entry (ID: {entry_id}).")
        except Exception as e:
            logger.error(f"Error deleting entry (ID: {entry_id}): {e}", exc_info=True)
            raise

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        if not self.conn: return False
        logger.info("Starting master password change process...")
        self.cursor.execute("SELECT entry_id, data FROM details")
        all_encrypted_data = self.cursor.fetchall()
        decrypted_entries: List[Dict[str, Any]] = []

        try:
            logger.info(f"Decrypting {len(all_encrypted_data)} entries with old key...")
            for entry_id, encrypted_data in all_encrypted_data:
                decrypted_json: str = self.crypto.decrypt(encrypted_data)
                decrypted_entries.append({'id': entry_id, 'json_data': decrypted_json})
        except InvalidToken:
            logger.error("Decryption failed with current key. The old password provided might be incorrect. Aborting.")
            return False

        logger.info("Verifying old password and updating encryption key at crypto layer...")
        if not self.crypto.change_master_password(old_password, new_password):
            logger.error("CryptoHandler rejected the password change. Aborting.")
            return False

        logger.info("Re-encrypting all data with the new key...")
        try:
            self.cursor.execute('BEGIN')
            for entry in decrypted_entries:
                new_encrypted_data: str = self.crypto.encrypt(entry['json_data'])
                self.cursor.execute(
                    "UPDATE details SET data = ? WHERE entry_id = ?",
                    (new_encrypted_data, entry['id'])
                )
            self.conn.commit()
            logger.info("All entries re-encrypted. Master password change complete!")
            return True
        except Exception as e:
            logger.critical(f"Critical error during re-encryption phase: {e}. Rolling back.", exc_info=True)
            self.conn.rollback()
            return False

    def close(self) -> None:
        if self.conn:
            try:
                self.conn.commit()
                self.conn.close()
                self.conn = None
                logger.info("Database connection closed.")
            except Exception as e:
                logger.error(f"Error during database close: {e}", exc_info=True)

    def save_category_icon(self, category_name: str, icon_data_base64: str) -> None:
        if not self.conn: return
        try:
            self.cursor.execute(
                """
                INSERT INTO categories (name, icon_data) VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET icon_data=excluded.icon_data
                """,
                (category_name, icon_data_base64)
            )
            self.conn.commit()
            logger.info(f"Saved icon for category '{category_name}'.")
        except Exception as e:
            logger.error(f"Database error saving icon for '{category_name}': {e}", exc_info=True)
            self.conn.rollback()
            raise

    def get_category_icons(self) -> Dict[str, str]:
        if not self.conn: return {}
        try:
            self.cursor.execute("SELECT name, icon_data FROM categories")
            return {name: icon_data for name, icon_data in self.cursor.fetchall() if icon_data}
        except Exception as e:
            logger.error(f"Database error fetching category icons: {e}", exc_info=True)
            return {}