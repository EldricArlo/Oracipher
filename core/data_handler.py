# core/data_handler.py

import csv
import io
import json
import logging
import re
import base64
import os
from typing import List, Dict, Any, Optional

from .crypto import CryptoHandler
from .importers import parse_google_chrome, GOOGLE_CHROME_HEADER, parse_samsung_pass

logger = logging.getLogger(__name__)

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
    """

    @staticmethod
    def export_to_encrypted_json(
        entries: List[Dict[str, Any]], crypto_handler: CryptoHandler
    ) -> bytes:
        logger.info(
            f"Preparing to securely export {len(entries)} entries to .skey format..."
        )
        try:
            salt = crypto_handler.get_salt()
            if not salt:
                raise ValueError(
                    "Cannot export: Salt not found. Vault may not be properly initialized."
                )

            data_json_string = json.dumps(entries, ensure_ascii=False)
            encrypted_data_string = crypto_handler.encrypt(data_json_string)

            export_payload = {
                "salt": base64.b64encode(salt).decode("utf-8"),
                "data": encrypted_data_string,
            }

            return json.dumps(export_payload, indent=2).encode("utf-8")
        except Exception as e:
            logger.error(f"Failed to create secure export package: {e}", exc_info=True)
            raise

    @staticmethod
    def export_to_csv(entries: List[Dict[str, Any]], include_totp: bool = False) -> str:
        """
        导出为CSV文件，并提供一个选项来决定是否包含TOTP密钥。
        """
        BASE_FIELDNAMES: List[str] = [
            "name",
            "username",
            "email",
            "password",
            "url",
            "notes",
            "category",
        ]

        fieldnames = BASE_FIELDNAMES[:]
        if include_totp:
            fieldnames.append("totp")

        logger.info(
            f"Preparing to export {len(entries)} entries to CSV. Include TOTP: {include_totp}"
        )
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
                        issuer = entry.get("name", "SafeKey").replace(":", "")
                        account = (
                            details.get("username") or details.get("email", "account")
                        ).replace(":", "")
                        row["totp"] = (
                            f"otpauth://totp/{issuer}:{account}?secret={totp_secret}&issuer={issuer}"
                        )
                    else:
                        row["totp"] = ""
                writer.writerow(row)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error during CSV export: {e}", exc_info=True)
            raise

    @staticmethod
    def import_from_encrypted_json(
        file_content_bytes: bytes, password: str
    ) -> List[Dict[str, Any]]:
        logger.info("Attempting to decrypt and import from .skey file...")
        try:
            from cryptography.fernet import Fernet

            import_payload = json.loads(file_content_bytes.decode("utf-8"))
            b64_salt = import_payload["salt"]
            encrypted_data_string = import_payload["data"]
            salt = base64.b64decode(b64_salt)

            derived_key = CryptoHandler._derive_key(password, salt)
            fernet = Fernet(derived_key)

            decrypted_json_string = fernet.decrypt(
                encrypted_data_string.encode("utf-8"), ttl=None
            )
            entries = json.loads(decrypted_json_string.decode("utf-8"))

            logger.info(
                f"Successfully decrypted and parsed {len(entries)} entries from .skey file."
            )
            return entries
        except (json.JSONDecodeError, KeyError):
            raise ValueError("Invalid .skey file format.")
        except Exception:
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

        if "name" not in field_map:
            raise ValueError(
                "Import failed: CSV file is missing a recognizable 'name' or 'title' column."
            )

        for row in reader:
            safe_row = {k.lower().strip(): v for k, v in row.items()}
            name_val = safe_row.get(field_map["name"], "").strip()
            if not name_val:
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
                        logger.warning(
                            f"Could not parse TOTP URI for entry '{name_val}': {e}"
                        )

            entry: Dict[str, Any] = {
                "name": name_val,
                "category": safe_row.get(field_map.get("category", ""), "").strip(),
                "details": details,
            }
            imported_entries.append(entry)

        return imported_entries

    @staticmethod
    def _parse_key_colon_value_format(content: str) -> List[Dict[str, Any]]:
        blocks = re.split(r"\n\s*\n+", content.strip())
        imported_entries: List[Dict[str, Any]] = []

        reverse_key_map = {
            alias: std_key for std_key, aliases in KEY_MAP.items() for alias in aliases
        }

        for block in blocks:
            lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
            if not lines:
                continue

            entry_name = lines.pop(0)
            parsed_data: Dict[str, str] = {}

            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    std_key = reverse_key_map.get(key.lower().strip())
                    if std_key:
                        parsed_data[std_key] = value.strip()

            if not parsed_data:
                continue

            entry: Dict[str, Any] = {
                "name": entry_name,
                "category": parsed_data.get("category", ""),
                "details": {k: v for k, v in parsed_data.items() if k != "category"},
            }
            imported_entries.append(entry)

        return imported_entries

    @staticmethod
    def _parse_double_slash_format(content: str) -> List[Dict[str, Any]]:
        lines = content.strip().split("\n")
        imported_entries: List[Dict[str, Any]] = []
        reverse_key_map = {
            alias: std_key for std_key, aliases in KEY_MAP.items() for alias in aliases
        }

        for line in lines:
            if not line.strip():
                continue

            parts = [p.strip() for p in line.split("//")]
            if not parts:
                continue

            entry_name = parts.pop(0)
            parsed_data: Dict[str, str] = {}

            for part in parts:
                key_val_pair = part.split(" ", 1)
                key = key_val_pair[0].lower().strip()
                value = key_val_pair[1].strip() if len(key_val_pair) > 1 else ""

                std_key = reverse_key_map.get(key)
                if std_key:
                    parsed_data[std_key] = value

            if not parsed_data:
                continue

            entry: Dict[str, Any] = {
                "name": entry_name,
                "category": parsed_data.get("category", ""),
                "details": {k: v for k, v in parsed_data.items() if k != "category"},
            }
            imported_entries.append(entry)

        return imported_entries

    @staticmethod
    def import_from_text(content: str) -> List[Dict[str, Any]]:
        first_lines = [line for line in content.strip().split("\n")[:5] if line.strip()]
        if first_lines and "//" in first_lines[0]:
            return DataHandler._parse_double_slash_format(content)
        else:
            return DataHandler._parse_key_colon_value_format(content)

    @staticmethod
    def import_from_file(
        file_path: str, password: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        logger.info(f"Starting import from file: {file_path}")
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == ".spass":
                if password is None:
                    raise ValueError("A password is required to decrypt .spass files.")
                with open(file_path, "r", encoding="utf-8") as f:
                    # 读取 Base64 文本内容，并将其编码回字节串以传递给解析器
                    file_content = f.read()
                    return parse_samsung_pass(file_content.encode("utf-8"), password)

            elif file_ext == ".skey":
                if password is None:
                    raise ValueError("A password is required to decrypt .skey files.")
                with open(file_path, "rb") as f:
                    file_content = f.read()
                return DataHandler.import_from_encrypted_json(file_content, password)

            with open(file_path, mode="r", encoding="utf-8-sig", newline="") as f:
                content = f.read()
                f.seek(0)

                if file_ext == ".csv":
                    try:
                        reader = csv.reader(io.StringIO(content))
                        header = [h.lower().strip() for h in next(reader)]

                        if header == GOOGLE_CHROME_HEADER:
                            return parse_google_chrome(content)

                        else:
                            logger.info(
                                "No specific CSV format detected, falling back to generic parser."
                            )
                            f.seek(0)
                            dict_reader = csv.DictReader(f)
                            return DataHandler._parse_generic_csv(dict_reader)

                    except Exception as e:
                        logger.warning(
                            f"Failed to sniff CSV format, trying generic parser. Error: {e}"
                        )
                        f.seek(0)
                        dict_reader = csv.DictReader(f)
                        return DataHandler._parse_generic_csv(dict_reader)

                elif file_ext in (".txt", ".md"):
                    return DataHandler.import_from_text(content)

                else:
                    raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            raise type(e)(f"Failed to process file: {e}") from e
