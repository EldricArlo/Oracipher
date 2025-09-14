# ui/logic/two_fa_manager.py

import logging
import urllib.parse
from typing import Optional, TYPE_CHECKING

from PyQt6.QtWidgets import QFileDialog, QWidget, QLabel, QPushButton

from PIL import Image
from pyzbar.pyzbar import decode

from ..dialogs.enter_secret_dialog import EnterSecretDialog
from ..dialogs.message_box_dialog import CustomMessageBox
from language import t

logger = logging.getLogger(__name__)

class TwoFAManager:
    """
    负责处理添加/编辑对话框中所有与两步验证(2FA/TOTP)相关的逻辑。
    """
    def __init__(
        self,
        parent_widget: QWidget,
        status_label: QLabel,
        remove_key_btn: QPushButton  # 修改: 接收移除按钮
    ):
        self.parent = parent_widget
        self.status_label = status_label
        self.remove_key_btn = remove_key_btn # 修改: 保存移除按钮的引用
        self.totp_secret: Optional[str] = None

    def set_initial_secret(self, secret: Optional[str]) -> None:
        self.totp_secret = secret
        if self.totp_secret:
            self.status_label.setText(t.get('2fa_status_enabled'))
            self.remove_key_btn.setVisible(True) # 修改: 如果有密钥则显示移除按钮
        else:
            self.status_label.setText(t.get('2fa_status_not_setup'))
            self.remove_key_btn.setVisible(False) # 修改: 如果没有密钥则隐藏移除按钮

    def open_manual_setup(self) -> None:
        dialog = EnterSecretDialog(self.parent)
        if dialog.exec():
            secret = dialog.get_secret()
            if secret:
                self.totp_secret = secret
                self.status_label.setText(t.get('2fa_status_enabled_pending_save'))
                self.remove_key_btn.setVisible(True) # 修改: 设置新密钥后显示移除按钮
                logger.info("New 2FA secret has been set manually.")
            else:
                # 用户可能在对话框中清空了密钥，这里我们不做任何事，保留原有密钥
                # 只有clear_secret才能清空
                pass

    # 新增: 清除密钥的逻辑
    def clear_secret(self) -> None:
        """清除当前的TOTP密钥。"""
        self.totp_secret = None
        self.status_label.setText(t.get('2fa_status_not_setup'))
        self.remove_key_btn.setVisible(False)
        logger.info("2FA secret has been cleared by user.")

    def scan_qr_from_file(self) -> None:
        """
        打开文件对话框，让用户选择一个图像文件，并尝试从中解码二维码。
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            t.get('dialog_select_icon'), 
            "",
            f"{t.get('dialog_image_files')} (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if not file_path:
            return

        try:
            image = Image.open(file_path)
            decoded_objects = decode(image)

            if not decoded_objects:
                self._show_qr_error()
                return

            qr_data = decoded_objects[0].data.decode('utf-8')
            self._parse_qr_data(qr_data)

        except Exception as e:
            logger.error(f"Error processing image file for QR scan: {e}", exc_info=True)
            self._show_qr_error()

    def _parse_qr_data(self, qr_data: str) -> None:
        """
        解析从二维码中获取的数据，提取TOTP密钥。
        """
        try:
            if qr_data.startswith("otpauth://totp/"):
                parsed_uri = urllib.parse.urlparse(qr_data)
                params = urllib.parse.parse_qs(parsed_uri.query)
                secret = params.get('secret', [None])[0]
                
                if secret:
                    self.totp_secret = secret.strip().replace(" ", "").upper()
                    self.status_label.setText(t.get('2fa_status_enabled_pending_save'))
                    self.remove_key_btn.setVisible(True) # 修改: 从QR码设置后显示移除按钮
                    logger.info("Successfully set 2FA secret from image file.")
                    return
        except Exception as e:
            logger.error(f"Failed to parse QR code URI: '{qr_data}'. Error: {e}")

        logger.warning(f"Scanned data is not a valid otpauth URI: '{qr_data}'")
        self._show_qr_error()

    def _show_qr_error(self) -> None:
        """显示一个统一的二维码扫描错误信息。"""
        CustomMessageBox.information(
            self.parent,
            t.get('error_title_generic'),
            t.get('2fa_error_invalid_qr')
        )

    def get_secret(self) -> Optional[str]:
        return self.totp_secret