# ui/dialogs/add_edit_dialog_ui.py

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTextEdit, QWidget, QTabWidget
)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon

from language import t
from utils.paths import resource_path

if TYPE_CHECKING:
    from ui.dialogs.add_edit_dialog import AddEditDialog

@dataclass
class UIData:
    """一个数据类，用于容纳由UI构建器创建的所有UI小部件。"""
    icon_preview_button: QPushButton = field(default_factory=QPushButton)
    name_input: QLineEdit = field(default_factory=QLineEdit)
    tabs: QTabWidget = field(default_factory=QTabWidget)
    cancel_btn: QPushButton = field(default_factory=QPushButton)
    save_btn: QPushButton = field(default_factory=QPushButton)
    username_input: QLineEdit = field(default_factory=QLineEdit)
    email_input: QLineEdit = field(default_factory=QLineEdit)
    password_input: QLineEdit = field(default_factory=QLineEdit)
    url_input: QLineEdit = field(default_factory=QLineEdit)
    category_input: QLineEdit = field(default_factory=QLineEdit)
    show_hide_btn: QPushButton = field(default_factory=QPushButton)
    generate_btn: QPushButton = field(default_factory=QPushButton)
    fetch_icon_btn: QPushButton = field(default_factory=QPushButton)
    set_cat_icon_btn: QPushButton = field(default_factory=QPushButton)
    backup_codes_input: QTextEdit = field(default_factory=QTextEdit)
    notes_input: QTextEdit = field(default_factory=QTextEdit)
    two_fa_status_label: QLabel = field(default_factory=QLabel)
    scan_file_btn: QPushButton = field(default_factory=QPushButton)
    scan_screen_btn: QPushButton = field(default_factory=QPushButton)
    manual_key_btn: QPushButton = field(default_factory=QPushButton)
    remove_key_btn: QPushButton = field(default_factory=QPushButton)


class AddEditDialogUI:
    """此类专门负责构建 AddEditDialog 的UI组件和布局。"""

    @staticmethod
    def setup_ui(dialog_instance: "AddEditDialog") -> UIData:
        ui = UIData()
        container = QFrame(dialog_instance)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)
        header_layout = AddEditDialogUI._create_header_layout(dialog_instance, ui)
        AddEditDialogUI._create_tabs(ui)
        button_layout = AddEditDialogUI._create_button_layout(ui)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(ui.tabs)
        main_layout.addLayout(button_layout)
        dialog_layout = QVBoxLayout(dialog_instance)
        dialog_layout.addWidget(container)
        return ui
    
    # ... ( _create_header_layout, _create_tabs, _populate_main_tab, etc. a-re unchanged ) ...
    @staticmethod
    def _create_header_layout(d: "AddEditDialog", ui: UIData) -> QHBoxLayout:
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        ui.icon_preview_button.setFixedSize(64, 64)
        ui.icon_preview_button.setIconSize(QSize(48, 48))
        ui.icon_preview_button.setObjectName("detailsActionButton")
        ui.icon_preview_button.setToolTip(t.get("tooltip_custom_icon"))
        title_and_name_layout = QVBoxLayout()
        title_text = t.get("edit_title") if d.entry else t.get("add_title")
        title_label = QLabel(title_text)
        title_label.setObjectName("dialogTitle")
        ui.name_input.setPlaceholderText(t.get("placeholder_name"))
        title_and_name_layout.addWidget(title_label)
        title_and_name_layout.addWidget(ui.name_input)
        header_layout.addWidget(ui.icon_preview_button)
        header_layout.addLayout(title_and_name_layout)
        return header_layout

    @staticmethod
    def _create_tabs(ui: UIData) -> None:
        main_tab, advanced_tab = QWidget(), QWidget()
        ui.tabs.addTab(main_tab, t.get("tab_main"))
        ui.tabs.addTab(advanced_tab, t.get("tab_advanced"))
        AddEditDialogUI._populate_main_tab(ui, main_tab)
        AddEditDialogUI._populate_advanced_tab(ui, advanced_tab)

    @staticmethod
    def _populate_main_tab(ui: UIData, parent_tab: QWidget) -> None:
        layout = QGridLayout(parent_tab)
        layout.setSpacing(15)
        ui.username_input.setPlaceholderText(t.get("placeholder_user"))
        ui.email_input.setPlaceholderText(t.get("placeholder_email"))
        ui.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        ui.url_input.setPlaceholderText(t.get("placeholder_url"))
        ui.category_input.setPlaceholderText(t.get("placeholder_cat"))
        layout.addWidget(QLabel(t.get("label_user")), 0, 0)
        layout.addWidget(ui.username_input, 0, 1)
        layout.addWidget(QLabel(t.get("label_email")), 1, 0)
        layout.addWidget(ui.email_input, 1, 1)
        layout.addWidget(QLabel(t.get("label_pass")), 2, 0)
        layout.addLayout(AddEditDialogUI._create_password_layout(ui), 2, 1)
        layout.addWidget(QLabel(t.get("label_url")), 3, 0)
        layout.addLayout(AddEditDialogUI._create_url_layout(ui), 3, 1)
        layout.addWidget(QLabel(t.get("label_cat")), 4, 0)
        layout.addLayout(AddEditDialogUI._create_category_layout(ui), 4, 1)
        layout.setRowStretch(5, 1)

    @staticmethod
    def _create_password_layout(ui: UIData) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        ui.show_hide_btn.setText(t.get("button_show"))
        ui.show_hide_btn.setObjectName("inlineButton")
        ui.show_hide_btn.setCheckable(True)
        ui.generate_btn.setText(t.get("button_generate"))
        ui.generate_btn.setObjectName("inlineButton")
        layout.addWidget(ui.password_input)
        layout.addWidget(ui.show_hide_btn)
        layout.addWidget(ui.generate_btn)
        return layout

    @staticmethod
    def _create_url_layout(ui: UIData) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        ui.fetch_icon_btn.setText(t.get("button_fetch_icon"))
        ui.fetch_icon_btn.setObjectName("inlineButton")
        layout.addWidget(ui.url_input)
        layout.addWidget(ui.fetch_icon_btn)
        return layout

    @staticmethod
    def _create_category_layout(ui: UIData) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        ui.set_cat_icon_btn.setObjectName("inlineButton")
        ui.set_cat_icon_btn.setIcon(QIcon(str(resource_path("ui/assets/icons/edit.svg"))))
        ui.set_cat_icon_btn.setToolTip(t.get("tooltip_set_cat_icon"))
        layout.addWidget(ui.category_input)
        layout.addWidget(ui.set_cat_icon_btn)
        return layout

    # --- MODIFICATION START ---
    @staticmethod
    def _populate_advanced_tab(ui: UIData, parent_tab: QWidget) -> None:
        """填充高级选项卡的内容，确保2FA按钮靠右对齐。"""
        layout = QVBoxLayout(parent_tab)
        layout.setSpacing(15)

        # 创建一个新的水平布局来容纳2FA控件
        two_fa_container_layout = QHBoxLayout()
        two_fa_container_layout.addWidget(QLabel(t.get("label_2fa_status")))
        two_fa_container_layout.addWidget(ui.two_fa_status_label)
        two_fa_container_layout.addStretch(1) # 添加伸缩，将按钮推到右边
        two_fa_container_layout.addLayout(AddEditDialogUI._create_2fa_buttons_layout(ui))

        ui.backup_codes_input.setPlaceholderText(t.get("placeholder_backup_codes"))
        
        layout.addLayout(two_fa_container_layout) # 添加2FA容器
        layout.addWidget(QLabel(t.get("label_backup_codes")))
        layout.addWidget(ui.backup_codes_input)
        layout.addWidget(QLabel(t.get("label_notes")))
        layout.addWidget(ui.notes_input)

    @staticmethod
    def _create_2fa_buttons_layout(ui: UIData) -> QHBoxLayout:
        """仅创建2FA操作按钮的布局。"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # 定义一个辅助函数来配置图标按钮
        def setup_icon_button(button: QPushButton, icon_name: str, tooltip_key: str):
            button.setText("")
            button.setIcon(QIcon(resource_path(f"ui/assets/icons/{icon_name}.svg")))
            button.setFixedSize(36, 36)
            button.setIconSize(QSize(20, 20))
            button.setObjectName("inlineButton")
            button.setToolTip(t.get(tooltip_key))
        
        # 假设新的翻译键为 "tooltip_scan_file", "tooltip_scan_screen", "tooltip_manual_key"
        setup_icon_button(ui.scan_file_btn, "scan-file", "button_2fa_scan_qr_file")
        setup_icon_button(ui.scan_screen_btn, "scan-screen", "button_2fa_scan_qr_screen")
        setup_icon_button(ui.manual_key_btn, "key-manual", "button_2fa_setup")

        # 移除按钮需要文本
        ui.remove_key_btn.setText(t.get("button_2fa_remove_key"))
        ui.remove_key_btn.setObjectName("inlineButton")

        button_layout.addWidget(ui.scan_file_btn)
        button_layout.addWidget(ui.scan_screen_btn)
        button_layout.addWidget(ui.manual_key_btn)
        button_layout.addWidget(ui.remove_key_btn)

        return button_layout
    # --- MODIFICATION END ---
        
    @staticmethod
    def _create_button_layout(ui: UIData) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.addStretch()
        ui.cancel_btn.setText(t.get("button_cancel"))
        ui.cancel_btn.setObjectName("cancelButton")
        ui.save_btn.setText(t.get("button_save"))
        ui.save_btn.setObjectName("saveButton")
        layout.addWidget(ui.cancel_btn)
        layout.addWidget(ui.save_btn)
        return layout