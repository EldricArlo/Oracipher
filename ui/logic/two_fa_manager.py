# ui/logic/two_fa_manager.py

import logging
import urllib.parse
from typing import Optional

from PyQt6.QtWidgets import QFileDialog, QWidget, QLabel, QPushButton
# --- MODIFICATION START: 导入 QObject ---
from PyQt6.QtCore import QObject, pyqtSignal
# --- MODIFICATION END ---

from PIL import Image
from pyzbar.pyzbar import decode

from ..dialogs.enter_secret_dialog import EnterSecretDialog
from ..dialogs.message_box_dialog import CustomMessageBox
from ..components.screen_qr_reader import ScreenQRReader
from language import t

logger = logging.getLogger(__name__)


# --- MODIFICATION START: 继承 QObject ---
class TwoFAManager(QObject):
# --- MODIFICATION END ---
    scan_finished = pyqtSignal()

    def __init__(
        self,
        parent_widget: QWidget,
        status_label: QLabel,
        scan_file_btn: QPushButton,
        scan_screen_btn: QPushButton,
        manual_key_btn: QPushButton,
        remove_key_btn: QPushButton,
    ):
        # --- MODIFICATION START: 调用 super().__init__() ---
        super().__init__()
        # --- MODIFICATION END ---
        
        self.parent = parent_widget
        self.status_label = status_label
        self.scan_file_btn = scan_file_btn
        self.scan_screen_btn = scan_screen_btn
        self.manual_key_btn = manual_key_btn
        self.remove_key_btn = remove_key_btn
        self.totp_secret: Optional[str] = None
        self.qr_reader: Optional[ScreenQRReader] = None

    def set_initial_secret(self, secret: Optional[str]) -> None:
        self.totp_secret = secret
        if self.totp_secret:
            self.status_label.setText(t.get("2fa_status_enabled"))
        else:
            self.status_label.setText(t.get("2fa_status_not_setup"))
        self._update_button_visibility()

    def open_manual_setup(self) -> None:
        dialog = EnterSecretDialog(self.parent)
        if dialog.exec():
            secret = dialog.get_secret()
            if secret:
                self.totp_secret = secret
                self.status_label.setText(t.get("2fa_status_enabled_pending_save"))
                self._update_button_visibility()

    def clear_secret(self) -> None:
        self.totp_secret = None
        self.status_label.setText(t.get("2fa_status_not_setup"))
        self._update_button_visibility()

    def scan_qr_from_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            t.get("dialog_select_icon"), "",
            f"{t.get('dialog_image_files')} (*.png *.jpg *.jpeg *.bmp *.gif)",
        )
        if not file_path: return
        try:
            image = Image.open(file_path)
            decoded_objects = decode(image)
            if not decoded_objects:
                self._show_qr_error()
                return
            qr_data = decoded_objects[0].data.decode("utf-8")
            self._parse_qr_data(qr_data)
        except Exception as e:
            logger.error(f"Error processing image file for QR scan: {e}", exc_info=True)
            self._show_qr_error()
            
    def start_screen_scan(self) -> None:
        if self.qr_reader is None:
            self.qr_reader = ScreenQRReader()
            self.qr_reader.qr_code_decoded.connect(self._on_screen_qr_decoded)
            self.qr_reader.scan_cancelled.connect(self._on_screen_scan_cancelled)
            self.qr_reader.show()

    def _on_screen_qr_decoded(self, qr_data: str) -> None:
        self._parse_qr_data(qr_data)
        self.scan_finished.emit()
        self.qr_reader = None

    def _on_screen_scan_cancelled(self) -> None:
        self.scan_finished.emit()
        self.qr_reader = None

    def _parse_qr_data(self, qr_data: str) -> None:
        try:
            if qr_data.startswith("otpauth://totp/"):
                parsed_uri = urllib.parse.urlparse(qr_data)
                params = urllib.parse.parse_qs(parsed_uri.query)
                secret = params.get("secret", [None])[0]
                if secret:
                    self.totp_secret = secret.strip().replace(" ", "").upper()
                    self.status_label.setText(t.get("2fa_status_enabled_pending_save"))
                    self._update_button_visibility()
                    return
        except Exception as e:
            logger.error(f"Failed to parse QR code URI: '{qr_data}'. Error: {e}")
        self._show_qr_error()

    def _show_qr_error(self) -> None:
        CustomMessageBox.information(
            self.parent, t.get("error_title_generic"), t.get("2fa_error_invalid_qr")
        )

    def _update_button_visibility(self) -> None:
        has_secret = self.totp_secret is not None
        self.remove_key_btn.setVisible(has_secret)
        self.scan_file_btn.setVisible(not has_secret)
        self.scan_screen_btn.setVisible(not has_secret)
        self.manual_key_btn.setVisible(not has_secret)

    def get_secret(self) -> Optional[str]:
        return self.totp_secret