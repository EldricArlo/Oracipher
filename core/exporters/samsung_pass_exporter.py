# core/exporters/samsung_pass_exporter.py

import base64
import hashlib
import io
import csv
import logging
import os
from typing import List, Dict, Any

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

logger = logging.getLogger(__name__)

def _encode_field(data: str) -> str:
    """对字段进行Base64编码，处理空值。"""
    if not data:
        # "%%NULL%%" in base64
        return "JiYmTlVMTCYmJg=="
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")

def export(entries: List[Dict[str, Any]], password: str) -> bytes:
    """
    将条目加密并打包成三星密码本 (.spass) 兼容的格式。
    """
    logger.info(f"Starting export of {len(entries)} entries to Samsung Pass format.")

    # 1. 准备要加密的CSV内容
    output = io.StringIO()
    # 这是三星.spass文件内部期望的固定头部
    header = "_id;origin_url;action_url;username_element;username_value;id_tz_enc;password_element;password_value;pw_tz_enc;host_url;ssl_valid;preferred;blacklisted_by_user;use_additional_auth;cm_api_support;created_time;modified_time;title;favicon;source_type;app_name;package_name;package_signature;reserved_1;reserved_2;reserved_3;reserved_4;reserved_5;reserved_6;reserved_7;reserved_8;credential_memo;otp"
    output.write(header + "\n")
    
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_NONE, escapechar='\\')

    for i, entry in enumerate(entries):
        details = entry.get("details", {})
        # 构造三星格式的一行数据
        row = [
            i + 1,  # _id
            _encode_field(details.get("url", "")), # origin_url
            _encode_field(""), # action_url
            _encode_field(""), # username_element
            _encode_field(details.get("username", "")), # username_value
            _encode_field(""), # id_tz_enc
            _encode_field(""), # password_element
            _encode_field(details.get("password", "")), # password_value
            _encode_field(""), # pw_tz_enc
            _encode_field(details.get("url", "")), # host_url
            _encode_field("true"), # ssl_valid
            _encode_field("true"), # preferred
            _encode_field("false"), # blacklisted_by_user
            _encode_field("false"), # use_additional_auth
            _encode_field("false"), # cm_api_support
            _encode_field("0"), # created_time
            _encode_field("0"), # modified_time
            _encode_field(entry.get("name", "")), # title
            _encode_field(""), # favicon
            _encode_field("0"), # source_type
            _encode_field(""), # app_name
            _encode_field(""), # package_name
            _encode_field(""), # package_signature
            _encode_field(""),_encode_field(""),_encode_field(""),_encode_field(""), # reserved 1-4
            _encode_field(""),_encode_field(""),_encode_field(""),_encode_field(""), # reserved 5-8
            _encode_field(details.get("notes", "")), # credential_memo
            _encode_field(""), # otp
        ]
        writer.writerow(row)

    content_to_encrypt = output.getvalue().encode("utf-8")
    
    # 2. 加密内容
    salt = os.urandom(20)
    iv = os.urandom(16)
    
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 70000, dklen=32
    )
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    padded_data = pad(content_to_encrypt, AES.block_size, style="pkcs7")
    encrypted_data = cipher.encrypt(padded_data)
    
    # 3. 组合并进行Base64编码
    final_binary_data = salt + iv + encrypted_data
    final_base64_data = base64.b64encode(final_binary_data)
    
    logger.info("Successfully encrypted data for .spass export.")
    return final_base64_data