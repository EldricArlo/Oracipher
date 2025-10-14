# ui/dialogs/add_edit_dialog_ui.py

# 1. 从 typing 模块导入 TYPE_CHECKING
from typing import TYPE_CHECKING
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QTextEdit,
    QWidget,
    QTabWidget,
)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon

from language import t
from utils.paths import resource_path

# 2. 使用 TYPE_CHECKING 来避免循环导入
# 这段代码只在类型检查时运行，所以不会在程序实际执行时导致错误。
if TYPE_CHECKING:
    # 假设你的对话框主类文件是 add_edit_dialog.py，类名是 AddEditDialog
    from ui.dialogs.add_edit_dialog import AddEditDialog


class AddEditDialogUI:
    """此类专门负责构建 AddEditDialog 的UI组件和布局。"""

    # 3. 将类型提示从 QWidget 修改为你自己的对话框类
    # 注意类名要用引号括起来，这叫做前向引用（Forward Reference）。
    def setup_ui(self, dialog_instance: "AddEditDialog") -> None:
        """设置对话框的用户界面。"""
        container = QFrame(dialog_instance)
        container.setObjectName("dialogContainer")

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        header_layout = self._create_header_layout(dialog_instance)

        # 现在 Pylance 理解 dialog_instance 是一个可以拥有 'tabs' 属性的对象，
        # 我们可以将代码恢复到最初的、更简洁的结构。
        self._create_tabs(dialog_instance)

        button_layout = self._create_button_layout(dialog_instance)

        main_layout.addLayout(header_layout)

        # 这一行不再报错，因为 Pylance 现在知道 dialog_instance 有一个 'tabs' 属性。
        main_layout.addWidget(dialog_instance.tabs)

        main_layout.addLayout(button_layout)

        dialog_layout = QVBoxLayout(dialog_instance)
        dialog_layout.addWidget(container)

    def _create_header_layout(self, d: "AddEditDialog") -> QHBoxLayout:
        """创建对话框的头部布局。"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        d.icon_preview_button = QPushButton()
        d.icon_preview_button.setFixedSize(64, 64)
        d.icon_preview_button.setIconSize(QSize(48, 48))
        d.icon_preview_button.setObjectName("detailsActionButton")
        d.icon_preview_button.setToolTip(t.get("tooltip_custom_icon"))
        title_and_name_layout = QVBoxLayout()
        title_text = t.get("edit_title") if d.entry else t.get("add_title")
        title_label = QLabel(title_text)
        title_label.setObjectName("dialogTitle")
        d.name_input = QLineEdit()
        d.name_input.setPlaceholderText(t.get("placeholder_name"))
        title_and_name_layout.addWidget(title_label)
        title_and_name_layout.addWidget(d.name_input)
        header_layout.addWidget(d.icon_preview_button)
        header_layout.addLayout(title_and_name_layout)
        return header_layout

    def _create_tabs(self, d: "AddEditDialog") -> None:
        """创建并填充选项卡。"""
        d.tabs = QTabWidget()
        main_tab, advanced_tab = QWidget(), QWidget()
        d.tabs.addTab(main_tab, t.get("tab_main"))
        d.tabs.addTab(advanced_tab, t.get("tab_advanced"))
        self._populate_main_tab(d, main_tab)
        self._populate_advanced_tab(d, advanced_tab)

    def _populate_main_tab(self, d: "AddEditDialog", parent_tab: QWidget) -> None:
        """填充主选项卡的内容。"""
        layout = QGridLayout(parent_tab)
        layout.setSpacing(15)

        d.username_input = QLineEdit()
        d.username_input.setPlaceholderText(t.get("placeholder_user"))
        d.email_input = QLineEdit()
        d.email_input.setPlaceholderText(t.get("placeholder_email"))
        d.password_input = QLineEdit()
        d.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        d.url_input = QLineEdit()
        d.url_input.setPlaceholderText(t.get("placeholder_url"))
        d.category_input = QLineEdit()
        d.category_input.setPlaceholderText(t.get("placeholder_cat"))

        layout.addWidget(QLabel(t.get("label_user")), 0, 0)
        layout.addWidget(d.username_input, 0, 1)
        layout.addWidget(QLabel(t.get("label_email")), 1, 0)
        layout.addWidget(d.email_input, 1, 1)
        layout.addWidget(QLabel(t.get("label_pass")), 2, 0)
        layout.addLayout(self._create_password_layout(d), 2, 1)
        layout.addWidget(QLabel(t.get("label_url")), 3, 0)
        layout.addLayout(self._create_url_layout(d), 3, 1)
        layout.addWidget(QLabel(t.get("label_cat")), 4, 0)
        layout.addLayout(self._create_category_layout(d), 4, 1)
        layout.setRowStretch(5, 1)

    def _create_password_layout(self, d: "AddEditDialog") -> QHBoxLayout:
        """创建密码输入区域的布局。"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        d.show_hide_btn = QPushButton(t.get("button_show"))
        d.show_hide_btn.setObjectName("inlineButton")
        d.show_hide_btn.setCheckable(True)
        d.generate_btn = QPushButton(t.get("button_generate"))
        d.generate_btn.setObjectName("inlineButton")
        layout.addWidget(d.password_input)
        layout.addWidget(d.show_hide_btn)
        layout.addWidget(d.generate_btn)
        return layout

    def _create_url_layout(self, d: "AddEditDialog") -> QHBoxLayout:
        """创建URL输入区域的布局。"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        d.fetch_icon_btn = QPushButton(t.get("button_fetch_icon"))
        d.fetch_icon_btn.setObjectName("inlineButton")
        layout.addWidget(d.url_input)
        layout.addWidget(d.fetch_icon_btn)
        return layout

    def _create_category_layout(self, d: "AddEditDialog") -> QHBoxLayout:
        """创建分类输入区域的布局。"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        d.set_cat_icon_btn = QPushButton()
        d.set_cat_icon_btn.setObjectName("inlineButton")
        d.set_cat_icon_btn.setIcon(
            QIcon(str(resource_path("ui/assets/icons/edit.svg")))
        )
        d.set_cat_icon_btn.setToolTip(t.get("tooltip_set_cat_icon"))
        layout.addWidget(d.category_input)
        layout.addWidget(d.set_cat_icon_btn)
        return layout

    def _populate_advanced_tab(self, d: "AddEditDialog", parent_tab: QWidget) -> None:
        """填充高级选项卡的内容。"""
        layout = QVBoxLayout(parent_tab)
        layout.setSpacing(15)
        d.backup_codes_input = QTextEdit()
        d.backup_codes_input.setPlaceholderText(t.get("placeholder_backup_codes"))
        d.notes_input = QTextEdit()
        layout.addLayout(self._create_2fa_layout(d))
        layout.addWidget(QLabel(t.get("label_backup_codes")))
        layout.addWidget(d.backup_codes_input)
        layout.addWidget(QLabel(t.get("label_notes")))
        layout.addWidget(d.notes_input)

    def _create_2fa_layout(self, d: "AddEditDialog") -> QHBoxLayout:
        """创建2FA区域的布局。"""
        layout = QHBoxLayout()
        d.two_fa_status_label = QLabel()
        d.scan_qr_btn = QPushButton(t.get("button_2fa_scan_qr"))
        d.scan_qr_btn.setObjectName("inlineButton")
        d.enter_key_btn = QPushButton(t.get("button_2fa_setup"))
        d.enter_key_btn.setObjectName("inlineButton")
        d.remove_key_btn = QPushButton(t.get("button_2fa_remove_key"))
        d.remove_key_btn.setObjectName("inlineButton")

        layout.addWidget(QLabel(t.get("label_2fa_status")))
        layout.addWidget(d.two_fa_status_label, 1)
        layout.addWidget(d.scan_qr_btn)
        layout.addWidget(d.enter_key_btn)
        layout.addWidget(d.remove_key_btn)
        return layout

    def _create_button_layout(self, d: "AddEditDialog") -> QHBoxLayout:
        """创建底部按钮（取消/保存）的布局。"""
        layout = QHBoxLayout()
        layout.addStretch()
        d.cancel_btn = QPushButton(t.get("button_cancel"))
        d.cancel_btn.setObjectName("cancelButton")
        d.save_btn = QPushButton(t.get("button_save"))
        d.save_btn.setObjectName("saveButton")
        layout.addWidget(d.cancel_btn)
        layout.addWidget(d.save_btn)
        return layout
