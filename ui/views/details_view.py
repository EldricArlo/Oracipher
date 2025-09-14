# ui/views/details_view.py

import logging
from typing import Dict, Any, Optional, List

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QTextEdit, 
                             QTabWidget, QLayout)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal

from language import t
from utils import clipboard_manager, icon_cache
from core.icon_fetcher import IconFetcher
from ..components.two_fa_widget import TwoFAWidget

logger = logging.getLogger(__name__)

class DetailsView(QWidget):
    """
    详情视图，用于展示一个或多个同名账户的详细信息。
    """
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_entry_group: List[Dict[str, Any]] = []
        self.active_entry_in_group: Optional[Dict[str, Any]] = None
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.clear_details()

    def display_entry_group(self, entries: List[Dict[str, Any]]) -> None:
        if not entries:
            self.clear_details()
            return
            
        self.current_entry_group = sorted(entries, key=lambda x: x.get('details', {}).get('username', ''))
        self._clear_layout_widgets()
        self.main_layout.setSpacing(15)
        
        representative_entry = self.current_entry_group[0]
        self.main_layout.addLayout(self._create_shared_header(representative_entry))

        if len(self.current_entry_group) == 1:
            self.active_entry_in_group = self.current_entry_group[0]
            details_tabs = self._create_details_widget_for_entry(self.active_entry_in_group)
            self.main_layout.addWidget(details_tabs, 1)
        else:
            account_tabs = QTabWidget()
            for entry in self.current_entry_group:
                details_widget = self._create_details_widget_for_entry(entry)
                username = entry.get('details', {}).get('username', f"Account ID: {entry['id']}")
                account_tabs.addTab(details_widget, username)
            
            account_tabs.currentChanged.connect(self._on_account_tab_changed)
            self._on_account_tab_changed(0)
            self.main_layout.addWidget(account_tabs, 1)

    def retranslate_ui(self) -> None:
        if self.current_entry_group:
            self.display_entry_group(self.current_entry_group)
        else:
            self.clear_details()

    def _on_account_tab_changed(self, index: int) -> None:
        if 0 <= index < len(self.current_entry_group):
            self.active_entry_in_group = self.current_entry_group[index]

    def _create_shared_header(self, entry: Dict[str, Any]) -> QHBoxLayout:
        header_layout = QHBoxLayout(); header_layout.setSpacing(15)
        icon_label = QLabel(); icon_label.setFixedSize(52, 52); icon_label.setScaledContents(True)
        pixmap = IconFetcher.pixmap_from_base64(entry.get("details", {}).get("icon_data"))
        icon_label.setPixmap(pixmap)
        name_label = QLabel(str(entry.get("name", ""))); name_label.setObjectName("detailsNameLabel"); name_label.setWordWrap(True)
        header_layout.addWidget(icon_label); header_layout.addWidget(name_label); header_layout.addStretch()
        edit_button = self._create_action_button("detailsActionButton", "edit", t.get('button_edit_icon'))
        delete_button = self._create_action_button("detailsActionButton", "delete", t.get('button_delete_icon'))
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.active_entry_in_group['id']) if self.active_entry_in_group else None)
        delete_button.clicked.connect(lambda: self.delete_requested.emit(self.active_entry_in_group['id']) if self.active_entry_in_group else None)
        header_layout.addWidget(edit_button); header_layout.addSpacing(10); header_layout.addWidget(delete_button)
        return header_layout
    
    def _create_action_button(self, obj_name: str, icon_key: str, tooltip: str) -> QPushButton:
        button = QPushButton(); button.setObjectName(obj_name); button.setFixedSize(40, 40)
        button.setIcon(icon_cache.get(icon_key)); button.setIconSize(QSize(22, 22)); button.setToolTip(tooltip)
        return button

    def _create_details_widget_for_entry(self, entry: Dict[str, Any]) -> QWidget:
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        tabs = QTabWidget()
        main_tab, advanced_tab = QWidget(), QWidget()
        tabs.addTab(main_tab, t.get('tab_main')); tabs.addTab(advanced_tab, t.get('tab_advanced'))
        container_layout.addWidget(tabs)
        
        main_layout = QVBoxLayout(main_tab); main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(15); main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        details = entry.get("details", {})
        if details.get("username"): main_layout.addWidget(self._create_detail_field(t.get('label_user'), details["username"]))
        if details.get("email"): main_layout.addWidget(self._create_detail_field(t.get('label_email'), details["email"]))
        if details.get("password"): main_layout.addWidget(self._create_detail_field(t.get('label_pass'), details["password"], is_password=True))
        if details.get("url"): main_layout.addWidget(self._create_detail_field(t.get('label_url'), details["url"]))
        if details.get("totp_secret"): main_layout.addWidget(self._create_2fa_field(details["totp_secret"]))
        main_layout.addStretch()
        
        adv_layout = QVBoxLayout(advanced_tab); adv_layout.setContentsMargins(0, 15, 0, 0)
        adv_layout.setSpacing(15); adv_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        has_advanced_info = False
        if details.get("backup_codes"):
            has_advanced_info = True
            adv_layout.addWidget(self._create_detail_field(t.get('label_backup_codes'), details["backup_codes"], multiline=True))
        if details.get("notes"):
            has_advanced_info = True
            adv_layout.addWidget(self._create_detail_field(t.get('label_notes'), details["notes"], multiline=True))
        
        tabs.setTabVisible(1, has_advanced_info)
        adv_layout.addStretch()
        
        return container

    def _create_detail_field(self, title: str, value: str, is_password: bool = False, multiline: bool = False) -> QFrame:
        field_frame = QFrame(); field_frame.setObjectName("detailField")
        layout = QVBoxLayout(field_frame)
        title_label = QLabel(title); title_label.setObjectName("fieldTitleLabel")
        value_layout = QHBoxLayout()
        value_display: QLineEdit | QTextEdit
        
        if multiline:
            value_display = QTextEdit(value)
            value_display.setReadOnly(True)
            value_display.setObjectName("fieldValueDisplay")
            # 修正: 移除所有手动调整高度的逻辑
        else:
            value_display = QLineEdit(value)
            value_display.setReadOnly(True)
            value_display.setObjectName("fieldValueDisplay")
            if is_password: value_display.setEchoMode(QLineEdit.EchoMode.Password)
        
        value_layout.addWidget(value_display, 1)
        
        if is_password:
            show_hide_btn = QPushButton(t.get('button_show')); show_hide_btn.setObjectName("inlineButton"); show_hide_btn.setCheckable(True)
            show_hide_btn.toggled.connect(lambda checked, v=value_display, b=show_hide_btn: self._toggle_password_visibility(checked, v, b))
            value_layout.addWidget(show_hide_btn)
        
        copy_btn = QPushButton(t.get('button_copy')); copy_btn.setObjectName("inlineButton")
        is_sensitive = is_password or title == t.get('label_backup_codes')
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(value, copy_btn, is_sensitive))
        value_layout.addWidget(copy_btn)
        
        layout.addWidget(title_label); layout.addLayout(value_layout)
        return field_frame

    def _create_2fa_field(self, secret: str) -> QFrame:
        field_frame = QFrame(); field_frame.setObjectName("detailField")
        layout = QVBoxLayout(field_frame)
        title_label = QLabel(t.get('label_2fa_code')); title_label.setObjectName("fieldTitleLabel")
        two_fa_widget = TwoFAWidget(secret)
        layout.addWidget(title_label); layout.addWidget(two_fa_widget)
        return field_frame

    def clear_details(self) -> None:
        self.current_entry_group = []
        self.active_entry_in_group = None
        self._clear_layout_widgets()
        placeholder = QLabel(t.get('details_placeholder'))
        placeholder.setObjectName("placeholderLabel")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(placeholder, 1, Qt.AlignmentFlag.AlignCenter)

    def _toggle_password_visibility(self, checked: bool, display_widget: QLineEdit, button: QPushButton) -> None:
        display_widget.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
        button.setText(t.get('button_hide') if checked else t.get('button_show'))

    def _copy_to_clipboard(self, text: str, button: QPushButton, is_sensitive: bool) -> None:
        clipboard_manager.copy(text, is_sensitive=is_sensitive)
        original_text = button.text()
        button.setText(t.get('button_copied')); button.setEnabled(False)
        QTimer.singleShot(1500, lambda: (button.setText(original_text), button.setEnabled(True)))

    def _clear_layout_widgets(self) -> None:
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_recursive(child.layout())
    
    def _clear_recursive(self, layout: QLayout) -> None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_recursive(child.layout())

    # 移除不再使用的方法
    # def _adjust_textedit_height(...)