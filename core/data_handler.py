# core/data_handler.py

import csv
import io
import json
import logging
import re
import base64
import os
from typing import List, Dict, Any, Optional, Callable

from .crypto import CryptoHandler

logger = logging.getLogger(__name__)

KEY_MAP = {
    'name': ['name', 'title', '名称'],
    'username': ['username', 'usename', 'login', 'user', '用户名', '用户'],
    'email': ['email', '邮箱'],
    'password': ['password', 'pass', '密码'],
    'url': ['url', 'website', 'address', 'uri', '网址', '地址'],
    'notes': ['notes', 'remark', 'extra', '备注'],
    'category': ['category', 'cat', 'group', 'folder', '分类'],
    '2fa_app': ['2fa', '2fa authenticator app', 'authenticator', 'otpauth', '两步验证'],
}

class DataHandler:
    """
    负责处理数据的导入和导出，支持多种格式。
    """
    
    @staticmethod
    def export_to_encrypted_json(entries: List[Dict[str, Any]], crypto_handler: CryptoHandler) -> bytes:
        logger.info(f"Preparing to securely export {len(entries)} entries to .skey format...")
        try:
            salt = crypto_handler.get_salt()
            if not salt:
                raise ValueError("Cannot export: Salt not found. Vault may not be properly initialized.")
            
            data_json_string = json.dumps(entries, ensure_ascii=False)
            encrypted_data_string = crypto_handler.encrypt(data_json_string)
            
            export_payload = {
                "salt": base64.b64encode(salt).decode('utf-8'),
                "data": encrypted_data_string
            }
            
            return json.dumps(export_payload, indent=2).encode('utf-8')
        except Exception as e:
            logger.error(f"Failed to create secure export package: {e}", exc_info=True)
            raise

    @staticmethod
    def export_to_csv(entries: List[Dict[str, Any]]) -> str:
        CSV_FIELDNAMES: List[str] = ['name', 'username', 'email', 'password', 'url', 'notes', 'category']
        logger.info(f"Preparing to export {len(entries)} entries to standard CSV...")
        try:
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()
            for entry in entries:
                details = entry.get('details', {})
                row = {
                    'name': entry.get('name', ''),
                    'username': details.get('username', ''),
                    'email': details.get('email', ''),
                    'password': details.get('password', ''),
                    'url': details.get('url', ''),
                    'notes': details.get('notes', ''),
                    'category': entry.get('category', '')
                }
                writer.writerow(row)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error during CSV export: {e}", exc_info=True)
            raise

    @staticmethod
    def import_from_encrypted_json(file_content_bytes: bytes, password: str) -> List[Dict[str, Any]]:
        logger.info("Attempting to decrypt and import from .skey file...")
        try:
            from cryptography.fernet import Fernet
            from argon2.low_level import hash_secret_raw, Type
            
            import_payload = json.loads(file_content_bytes.decode('utf-8'))
            b64_salt = import_payload["salt"]
            encrypted_data_string = import_payload["data"]

            salt = base64.b64decode(b64_salt)
            
            raw_key = hash_secret_raw(
                secret=password.encode('utf-8'), salt=salt,
                time_cost=3, memory_cost=65536, parallelism=4,
                hash_len=32, type=Type.ID
            )
            derived_key = base64.urlsafe_b64encode(raw_key)
            fernet = Fernet(derived_key)
            
            decrypted_json_string = fernet.decrypt(encrypted_data_string.encode('utf-8'), ttl=None)
            entries = json.loads(decrypted_json_string.decode('utf-8'))
            
            logger.info(f"Successfully decrypted and parsed {len(entries)} entries from .skey file.")
            return entries
        except (json.JSONDecodeError, KeyError):
            logger.error(f"Failed to parse .skey file structure. It may be corrupt or invalid.", exc_info=True)
            raise ValueError("Invalid .skey file format.")
        except Exception:
            logger.error("Failed to decrypt .skey file. Incorrect password or corrupt file.", exc_info=True)
            raise ValueError("Incorrect password or corrupt file.")

    @staticmethod
    def _parse_generic_csv(reader: csv.DictReader) -> List[Dict[str, Any]]:
        imported_entries: List[Dict[str, Any]] = []
        
        header = [h.lower().strip() for h in (reader.fieldnames or [])]
        field_map: Dict[str, str] = {}
        for std_key, aliases in KEY_MAP.items():
            for alias in aliases:
                if alias in header:
                    field_map[std_key] = alias
                    break
        
        if 'name' not in field_map:
             raise ValueError("Import failed: CSV file is missing a recognizable 'name' or 'title' column.")

        for row in reader:
            safe_row = {k.lower().strip(): v for k, v in row.items()}
            
            name_val = safe_row.get(field_map['name'], '').strip()
            if not name_val: continue
                
            details = {
                std_key: safe_row.get(csv_key, '').strip()
                for std_key, csv_key in field_map.items()
                if std_key not in ['name', 'category']
            }

            entry: Dict[str, Any] = {
                "name": name_val,
                "category": safe_row.get(field_map.get('category', ''), '').strip(),
                "details": details
            }
            imported_entries.append(entry)
            
        return imported_entries

    @staticmethod
    def _parse_key_colon_value_format(content: str) -> List[Dict[str, Any]]:
        blocks = re.split(r'\n\s*\n+', content.strip())
        imported_entries: List[Dict[str, Any]] = []
        
        reverse_key_map = {alias: std_key for std_key, aliases in KEY_MAP.items() for alias in aliases}

        for block in blocks:
            lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
            if not lines: continue
            
            entry_name = lines.pop(0)
            parsed_data: Dict[str, str] = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    std_key = reverse_key_map.get(key.lower().strip())
                    if std_key: parsed_data[std_key] = value.strip()
            
            if not parsed_data: continue

            entry: Dict[str, Any] = {
                "name": entry_name,
                "category": parsed_data.get('category', ''),
                "details": {k: v for k, v in parsed_data.items() if k != 'category'}
            }
            imported_entries.append(entry)
            
        return imported_entries

    @staticmethod
    def _parse_double_slash_format(content: str) -> List[Dict[str, Any]]:
        lines = content.strip().split('\n')
        imported_entries: List[Dict[str, Any]] = []
        reverse_key_map = {alias: std_key for std_key, aliases in KEY_MAP.items() for alias in aliases}

        for line in lines:
            if not line.strip(): continue
            
            parts = [p.strip() for p in line.split('//')]
            if not parts: continue

            entry_name = parts.pop(0)
            parsed_data: Dict[str, str] = {}

            for part in parts:
                key_val_pair = part.split(' ', 1)
                key = key_val_pair[0].lower().strip()
                value = key_val_pair[1].strip() if len(key_val_pair) > 1 else ""
                
                std_key = reverse_key_map.get(key)
                if std_key: parsed_data[std_key] = value

            if not parsed_data: continue

            entry: Dict[str, Any] = {
                "name": entry_name,
                "category": parsed_data.get('category', ''),
                "details": {k: v for k, v in parsed_data.items() if k != 'category'}
            }
            imported_entries.append(entry)

        return imported_entries

    @staticmethod
    def import_from_text(content: str) -> List[Dict[str, Any]]:
        first_lines = [line for line in content.strip().split('\n')[:5] if line.strip()]
        if first_lines and '//' in first_lines[0]:
            logger.info("Detected double-slash text format. Using new parser.")
            return DataHandler._parse_double_slash_format(content)
        else:
            logger.info("Detected colon-separated text format. Using legacy parser.")
            return DataHandler._parse_key_colon_value_format(content)

    @staticmethod
    def import_from_file(file_path: str, password_provider: Optional[Callable[[], Optional[str]]] = None) -> List[Dict[str, Any]]:
        logger.info(f"Starting import from file: {file_path}")
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.skey':
                if not password_provider:
                    raise ValueError("A password provider is required to decrypt .skey files.")
                
                password = password_provider()
                if not password:
                    logger.warning("Import cancelled by user (no password provided for .skey).")
                    return []
                
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                return DataHandler.import_from_encrypted_json(file_content, password)
            
            with open(file_path, mode='r', encoding='utf-8-sig', newline='') as f:
                if file_ext == '.csv':
                    try:
                        dialect = csv.Sniffer().sniff(f.read(2048))
                        f.seek(0)
                        reader = csv.DictReader(f, dialect=dialect)
                    except csv.Error:
                        f.seek(0)
                        reader = csv.DictReader(f)
                    return DataHandler._parse_generic_csv(reader)
                
                elif file_ext in ('.txt', '.md'):
                    content = f.read()
                    return DataHandler.import_from_text(content)
                
                else:
                    raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            logger.error(f"Failed to import file '{os.path.basename(file_path)}'.", exc_info=True)
            raise type(e)(f"Failed to process file: {e}") from e