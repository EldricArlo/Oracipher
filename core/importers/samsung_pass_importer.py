# core/importers/samsung_pass_importer.py

import csv
import io
import logging
import base64
import hashlib

# Import 're' for regular expressions
import re

from typing import List, Dict, Any

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

logger = logging.getLogger(__name__)


# Improved URL cleaning logic
def clean_android_url(url: str) -> str:
    """
    智能清理URL，优先保留标准网址，只转换非标准的 Android App Link。
    """
    if not url:
        return ""

    # 1. 首先，检查这是否是一个看起来像标准网址的链接。
    #    这个正则表达式会查找一个点后面跟着至少两个字母的模式 (e.g., .com, .ai, .co.uk)
    #    这可以覆盖绝大多数的域名格式。
    if re.search(r"\.[a-zA-Z]{2,}", url):
        return url

    # 2. 如果不是标准网址，再检查它是否是 Android App Link。
    if url.startswith("android://"):
        try:
            package_name = url.split("@")[-1]

            package_to_domain_map = {
                "com.anthropic.claude": "claude.ai",
                "com.google.android.gm": "mail.google.com",
                "com.google.android.googlequicksearchbox": "google.com",
                "com.facebook.katana": "facebook.com",
                "com.twitter.android": "twitter.com",
                "com.instagram.android": "instagram.com",
                "com.zhiliaoapp.musically": "tiktok.com",
                "com.tencent.mm": "weixin.qq.com",
            }

            if package_name in package_to_domain_map:
                return package_to_domain_map[package_name]

            parts = package_name.split(".")
            if len(parts) >= 2:
                domain = f"{parts[-2]}.{parts[-1]}"
                if "android" not in domain:
                    return domain

            return package_name
        except Exception:
            # 如果解析失败，安全地返回原始URL
            return url

    # 3. 如果以上都不是，直接返回原始的、未知的URL格式。
    return url

def parse_decrypted_content(decrypted_content: str) -> List[Dict[str, Any]]:
    logger.info(
        "Parsing the decrypted multi-block content with double Base64 decoding..."
    )
    imported_entries: List[Dict[str, Any]] = []

    blocks = decrypted_content.split("next_table")
    login_data_block = None
    expected_header_str = "_id;origin_url;action_url;username_element;username_value;id_tz_enc;password_element;password_value;pw_tz_enc;host_url;ssl_valid;preferred;blacklisted_by_user;use_additional_auth;cm_api_support;created_time;modified_time;title;favicon;source_type;app_name;package_name;package_signature;reserved_1;reserved_2;reserved_3;reserved_4;reserved_5;reserved_6;reserved_7;reserved_8;credential_memo;otp"
    for block in blocks:
        clean_block = block.strip()
        if clean_block.startswith(expected_header_str):
            login_data_block = clean_block
            break

    if not login_data_block:
        raise ValueError(
            "Could not find the login data block in the decrypted content."
        )

    reader = csv.DictReader(io.StringIO(login_data_block), delimiter=";")

    for row in reader:
        title_b64 = row.get("title", "").strip()
        if not title_b64:
            continue

        def decode_field(field_name: str) -> str:
            b64_string = row.get(field_name, "")
            if not b64_string or b64_string == "JiYmTlVMTCYmJg==":
                return ""
            try:
                missing_padding = len(b64_string) % 4
                if missing_padding:
                    b64_string += "=" * (4 - missing_padding)
                return base64.b64decode(b64_string).decode("utf-8")
            except Exception:
                return row.get(field_name, "")

        raw_url = decode_field("origin_url")
        cleaned_url = clean_android_url(raw_url)

        entry: Dict[str, Any] = {
            "name": decode_field("title"),
            "category": "Samsung Pass",
            "details": {
                "username": decode_field("username_value"),
                "password": decode_field("password_value"),
                "url": cleaned_url,
                "notes": decode_field("credential_memo"),
            },
        }
        imported_entries.append(entry)

    return imported_entries


def parse(file_content_bytes: bytes, password: str) -> List[Dict[str, Any]]:
    logger.info(
        "Attempting to decrypt and parse Samsung Pass file with validated parameters..."
    )

    try:
        base64_data = file_content_bytes.decode("utf-8").strip()
        binary_data = base64.b64decode(base64_data)

        salt_bytes_len = 20
        block_size = 16

        salt = binary_data[:salt_bytes_len]
        iv = binary_data[salt_bytes_len : salt_bytes_len + block_size]
        encrypted_data = binary_data[salt_bytes_len + block_size :]

        iteration_count = 70000
        key_length = 32

        key = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, iteration_count, dklen=key_length
        )

        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded_data = cipher.decrypt(encrypted_data)
        decrypted_data = unpad(decrypted_padded_data, AES.block_size, style="pkcs7")

        final_content = decrypted_data.decode("utf-8")

        entries = parse_decrypted_content(final_content)

        logger.info(
            f"Successfully decrypted and parsed {len(entries)} entries from Samsung Pass file."
        )
        return entries

    except (ValueError, KeyError) as e:
        logger.error(
            f"Decryption failed. This strongly suggests an incorrect password or a corrupt file. Details: {e}",
            exc_info=True,
        )
        raise ValueError("Decryption failed. Please ensure your password is correct.")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during Samsung Pass import: {e}",
            exc_info=True,
        )
        raise ValueError(f"An unexpected error occurred: {e}")
