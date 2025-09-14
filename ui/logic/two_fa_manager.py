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
    # --- MODIFICATION START ---
    def __init__(
        self,
        parent_widget: QWidget,
        status_label: QLabel,
        scan_qr_btn: QPushButton,
        enter_key_btn: QPushButton,
        remove_key_btn: QPushButton
    ):
        self.parent = parent_widget
        self.status_label = status_label
        self.scan_qr_btn = scan_qr_btn
        self.enter_key_btn = enter_key_btn
        self.remove_key_btn = remove_key_btn
        self.totp_secret: Optional[str] = None
    # --- MODIFICATION END ---

    def set_initial_secret(self, secret: Optional[str]) -> None:
        self.totp_secret = secret
        if self.totp_secret:
            self.status_label.setText(t.get('2fa_status_enabled'))
        else:
            self.status_label.setText(t.get('2fa_status_not_setup'))
        # --- MODIFICATION START ---
        self._update_button_visibility()
        # --- MODIFICATION END ---

    def open_manual_setup(self) -> None:
        dialog = EnterSecretDialog(self.parent)
        if dialog.exec():
            secret = dialog.get_secret()
            if secret:
                self.totp_secret = secret
                self.status_label.setText(t.get('2fa_status_enabled_pending_save'))
                logger.info("New 2FA secret has been set manually.")
                # --- MODIFICATION START ---
                self._update_button_visibility()
                # --- MODIFICATION END ---
            else:
                pass

    def clear_secret(self) -> None:
        """清除当前的TOTP密钥。"""
        self.totp_secret = None
        self.status_label.setText(t.get('2fa_status_not_setup'))
        logger.info("2FA secret has been cleared by user.")
        # --- MODIFICATION START ---
        self._update_button_visibility()
        # --- MODIFICATION END ---

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
                    logger.info("Successfully set 2FA secret from image file.")
                    # --- MODIFICATION START ---
                    self._update_button_visibility()
                    # --- MODIFICATION END ---
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

    # --- MODIFICATION START ---
    def _update_button_visibility(self) -> None:
        """根据是否存在密钥来更新按钮的可见性。"""
        has_secret = self.totp_secret is not None
        self.remove_key_btn.setVisible(has_secret)
        self.scan_qr_btn.setVisible(not has_secret)
        self.enter_key_btn.setVisible(not has_secret)
    # --- MODIFICATION END ---

    def get_secret(self) -> Optional[str]:
        return self.totp_secret