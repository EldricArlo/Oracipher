# core/database.py

import os
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional, Tuple

from cryptography.fernet import InvalidToken
from .crypto import CryptoHandler
from .database_migration import check_and_migrate_schema

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, data_dir: str, crypto_handler: CryptoHandler):
        self.db_path: str = os.path.join(data_dir, "safekey.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.crypto: CryptoHandler = crypto_handler
        self.conn: Optional[sqlite3.Connection] = None
        check_and_migrate_schema(self.db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self) -> None:
        if not self.conn: return
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY, category TEXT NOT NULL, name TEXT NOT NULL)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS details (entry_id INTEGER PRIMARY KEY, data TEXT NOT NULL, FOREIGN KEY (entry_id) REFERENCES entries (id) ON DELETE CASCADE)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS categories (name TEXT PRIMARY KEY NOT NULL, icon_data TEXT)")
        self.conn.commit()
    
    def save_entry_and_category_icon(self, entry_id, category, name, details, category_icon_data):
        if not self.conn: return
        try:
            self.cursor.execute('BEGIN')
            encrypted_data = self.crypto.encrypt(json.dumps(details))
            if entry_id is not None:
                self.cursor.execute("UPDATE entries SET category=?, name=? WHERE id=?", (category, name, entry_id))
                self.cursor.execute("UPDATE details SET data=? WHERE entry_id=?", (encrypted_data, entry_id))
            else:
                self.cursor.execute("INSERT INTO entries (category, name) VALUES (?, ?)", (category, name))
                new_id = self.cursor.lastrowid
                if new_id is None: raise sqlite3.Error("Failed to get last row ID.")
                self.cursor.execute("INSERT INTO details (entry_id, data) VALUES (?, ?)", (new_id, encrypted_data))
            if category_icon_data:
                self.cursor.execute("INSERT INTO categories (name, icon_data) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET icon_data=excluded.icon_data", category_icon_data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback(); raise
            
    def save_multiple_entries(self, entries: List[Dict[str, Any]]) -> Tuple[int, int, int]:
        """
        以智能方式批量保存条目：新增、更新或跳过。
        返回 (新增数, 更新数, 跳过数)
        """
        if not self.conn or not entries: return 0, 0, 0
        
        added, updated, skipped = 0, 0, 0
        
        try:
            existing_entries = self.get_entries()
            # 键: (名称, 用户名), 值: 数据库ID
            lookup_by_name_user: Dict[Tuple[str, str], int] = {}
            # 键: (所有细节), 值: None
            lookup_by_all_details: Dict[Tuple, None] = {}

            for entry in existing_entries:
                details = entry.get('details', {})
                name = entry.get('name', '').strip()
                username = details.get('username', '').strip()
                
                # 创建用于更新的查找字典
                if name or username:
                    lookup_by_name_user[(name, username)] = entry['id']
                
                # 创建用于精确去重的查找元组
                full_identifier = tuple(sorted(details.items()))
                lookup_by_all_details[(name, entry.get('category',''), full_identifier)] = None

            self.cursor.execute('BEGIN')
            for entry in entries:
                if 'name' not in entry or 'details' not in entry:
                    skipped += 1; continue
                
                details = entry.get('details', {})
                name = entry.get('name', '').strip()
                category = entry.get('category', '').strip()
                username = details.get('username', '').strip()

                # 检查是否完全重复
                current_full_id = tuple(sorted(details.items()))
                if (name, category, current_full_id) in lookup_by_all_details:
                    skipped += 1; continue
                
                encrypted_data = self.crypto.encrypt(json.dumps(details))
                
                # 检查是更新还是新增
                existing_id = lookup_by_name_user.get((name, username))
                if existing_id:
                    self.cursor.execute("UPDATE entries SET category=? WHERE id=?", (category, existing_id))
                    self.cursor.execute("UPDATE details SET data=? WHERE entry_id=?", (encrypted_data, existing_id))
                    updated += 1
                else:
                    self.cursor.execute("INSERT INTO entries (category, name) VALUES (?, ?)", (category, name))
                    new_id = self.cursor.lastrowid
                    if new_id is None: raise sqlite3.Error("Failed to get last row ID.")
                    self.cursor.execute("INSERT INTO details (entry_id, data) VALUES (?, ?)", (new_id, encrypted_data))
                    added += 1

            self.conn.commit()
            logger.info(f"Bulk save done. Added: {added}, Updated: {updated}, Skipped: {skipped}.")
            return added, updated, skipped
        except Exception as e:
            self.conn.rollback(); raise

    def get_entries(self) -> List[Dict[str, Any]]:
        # ... (此方法无需改动)
        if not self.conn: return []
        query = "SELECT e.id, e.category, e.name, d.data FROM entries e JOIN details d ON e.id = d.entry_id"
        self.cursor.execute(query)
        entries: List[Dict[str, Any]] = []
        for row in self.cursor.fetchall():
            entry_id, category, name, encrypted_data_str = row
            try:
                decrypted_data_json: str = self.crypto.decrypt(encrypted_data_str)
                details: Dict[str, Any] = json.loads(decrypted_data_json)
                entries.append({"id": entry_id, "category": category, "name": name, "details": details})
            except (InvalidToken, json.JSONDecodeError, Exception) as e:
                 logger.error(f"Error loading entry ID {entry_id}: {e}")
        return entries
    
    def delete_entry(self, entry_id: int) -> None:
        # ... (此方法无需改动)
        if not self.conn: return
        try:
            self.cursor.execute("DELETE FROM entries WHERE id=?", (entry_id,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error deleting entry ID {entry_id}: {e}", exc_info=True)
            raise

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        # ... (此方法无需改动)
        if not self.conn: return False
        self.cursor.execute("SELECT entry_id, data FROM details")
        all_encrypted_data = self.cursor.fetchall()
        decrypted_entries: List[Dict[str, Any]] = []
        try:
            for entry_id, encrypted_data in all_encrypted_data:
                decrypted_json: str = self.crypto.decrypt(encrypted_data)
                decrypted_entries.append({'id': entry_id, 'json_data': decrypted_json})
        except InvalidToken:
            return False
        if not self.crypto.change_master_password(old_password, new_password):
            return False
        try:
            self.cursor.execute('BEGIN')
            for entry in decrypted_entries:
                new_encrypted_data: str = self.crypto.encrypt(entry['json_data'])
                self.cursor.execute("UPDATE details SET data = ? WHERE entry_id = ?", (new_encrypted_data, entry['id']))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
            
    def close(self) -> None:
        # ... (此方法无需改动)
        if self.conn:
            try:
                self.conn.commit()
                self.conn.close()
                self.conn = None
            except Exception as e:
                logger.error(f"Error during database close: {e}", exc_info=True)

    def save_category_icon(self, category_name: str, icon_data_base64: str) -> None:
        # ... (此方法无需改动)
        if not self.conn: return
        try:
            self.cursor.execute("INSERT INTO categories (name, icon_data) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET icon_data=excluded.icon_data", (category_name, icon_data_base64))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise

    def get_category_icons(self) -> Dict[str, str]:
        # ... (此方法无需改动)
        if not self.conn: return {}
        try:
            self.cursor.execute("SELECT name, icon_data FROM categories")
            return {name: icon_data for name, icon_data in self.cursor.fetchall() if icon_data}
        except Exception:
            return {}