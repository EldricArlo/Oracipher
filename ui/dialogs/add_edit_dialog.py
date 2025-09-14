# ui/dialogs/add_edit_dialog.py

import logging
import re
import base64
from typing import Optional, Dict, Any, Tuple

from PyQt6.QtWidgets import (
    QDialog,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QTabWidget,
    QWidget,
    QLabel,
    QFileDialog,
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent

from language import t
from .generator_dialog import GeneratorWindow
from .message_box_dialog import CustomMessageBox
from ..logic.icon_manager import IconManager
from ..logic.two_fa_manager import TwoFAManager
from .add_edit_dialog_ui import AddEditDialogUI

logger = logging.getLogger(__name__)


class AddEditDialog(QDialog):
    """
    用于添加或编辑密码条目的对话框。
    """

    def __init__(
        self, parent: Optional[QWidget] = None, entry: Optional[Dict[str, Any]] = None
    ):
        super().__init__(parent)
        self.entry = entry
        self.new_category_icon_data: Optional[Tuple[str, str]] = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumSize(520, 620)
        self.drag_pos: QPoint = QPoint()

        self.icon_preview_button: QPushButton
        self.name_input: QLineEdit
        self.tabs: QTabWidget
        self.cancel_btn: QPushButton
        self.save_btn: QPushButton
        self.username_input: QLineEdit
        self.email_input: QLineEdit
        self.password_input: QLineEdit
        self.url_input: QLineEdit
        self.category_input: QLineEdit
        self.show_hide_btn: QPushButton
        self.generate_btn: QPushButton
        self.fetch_icon_btn: QPushButton
        self.set_cat_icon_btn: QPushButton
        self.backup_codes_input: QTextEdit
        self.notes_input: QTextEdit
        self.two_fa_status_label: QLabel
        self.scan_qr_btn: QPushButton
        self.enter_key_btn: QPushButton
        self.remove_key_btn: QPushButton

        ui_builder = AddEditDialogUI()
        ui_builder.setup_ui(self)

        self.init_logic_managers()
        self._connect_signals()
        self.load_entry_data()

    def init_logic_managers(self) -> None:
        self.icon_manager = IconManager(
            parent_widget=self,
            icon_preview_button=self.icon_preview_button,
            url_input=self.url_input,
        )
        self.two_fa_manager = TwoFAManager(
            parent_widget=self,
            status_label=self.two_fa_status_label,
            scan_qr_btn=self.scan_qr_btn,
            enter_key_btn=self.enter_key_btn,
            remove_key_btn=self.remove_key_btn,
        )

    def _connect_signals(self) -> None:
        self.icon_preview_button.clicked.connect(
            self.icon_manager.select_icon_from_file
        )
        self.show_hide_btn.toggled.connect(self._toggle_password_visibility)
        self.generate_btn.clicked.connect(self._open_generator)
        self.fetch_icon_btn.clicked.connect(self.icon_manager.fetch_icon_from_url)
        self.set_cat_icon_btn.clicked.connect(self._set_category_icon)
        self.scan_qr_btn.clicked.connect(self.two_fa_manager.scan_qr_from_file)
        self.enter_key_btn.clicked.connect(self.two_fa_manager.open_manual_setup)
        self.remove_key_btn.clicked.connect(self.two_fa_manager.clear_secret)
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.accept)

    def load_entry_data(self) -> None:
        if not self.entry:
            self.icon_manager.set_initial_icon(None)
            self.two_fa_manager.set_initial_secret(None)
            return

        details = self.entry.get("details", {})
        self.name_input.setText(self.entry.get("name", ""))
        self.category_input.setText(self.entry.get("category", ""))
        self.username_input.setText(details.get("username", ""))
        self.email_input.setText(details.get("email", ""))
        self.password_input.setText(details.get("password", ""))
        self.url_input.setText(details.get("url", ""))
        
        # --- MODIFICATION START: Directly set text without any conversion ---
        self.backup_codes_input.setText(details.get("backup_codes", ""))
        self.notes_input.setText(details.get("notes", ""))
        # --- MODIFICATION END ---

        self.icon_manager.set_initial_icon(details.get("icon_data"))
        self.two_fa_manager.set_initial_secret(details.get("totp_secret"))

    def _toggle_password_visibility(self, checked: bool) -> None:
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        self.show_hide_btn.setText(
            t.get("button_hide") if checked else t.get("button_show")
        )

    def _open_generator(self) -> None:
        gen_dialog = GeneratorWindow(self)
        if gen_dialog.exec():
            password = gen_dialog.get_password()
            if password != t.get("gen_no_charset"):
                self.password_input.setText(password)

    def _set_category_icon(self) -> None:
        category_name = self.category_input.text().strip()
        if not category_name:
            CustomMessageBox.information(
                self, t.get("msg_title_input_error"), t.get("error_cat_name_required")
            )
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t.get("dialog_select_cat_icon"),
            "",
            f"{t.get('dialog_image_files')} (*.png *.jpg *.jpeg *.ico *.svg)",
        )
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    icon_base64 = base64.b64encode(f.read()).decode("utf-8")
                    self.new_category_icon_data = (category_name, icon_base64)
                    CustomMessageBox.information(
                        self,
                        t.get("info_title_cat_icon_set"),
                        t.get("info_msg_cat_icon_set", name=category_name),
                    )
            except Exception as e:
                logger.error(f"Failed to load category icon: {e}", exc_info=True)
                CustomMessageBox.information(
                    self, t.get("error_title_generic"), t.get("error_loading_icon")
                )
    
    def get_data(self) -> Dict[str, Any]:
        # --- MODIFICATION START: Directly get plain text without any conversion ---
        backup_codes_str = self.backup_codes_input.toPlainText()
        notes_str = self.notes_input.toPlainText()
        # --- MODIFICATION END ---

        return {
            "category": self.category_input.text().strip(),
            "name": self.name_input.text().strip(),
            "details": {
                "username": self.username_input.text().strip(),
                "email": self.email_input.text().strip(),
                "password": self.password_input.text(),
                "notes": notes_str,
                "url": self.url_input.text().strip(),
                "icon_data": self.icon_manager.get_icon_data(),
                "totp_secret": self.two_fa_manager.get_secret(),
                "backup_codes": backup_codes_str,
            },
        }

    def mousePressEvent(self, a0: Optional[QMouseEvent]) -> None:
        if a0 and a0.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = a0.globalPosition().toPoint()
            a0.accept()

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        if a0 and a0.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + a0.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = a0.globalPosition().toPoint()
            a0.accept()