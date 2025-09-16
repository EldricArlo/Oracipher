# core/data_handler.py

import csv
import io
import json
import logging
import re
import base64
import os
import struct
from typing import List, Dict, Any, Optional, Callable, NamedTuple

from .crypto import CryptoHandler
from .importers import parse_google_chrome, GOOGLE_CHROME_HEADER, parse_samsung_pass
from .exporters import export_samsung_pass

logger = logging.getLogger(__name__)


class Importer(NamedTuple):
    """定义一个导入器的结构"""
    name: str  # 用于在文件对话框中显示的名称
    extensions: List[str]  # 此导入器支持的文件扩展名
    handler: Callable  # 处理文件内容的函数
    requires_password: bool = False # 导入是否需要密码
    read_mode: str = 'r'  # 'r' for text, 'rb' for binary

class Exporter(NamedTuple):
    """定义一个导出器的结构"""
    name: str # 用于在文件对话框中显示的名称
    extension: str # 默认文件扩展名
    handler: Callable # 处理导出的函数
    requires_password: bool = False # 导出是否需要密码


# 用于通用CSV解析的键映射
KEY_MAP = {
    "name": ["name", "title", "名称"],
    "username": ["username", "usename", "login", "user", "user id", "用户名", "用户"],
    "email": ["email", "邮箱"],
    "password": ["password", "pass", "密码"],
    "url": ["url", "website", "address", "uri", "网址", "地址"],
    "notes": ["notes", "remark", "extra", "备注"],
    "category": ["category", "cat", "group", "folder", "分类"],
    "totp": ["totp", "otpauth", "2fa", "2fa_app", "authenticator", "两步验证"],
}


class DataHandler:
    """
    负责处理数据的导入和导出，支持多种格式。
    (已重构为可扩展的注册表模式)
    """

    # ----------------------------------------------------------------
    # 导入器注册表
    # ----------------------------------------------------------------
    _IMPORTERS = {
        '.pher': Importer(
            name="Oracipher Encrypted File",
            extensions=['.pher'],
            handler=lambda content, pwd: DataHandler._import_from_pher(content, pwd),
            requires_password=True,
            read_mode='rb'
        ),
        '.skey': Importer( # 用于向后兼容
            name="Legacy Oracipher File",
            extensions=['.skey'],
            handler=lambda content, pwd: DataHandler._import_from_legacy_skey(content, pwd),
            requires_password=True,
            read_mode='rb'
        ),
        '.spass': Importer(
            name="Samsung Pass",
            extensions=['.spass'],
            handler=lambda content, pwd: parse_samsung_pass(content, pwd),
            requires_password=True,
            read_mode='rb'
        ),
        '.csv': Importer(
            name="CSV File",
            extensions=['.csv'],
            handler=lambda content, pwd: DataHandler._handle_csv_import(content.decode('utf-8-sig')),
            requires_password=False,
            read_mode='rb' # 以二进制读取，在handler内部解码
        ),
        '.txt': Importer(
            name="Text File",
            extensions=['.txt', '.md'],
            handler=lambda content, pwd: DataHandler.import_from_text(content.decode('utf-8')),
            requires_password=False,
            read_mode='rb' # 以二进制读取，在handler内部解码
        )
    }

    # ----------------------------------------------------------------
    # 导出器注册表
    # ----------------------------------------------------------------
    _EXPORTERS = {
        '.pher': Exporter(
            name="Oracipher Encrypted File (*.pher)",
            extension=".pher",
            handler=lambda entries, **kwargs: DataHandler.export_to_pher(entries, kwargs['crypto_handler']),
            requires_password=False # 密码来自 crypto_handler
        ),
        '.spass': Exporter(
            name="Samsung Pass Encrypted (*.spass)",
            extension=".spass",
            handler=lambda entries, **kwargs: export_samsung_pass(entries, kwargs['password']),
            requires_password=True
        ),
        '.csv': Exporter(
            name="CSV (Unsecure) (*.csv)",
            extension=".csv",
            handler=lambda entries, **kwargs: DataHandler.export_to_csv(entries, kwargs['include_totp']),
            requires_password=False
        )
    }

    # ================================================================
    # 公共静态方法 (Public Static Methods)
    # ================================================================

    @staticmethod
    def get_import_filter() -> str:
        """从注册表动态生成QFileDialog的导入过滤器字符串。"""
        filters = []
        all_exts = " ".join(f"*{ext}" for importer in DataHandler._IMPORTERS.values() for ext in importer.extensions)
        filters.append(f"All Supported Files ({all_exts})")
        
        # 使用一个集合来避免重复添加过滤器（例如.txt和.md使用同一个importer）
        added_importers = set()
        for importer in DataHandler._IMPORTERS.values():
            if importer.name not in added_importers:
                ext_str = " ".join(f"*{ext}" for ext in importer.extensions)
                filters.append(f"{importer.name} ({ext_str})")
                added_importers.add(importer.name)
        
        return ";;".join(filters)

    @staticmethod
    def get_export_filter() -> str:
        """从注册表动态生成QFileDialog的导出过滤器字符串。"""
        return ";;".join(exporter.name for exporter in DataHandler._EXPORTERS.values())

    @staticmethod
    def import_from_file(file_path: str, password: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        根据文件扩展名，从注册表动态选择合适的导入器来处理文件。
        """
        logger.info(f"Starting import from file: {file_path}")
        file_ext = os.path.splitext(file_path)[1].lower()
        
        importer: Optional[Importer] = None
        # 优先直接匹配主扩展名
        if file_ext in DataHandler._IMPORTERS:
            importer = DataHandler._IMPORTERS[file_ext]
        else:
            # 否则遍历查找支持该扩展名的importer
            for imp in DataHandler._IMPORTERS.values():
                if file_ext in imp.extensions:
                    importer = imp
                    break
        
        if not importer:
            raise ValueError(f"Unsupported file format: {file_ext}")

        try:
            with open(file_path, mode=importer.read_mode) as f:
                content = f.read()
            
            if importer.requires_password and not password:
                raise ValueError(f"A password is required to import {file_ext} files.")

            return importer.handler(content, password)

        except FileNotFoundError:
            raise FileNotFoundError(f"The file could not be found: {file_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied to read the file: {file_path}")
        except ValueError as e:
            raise ValueError(f"Failed to parse file content: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing file '{file_path}': {e}", exc_info=True)
            raise IOError(f"An unexpected error occurred while processing the file.")
            
    # ================================================================
    # 具体的导入/导出实现 (部分已设为私有方法)
    # ================================================================
    
    # --- 导出实现 ---
    @staticmethod
    def export_to_pher(entries: List[Dict[str, Any]], crypto_handler: CryptoHandler) -> bytes:
        """
        将条目导出为独特的、加密的 .pher 格式。
        格式: [MAGIC_NUMBER (9 bytes)] [VERSION (1 byte)] [METADATA_LEN (4 bytes)] [METADATA_JSON] [ENCRYPTED_DATA]
        """
        logger.info(f"Preparing to securely export {len(entries)} entries to .pher format...")
        try:
            meta = crypto_handler.get_metadata()
            if not meta:
                raise ValueError("Cannot export: Metadata not found.")
            
            data_json_string = json.dumps(entries, ensure_ascii=False)
            encrypted_data = crypto_handler.encrypt(data_json_string).encode('utf-8')

            meta_bytes = json.dumps(meta).encode('utf-8')
            meta_len_bytes = struct.pack('>I', len(meta_bytes))

            file_content = (
                b'ORACIPHER' + b'\x01' + meta_len_bytes + meta_bytes + encrypted_data
            )
            return file_content
        except Exception as e:
            logger.error(f"Failed to create secure .pher export package: {e}", exc_info=True)
            raise

    @staticmethod
    def export_to_csv(entries: List[Dict[str, Any]], include_totp: bool = False) -> str:
        """
        导出为CSV文件，并提供一个选项来决定是否包含TOTP密钥。
        """
        BASE_FIELDNAMES: List[str] = [
            "name", "username", "email", "password", "url", "notes", "category",
        ]
        fieldnames = BASE_FIELDNAMES[:]
        if include_totp:
            fieldnames.append("totp")

        logger.info(f"Preparing to export {len(entries)} entries to CSV. Include TOTP: {include_totp}")
        try:
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for entry in entries:
                details = entry.get("details", {})
                row = {
                    "name": entry.get("name", ""),
                    "username": details.get("username", ""),
                    "email": details.get("email", ""),
                    "password": details.get("password", ""),
                    "url": details.get("url", ""),
                    "notes": details.get("notes", ""),
                    "category": entry.get("category", ""),
                }
                if include_totp:
                    totp_secret = details.get("totp_secret", "")
                    if totp_secret:
                        issuer = entry.get("name", "Oracipher").replace(":", "")
                        account = (details.get("username") or details.get("email", "account")).replace(":", "")
                        row["totp"] = f"otpauth://totp/{issuer}:{account}?secret={totp_secret}&issuer={issuer}"
                    else:
                        row["totp"] = ""
                writer.writerow(row)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error during CSV export: {e}", exc_info=True)
            raise

    # --- 导入实现 ---
    @staticmethod
    def _import_from_pher(file_content_bytes: bytes, password: str) -> List[Dict[str, Any]]:
        """从 .pher 格式文件导入数据。"""
        logger.info("Attempting to decrypt and import from .pher file...")
        try:
            from cryptography.fernet import Fernet
            
            if not file_content_bytes.startswith(b'ORACIPHER'):
                raise ValueError("Invalid file format: incorrect magic number.")
            
            version = file_content_bytes[9:10]
            if version != b'\x01':
                raise ValueError(f"Unsupported file version: {version!r}")
                
            meta_len = struct.unpack('>I', file_content_bytes[10:14])[0]
            meta_end = 14 + meta_len
            meta = json.loads(file_content_bytes[14:meta_end].decode('utf-8'))
            encrypted_data = file_content_bytes[meta_end:]
            
            salt = base64.b64decode(meta['salt_b64'])
            params = meta['argon2_params']
            derived_key = CryptoHandler._derive_key(password, salt, params)
            fernet = Fernet(derived_key)
            decrypted_json_string = fernet.decrypt(encrypted_data, ttl=None)
            entries = json.loads(decrypted_json_string.decode('utf-8'))

            logger.info(f"Successfully decrypted and parsed {len(entries)} entries from .pher file.")
            return entries
        except (struct.error, json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Invalid .pher file structure: {e}", exc_info=True)
            raise ValueError("Invalid or corrupt .pher file format.")
        except Exception:
            logger.error("Decryption failed. Incorrect password or corrupt file.", exc_info=True)
            raise ValueError("Incorrect password or corrupt file.")
            
    @staticmethod
    def _import_from_legacy_skey(file_content_bytes: bytes, password: str) -> List[Dict[str, Any]]:
        """从旧的 .skey (JSON) 格式文件导入数据，用于向后兼容。"""
        logger.info("Attempting to import from legacy .skey file...")
        try:
            from cryptography.fernet import Fernet

            import_payload = json.loads(file_content_bytes.decode("utf-8"))
            encrypted_data_string = import_payload["data"]
            
            if "metadata" in import_payload:
                meta = import_payload["metadata"]
                salt = base64.b64decode(meta['salt_b64'])
                params = meta['argon2_params']
            else:
                b64_salt = import_payload["salt"]
                salt = base64.b64decode(b64_salt)
                params = {'time_cost': 3, 'memory_cost': 65536, 'parallelism': 4}
            
            derived_key = CryptoHandler._derive_key(password, salt, params)
            fernet = Fernet(derived_key)
            decrypted_json_string = fernet.decrypt(encrypted_data_string.encode("utf-8"), ttl=None)
            entries = json.loads(decrypted_json_string.decode('utf-8'))

            return entries
        except (json.JSONDecodeError, KeyError):
            raise ValueError("Invalid .skey file format.")
        except Exception:
            raise ValueError("Incorrect password or corrupt file.")

    @staticmethod
    def _handle_csv_import(content: str) -> List[Dict[str, Any]]:
        """智能判断是Google Chrome CSV还是通用CSV。"""
        try:
            reader = csv.reader(io.StringIO(content))
            header = [h.lower().strip() for h in next(reader)]
            if header == GOOGLE_CHROME_HEADER:
                return parse_google_chrome(content)
        except Exception:
            pass
        
        dict_reader = csv.DictReader(io.StringIO(content))
        return DataHandler._parse_generic_csv(dict_reader)

    @staticmethod
    def _parse_generic_csv(reader: csv.DictReader) -> List[Dict[str, Any]]:
        """解析通用格式的CSV文件。"""
        logger.debug("Parsing file with generic CSV handler.")
        imported_entries: List[Dict[str, Any]] = []

        header = [h.lower().strip() for h in (reader.fieldnames or [])]
        field_map: Dict[str, str] = {}
        for std_key, aliases in KEY_MAP.items():
            for alias in aliases:
                if alias in header:
                    field_map[std_key] = alias
                    break

        if "name" not in field_map:
            raise ValueError("Import failed: CSV file is missing a recognizable 'name' or 'title' column.")

        for row_num, row in enumerate(reader, 1):
            safe_row = {k.lower().strip() if k else '': v for k, v in row.items()}
            name_val = safe_row.get(field_map["name"], "").strip()
            if not name_val:
                logger.debug(f"Skipping empty row {row_num} in generic CSV.")
                continue

            details = {
                std_key: safe_row.get(csv_key, "").strip()
                for std_key, csv_key in field_map.items()
                if std_key not in ["name", "category", "totp"]
            }

            if "totp" in field_map:
                otp_uri = safe_row.get(field_map["totp"], "")
                if otp_uri.startswith("otpauth://"):
                    try:
                        from urllib.parse import urlparse, parse_qs
                        query = parse_qs(urlparse(otp_uri).query)
                        if "secret" in query:
                            details["totp_secret"] = query["secret"][0]
                    except Exception as e:
                        logger.warning(f"Could not parse TOTP URI for entry '{name_val}': {e}")

            entry: Dict[str, Any] = {
                "name": name_val,
                "category": safe_row.get(field_map.get("category", ""), "").strip(),
                "details": details,
            }
            imported_entries.append(entry)

        return imported_entries

    @staticmethod
    def import_from_text(content: str) -> List[Dict[str, Any]]:
        """根据内容自动选择解析器来解析纯文本文件。"""
        first_lines = [line for line in content.strip().split("\n")[:5] if line.strip()]
        if first_lines and "//" in first_lines[0]:
            return DataHandler._parse_double_slash_format(content)
        else:
            return DataHandler._parse_key_colon_value_format(content)

    @staticmethod
    def _parse_key_colon_value_format(content: str) -> List[Dict[str, Any]]:
        """解析 键:值 格式的文本块。"""
        blocks = re.split(r"\n\s*\n+", content.strip())
        imported_entries: List[Dict[str, Any]] = []

        reverse_key_map = {
            alias: std_key for std_key, aliases in KEY_MAP.items() for alias in aliases
        }

        for block in blocks:
            lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
            if not lines: continue

            entry_name = lines.pop(0)
            parsed_data: Dict[str, str] = {}
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    std_key = reverse_key_map.get(key.lower().strip())
                    if std_key:
                        parsed_data[std_key] = value.strip()

            if not parsed_data: continue
            entry: Dict[str, Any] = {
                "name": entry_name,
                "category": parsed_data.get("category", ""),
                "details": {k: v for k, v in parsed_data.items() if k != "category"},
            }
            imported_entries.append(entry)
        return imported_entries

    @staticmethod
    def _parse_double_slash_format(content: str) -> List[Dict[str, Any]]:
        """解析使用 // 分隔的单行格式文本。"""
        lines = content.strip().split("\n")
        imported_entries: List[Dict[str, Any]] = []
        reverse_key_map = {
            alias: std_key for std_key, aliases in KEY_MAP.items() for alias in aliases
        }

        for line in lines:
            if not line.strip(): continue
            parts = [p.strip() for p in line.split("//")]
            if not parts: continue

            entry_name = parts.pop(0)
            parsed_data: Dict[str, str] = {}
            for part in parts:
                key_val_pair = part.split(" ", 1)
                key = key_val_pair[0].lower().strip()
                value = key_val_pair[1].strip() if len(key_val_pair) > 1 else ""
                std_key = reverse_key_map.get(key)
                if std_key:
                    parsed_data[std_key] = value

            if not parsed_data: continue
            entry: Dict[str, Any] = {
                "name": entry_name,
                "category": parsed_data.get("category", ""),
                "details": {k: v for k, v in parsed_data.items() if k != "category"},
            }
            imported_entries.append(entry)
        return imported_entries