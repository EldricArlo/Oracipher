# ui/dialogs/add_edit_dialog.py

import logging
import base64
from typing import Optional, Dict, Any, Tuple

from PyQt6.QtWidgets import QDialog, QLineEdit, QWidget, QFileDialog, QMainWindow
from PyQt6.QtCore import Qt, QPoint, QTimer
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
        self, parent: QMainWindow, entry: Optional[Dict[str, Any]] = None
    ):
        super().__init__(parent)
        self.entry = entry
        self.new_category_icon_data: Optional[Tuple[str, str]] = None
        
        # --- MODIFICATION START: Store a reference to the main window ---
        self.main_window = parent 
        # --- MODIFICATION END ---

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumSize(520, 620) 
        self.drag_pos: QPoint = QPoint()

        self.ui = AddEditDialogUI.setup_ui(self)

        self.init_logic_managers()
        self._connect_signals()
        self.load_entry_data()

    def init_logic_managers(self) -> None:
        self.icon_manager = IconManager(
            parent_widget=self,
            icon_preview_button=self.ui.icon_preview_button,
            url_input=self.ui.url_input,
        )
        self.two_fa_manager = TwoFAManager(
            parent_widget=self,
            status_label=self.ui.two_fa_status_label,
            scan_file_btn=self.ui.scan_file_btn,
            scan_screen_btn=self.ui.scan_screen_btn,
            manual_key_btn=self.ui.manual_key_btn,
            remove_key_btn=self.ui.remove_key_btn,
        )

    def _connect_signals(self) -> None:
        self.ui.icon_preview_button.clicked.connect(self.icon_manager.select_icon_from_file)
        self.ui.show_hide_btn.toggled.connect(self._toggle_password_visibility)
        self.ui.generate_btn.clicked.connect(self._open_generator)
        self.ui.fetch_icon_btn.clicked.connect(self.icon_manager.fetch_icon_from_url)
        self.ui.set_cat_icon_btn.clicked.connect(self._set_category_icon)
        
        self.ui.scan_file_btn.clicked.connect(self.two_fa_manager.scan_qr_from_file)
        
        self.ui.scan_screen_btn.clicked.connect(self._start_screen_scan_flow)
        self.two_fa_manager.scan_finished.connect(self._finish_screen_scan_flow)
        
        self.ui.manual_key_btn.clicked.connect(self.two_fa_manager.open_manual_setup)
        
        self.ui.remove_key_btn.clicked.connect(self.two_fa_manager.clear_secret)
        self.ui.cancel_btn.clicked.connect(self.reject)
        self.ui.save_btn.clicked.connect(self.accept)

    # --- MODIFICATION START: Orchestrate main window and dialog visibility ---
    def _start_screen_scan_flow(self):
        """最小化主窗口，隐藏此对话框，然后启动屏幕扫描。"""
        if self.main_window:
            self.main_window.showMinimized()
        
        self.hide()
        self.two_fa_manager.start_screen_scan()

    def _finish_screen_scan_flow(self):
        """恢复主窗口，然后显示此对话框。"""
        if self.main_window:
            # 恢复主窗口到正常状态并激活它
            self.main_window.showNormal()
            self.main_window.activateWindow()

        # 重新显示此对话框
        self.show()
        self.activateWindow()
    # --- MODIFICATION END ---

    def load_entry_data(self) -> None:
        if not self.entry:
            self.icon_manager.set_initial_icon(None)
            self.two_fa_manager.set_initial_secret(None)
            return
        details = self.entry.get("details", {})
        self.ui.name_input.setText(self.entry.get("name", ""))
        self.ui.category_input.setText(self.entry.get("category", ""))
        self.ui.username_input.setText(details.get("username", ""))
        self.ui.email_input.setText(details.get("email", ""))
        self.ui.password_input.setText(details.get("password", ""))
        self.ui.url_input.setText(details.get("url", ""))
        self.ui.backup_codes_input.setText(details.get("backup_codes", ""))
        self.ui.notes_input.setText(details.get("notes", ""))
        self.icon_manager.set_initial_icon(details.get("icon_data"))
        self.two_fa_manager.set_initial_secret(details.get("totp_secret"))

    def _toggle_password_visibility(self, checked: bool) -> None:
        self.ui.password_input.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        self.ui.show_hide_btn.setText(
            t.get("button_hide") if checked else t.get("button_show")
        )

    def _open_generator(self) -> None:
        gen_dialog = GeneratorWindow(self)
        if gen_dialog.exec():
            password = gen_dialog.get_password()
            if password != t.get("gen_no_charset"):
                self.ui.password_input.setText(password)

    def _set_category_icon(self) -> None:
        category_name = self.ui.category_input.text().strip()
        if not category_name:
            CustomMessageBox.information(
                self, t.get("msg_title_input_error"), t.get("error_cat_name_required")
            )
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t.get("dialog_select_cat_icon"),"",
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
        backup_codes_str = self.ui.backup_codes_input.toPlainText()
        notes_str = self.ui.notes_input.toPlainText()
        return {
            "category": self.ui.category_input.text().strip(),
            "name": self.ui.name_input.text().strip(),
            "details": {
                "username": self.ui.username_input.text().strip(),
                "email": self.ui.email_input.text().strip(),
                "password": self.ui.password_input.text(),
                "notes": notes_str,
                "url": self.ui.url_input.text().strip(),
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