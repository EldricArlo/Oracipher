# ui/dialogs/add_edit_dialog.py

import base64
import logging
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QFrame, QTextEdit, QWidget,
                             QFileDialog)
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QMouseEvent, QIcon

from language import t
from .generator_dialog import GeneratorWindow
from core.icon_fetcher import IconFetcher
from ui.dialogs.message_box_dialog import CustomMessageBox

logger = logging.getLogger(__name__)

class AddEditDialog(QDialog):
    """
    一个用于添加新条目或编辑现有条目的自定义对话框。
    """
    def __init__(self, parent: Optional[QWidget] = None, entry: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.entry = entry
        self.current_icon_base64: Optional[str] = None
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumSize(480, 580)
        self.drag_pos: QPoint = QPoint()
        self.init_ui()
        if self.entry:
            self.load_entry_data()
            logger.debug(f"AddEditDialog 在 '编辑模式' 下打开，条目: {self.entry.get('name')}")
        else:
            self.current_icon_base64 = IconFetcher.get_default_icon_base64()
            self.update_icon_preview()
            logger.debug("AddEditDialog 在 '添加模式' 下打开。")

    def init_ui(self) -> None:
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        self.icon_preview_button = QPushButton()
        self.icon_preview_button.setFixedSize(64, 64)
        self.icon_preview_button.setIconSize(QSize(48, 48))
        self.icon_preview_button.setObjectName("detailsActionButton")
        self.icon_preview_button.setToolTip(t.get('tooltip_custom_icon'))
        self.icon_preview_button.clicked.connect(self._set_custom_icon)
        
        title_and_name_layout = QVBoxLayout()
        title_text = t.get('edit_title') if self.entry else t.get('add_title')
        title_label = QLabel(title_text)
        title_label.setObjectName("dialogTitle")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(t.get('placeholder_name'))
        
        title_and_name_layout.addWidget(title_label)
        title_and_name_layout.addWidget(self.name_input)

        header_layout.addWidget(self.icon_preview_button)
        header_layout.addLayout(title_and_name_layout)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(t.get('placeholder_user'))
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(t.get('placeholder_url'))

        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(10)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        show_hide_button = QPushButton(t.get('button_show'))
        show_hide_button.setObjectName("inlineButton")
        show_hide_button.setCheckable(True)
        show_hide_button.toggled.connect(self._toggle_password_visibility)

        generate_button = QPushButton(t.get('button_generate'))
        generate_button.setObjectName("inlineButton")
        generate_button.clicked.connect(self._open_generator)
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(show_hide_button)
        password_layout.addWidget(generate_button)
        
        icon_actions_layout = QHBoxLayout()
        icon_actions_layout.setContentsMargins(0,0,0,0)
        fetch_icon_button = QPushButton(t.get('button_fetch_icon'))
        fetch_icon_button.setObjectName("inlineButton")
        fetch_icon_button.clicked.connect(self._fetch_icon)
        
        custom_icon_button = QPushButton(t.get('button_custom_icon'))
        custom_icon_button.setObjectName("inlineButton")
        custom_icon_button.clicked.connect(self._set_custom_icon)

        icon_actions_layout.addWidget(fetch_icon_button)
        icon_actions_layout.addWidget(custom_icon_button)
        icon_actions_layout.addStretch()

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText(t.get('placeholder_cat'))
        self.notes_input = QTextEdit()
        self.notes_input.setFixedHeight(80)

        form_layout.addWidget(QLabel(t.get('label_user')), 0, 0)
        form_layout.addWidget(self.username_input, 0, 1)
        form_layout.addWidget(QLabel(t.get('label_url')), 1, 0)
        form_layout.addWidget(self.url_input, 1, 1)
        form_layout.addLayout(icon_actions_layout, 2, 1)
        form_layout.addWidget(QLabel(t.get('label_pass')), 3, 0)
        form_layout.addLayout(password_layout, 3, 1)
        form_layout.addWidget(QLabel(t.get('label_cat')), 4, 0)
        form_layout.addWidget(self.category_input, 4, 1)
        form_layout.addWidget(QLabel(t.get('label_notes')), 5, 0)
        form_layout.addWidget(self.notes_input, 5, 1)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_button = QPushButton(t.get('button_cancel'))
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = QPushButton(t.get('button_save'))
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(header_layout)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)

    def _open_generator(self) -> None:
        gen_dialog = GeneratorWindow(self)
        if gen_dialog.exec():
            generated_password = gen_dialog.get_password()
            if generated_password != t.get('gen_no_charset'):
                self.password_input.setText(generated_password)
                logger.debug("已使用生成器生成并填充了新密码。")

    def _toggle_password_visibility(self, checked: bool) -> None:
        button = self.sender()
        if isinstance(button, QPushButton):
            if checked:
                self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
                button.setText(t.get('button_hide'))
            else:
                self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
                button.setText(t.get('button_show'))
    
    def update_icon_preview(self) -> None:
        icon = IconFetcher.icon_from_base64(self.current_icon_base64)
        self.icon_preview_button.setIcon(icon)

    def _fetch_icon(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            CustomMessageBox.information(self, t.get('msg_title_input_error'), t.get('error_url_required'))
            return
        logger.info(f"正在从 '{url}' 获取图标...")
        fetched_icon_base64 = IconFetcher.fetch_icon_from_url(url)
        if fetched_icon_base64:
            self.current_icon_base64 = fetched_icon_base64
            logger.info("图标获取成功。")
        else:
            logger.warning("图标获取失败。")
            CustomMessageBox.information(self, t.get('msg_title_pass_change_fail'), t.get('error_fetch_failed'))
        self.update_icon_preview()
        
    def _set_custom_icon(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t.get('dialog_select_icon'),
            "",
            f"{t.get('dialog_image_files')} (*.png *.jpg *.ico *.svg)"
        )
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    self.current_icon_base64 = base64.b64encode(file_data).decode('utf-8')
                    self.update_icon_preview()
                    logger.info(f"已设置自定义图标: {file_path}")
            except Exception as e:
                logger.error(f"加载自定义图标失败: {e}", exc_info=True)
                CustomMessageBox.information(self, t.get('error_title_generic'), t.get('error_loading_icon'))

    def load_entry_data(self) -> None:
        if not self.entry:
            return
        details = self.entry.get("details", {})
        self.name_input.setText(self.entry.get("name", ""))
        self.category_input.setText(self.entry.get("category", ""))
        self.username_input.setText(details.get("username", ""))
        self.password_input.setText(details.get("password", ""))
        self.notes_input.setText(details.get("notes", ""))
        self.url_input.setText(details.get("url", ""))
        self.current_icon_base64 = details.get("icon_data")
        if not self.current_icon_base64:
            self.current_icon_base64 = IconFetcher.get_default_icon_base64()
        self.update_icon_preview()

    def get_data(self) -> Dict[str, Any]:
        return {
            "category": self.category_input.text().strip(),
            "name": self.name_input.text().strip(),
            "details": {
                "username": self.username_input.text().strip(),
                "password": self.password_input.text(),
                "notes": self.notes_input.toPlainText().strip(),
                "url": self.url_input.text().strip(),
                "icon_data": self.current_icon_base64
            },
        }

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()