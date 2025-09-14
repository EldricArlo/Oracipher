# ui/main_interface.py

import logging
import string
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QSplitter, QApplication,
    QTextEdit, QDialog
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer, QSize

from core.data_manager import DataManager
from language import t
from config import load_settings, save_settings
from ui.dialogs.add_edit_dialog import AddEditDialog
from ui.dialogs.generator_dialog import GeneratorWindow
from ui.dialogs.change_password_dialog import ChangePasswordDialog
from ui.dialogs.message_box_dialog import CustomMessageBox
from ui.dialogs.settings_dialog import SettingsDialog

# 获取此模块的 logger 实例
logger = logging.getLogger(__name__)

class MainWindow(QWidget):
    """
    应用程序的主功能界面。

    这个界面在用户成功解锁后显示，包含了所有核心功能：
    - 显示和过滤密码条目。
    - 查看条目详情。
    - 添加、编辑和删除条目。
    - 访问设置、密码生成器等工具。
    """
    def __init__(self, data_manager: DataManager):
        """
        初始化主窗口。

        Args:
            data_manager (DataManager): 数据管理器实例，用于所有数据库操作。
        """
        super().__init__()
        self.data_manager = data_manager
        self.entries = []  # 内存中的条目缓存
        self.current_selected_id = None
        self.setObjectName("MainWindow")
        
        self.init_ui()
        self.load_data()
        logger.info("主界面 (MainWindow) 初始化完成。")

    def init_ui(self):
        """
        构建主界面的所有UI组件和布局。
        """
        # --- 1. 主布局与分割器 ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- 2. 侧边栏 (Sidebar) ---
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebarContainer")
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 5, 10, 0)
        sidebar_layout.setSpacing(15)
        
        self.category_list = QListWidget()
        self.category_list.itemSelectionChanged.connect(self.on_category_selected)

        # 功能按钮
        self.settings_button = QPushButton()
        self.settings_button.setObjectName("sidebarExitButton")
        self.settings_button.clicked.connect(self._open_settings_dialog)

        self.generate_password_button = QPushButton()
        self.generate_password_button.setObjectName("sidebarExitButton")
        self.generate_password_button.clicked.connect(self._open_generator_window)

        self.add_account_button = QPushButton()
        self.add_account_button.setObjectName("sidebarExitButton")
        self.add_account_button.clicked.connect(self.add_new_entry)

        self.minimize_button = QPushButton()
        self.minimize_button.setObjectName("sidebarExitButton")
        self.minimize_button.clicked.connect(self._minimize_window)
        
        self.exit_button = QPushButton()
        self.exit_button.setObjectName("sidebarExitButton")
        self.exit_button.clicked.connect(QApplication.instance().quit)
        
        # 将组件添加到侧边栏布局
        sidebar_layout.addWidget(self.category_list, stretch=0)
        sidebar_layout.addStretch(1) # 弹簧，将下面的按钮推到底部
        sidebar_layout.addWidget(self.settings_button)
        sidebar_layout.addWidget(self.minimize_button)
        sidebar_layout.addWidget(self.generate_password_button)
        sidebar_layout.addWidget(self.add_account_button)
        sidebar_layout.addWidget(self.exit_button)
        
        # --- 3. 内容区 (Content Area) ---
        content_widget = QWidget()
        content_widget.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 5, 0, 0)
        content_layout.setSpacing(20)
        
        # 顶部工具栏 (搜索框 + 添加按钮)
        top_toolbar_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.textChanged.connect(self.filter_entries)
        
        self.add_button = QPushButton()
        self.add_button.setObjectName("addButton")
        self.add_button.setFixedSize(45, 45)
        self.add_button.clicked.connect(self.add_new_entry)
        
        top_toolbar_layout.addWidget(self.search_input)
        top_toolbar_layout.addSpacing(15)
        top_toolbar_layout.addWidget(self.add_button)
        
        # 内部内容分割器 (条目列表 | 详情视图)
        inner_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.entry_list = QListWidget()
        self.entry_list.itemSelectionChanged.connect(self.on_entry_selected)
        
        self.details_container = QWidget()
        self.details_layout = QVBoxLayout(self.details_container)
        self.details_layout.setContentsMargins(15, 0, 0, 0)
        self.details_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        inner_splitter.addWidget(self.entry_list)
        inner_splitter.addWidget(self.details_container)
        inner_splitter.setSizes([220, 480]) # 初始尺寸比例
        
        # 将组件添加到内容区布局
        content_layout.addLayout(top_toolbar_layout)
        content_layout.addWidget(inner_splitter)
        
        # --- 4. 组装主分割器 ---
        main_splitter.addWidget(sidebar_widget)
        main_splitter.addWidget(content_widget)
        main_splitter.setSizes([240, 560]) # 初始尺寸比例
        main_layout.addWidget(main_splitter)
        
        self.retranslate_ui()
        self.clear_details()
        logger.debug("主界面UI布局构建完成。")

    def retranslate_ui(self):
        """
        应用文本翻译到所有UI元素。
        """
        self.settings_button.setText(t.get('button_settings'))
        self.generate_password_button.setText(t.get('button_generate_password'))
        self.add_account_button.setText(t.get('button_add_account'))
        self.minimize_button.setText(t.get('button_minimize'))
        self.exit_button.setText(t.get('button_exit'))

        self.search_input.setPlaceholderText(t.get('search_placeholder'))
        self.add_button.setText(t.get('button_add_icon'))
        
        self.populate_categories()
        self.clear_details()

    def display_entry_details(self, entry: dict):
        """
        在详情区域动态地创建和显示所选条目的详细信息。

        Args:
            entry (dict): 包含条目所有信息的字典。
        """
        self.clear_layout(self.details_layout)
        self.details_layout.setSpacing(20)

        # --- 详情页头部 ---
        header_layout = QHBoxLayout()
        name_label = QLabel(entry["name"])
        name_label.setObjectName("detailsNameLabel")
        name_label.setWordWrap(True)

        # --- 核心修改 START: 增加日志和健壮性检查 ---
        icon_base_path = Path(__file__).parent / "assets" / "icons"
        edit_icon_path = icon_base_path / "edit.svg"
        delete_icon_path = icon_base_path / "delete.svg"

        # 编辑按钮
        self.edit_button = QPushButton()
        self.edit_button.setObjectName("detailsActionButton")
        self.edit_button.setFixedSize(40, 40)
        edit_icon = QIcon(str(edit_icon_path))
        if not edit_icon.isNull():
            self.edit_button.setIcon(edit_icon)
            self.edit_button.setIconSize(QSize(22, 22))
        else:
            self.edit_button.setText(t.get('button_edit_icon'))
            # 仅在文件实际存在但加载失败时记录警告
            if edit_icon_path.exists():
                logger.warning(f"编辑图标加载失败: {edit_icon_path}. 请确保安装了 PyQt6-SVG。")
            else:
                 logger.warning(f"编辑图标文件未找到: {edit_icon_path}")
        self.edit_button.setToolTip(t.get('edit_title'))
        self.edit_button.clicked.connect(self.edit_selected_entry)

        # 删除按钮
        self.delete_button = QPushButton()
        self.delete_button.setObjectName("detailsActionButton")
        self.delete_button.setFixedSize(40, 40)
        delete_icon = QIcon(str(delete_icon_path))
        if not delete_icon.isNull():
            self.delete_button.setIcon(delete_icon)
            self.delete_button.setIconSize(QSize(22, 22))
        else:
            self.delete_button.setText(t.get('button_delete_icon'))
            if delete_icon_path.exists():
                logger.warning(f"删除图标加载失败: {delete_icon_path}. 请确保安装了 PyQt6-SVG。")
            else:
                 logger.warning(f"删除图标文件未找到: {delete_icon_path}")

        self.delete_button.setToolTip(t.get('msg_title_confirm_delete'))
        self.delete_button.clicked.connect(self.delete_selected_entry)
        # --- 核心修改 END ---
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(self.edit_button)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.delete_button)

        # --- 动态字段创建 (此部分无逻辑修改) ---
        def create_detail_field(title_text, value_text, is_password=False, multiline=False):
            """一个辅助函数，用于创建一个标准的详情字段（标签+值+按钮）。"""
            field_frame = QFrame()
            field_frame.setObjectName("detailField")
            field_layout = QVBoxLayout(field_frame)
            title_label = QLabel(title_text)
            title_label.setObjectName("fieldTitleLabel")
            value_layout = QHBoxLayout()
            
            if multiline:
                value_display = QTextEdit(value_text)
                value_display.setMinimumHeight(80)
                def adjust_height():
                    doc_height = int(value_display.document().size().height())
                    new_height = max(80, doc_height + 10)
                    value_display.setFixedHeight(new_height)
                value_display.document().contentsChanged.connect(adjust_height)
                adjust_height()
            else:
                value_display = QLineEdit(value_text)

            value_display.setReadOnly(True)
            value_display.setObjectName("fieldValueDisplay")
            value_layout.addWidget(value_display)

            if is_password:
                value_display.setEchoMode(QLineEdit.EchoMode.Password)
                show_hide_button = QPushButton(t.get('button_show'))
                show_hide_button.setObjectName("inlineButton")
                show_hide_button.setCheckable(True)
                def toggle_visibility(checked):
                    value_display.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
                    show_hide_button.setText(t.get('button_hide') if checked else t.get('button_show'))
                show_hide_button.toggled.connect(toggle_visibility)
                value_layout.addWidget(show_hide_button)

            copy_button = QPushButton(t.get('button_copy'))
            copy_button.setObjectName("inlineButton")
            def copy_and_feedback():
                clipboard = QApplication.clipboard()
                text_to_copy = value_display.toPlainText() if isinstance(value_display, QTextEdit) else value_display.text()
                clipboard.setText(text_to_copy)
                
                original_text = copy_button.text()
                copy_button.setText(t.get('button_copied'))
                QTimer.singleShot(1500, lambda: copy_button.setText(original_text))
                
                QTimer.singleShot(30000, lambda: clipboard.clear() if clipboard.text() == text_to_copy else None)
                logger.debug(f"已复制字段 '{title_text}' 的内容到剪贴板。")
            copy_button.clicked.connect(copy_and_feedback)
            value_layout.addWidget(copy_button)

            field_layout.addWidget(title_label)
            field_layout.addLayout(value_layout)
            return field_frame

        username_field = create_detail_field(t.get('label_user'), entry["details"].get("username", "N/A"))
        password_field = create_detail_field(t.get('label_pass'), entry["details"].get("password", "N/A"), is_password=True)

        self.details_layout.addLayout(header_layout)
        self.details_layout.addWidget(username_field)
        self.details_layout.addWidget(password_field)
        
        notes = entry["details"].get("notes", "")
        if notes:
            notes_field = create_detail_field(t.get('label_notes'), notes, multiline=True)
            self.details_layout.addWidget(notes_field)

        self.details_layout.addStretch()

    # 后续方法与之前版本相同，此处为简洁省略...
    # (在实际文件中，所有方法都应保留)
    def _open_add_edit_dialog(self, entry: dict = None):
        self.overlay = QFrame(self)
        self.overlay.setObjectName("dialogOverlay")
        self.overlay.setGeometry(self.rect())
        
        dialog = AddEditDialog(self, entry=entry)
        self.overlay.show()
        
        if dialog.exec():
            data = dialog.get_data()
            if not data["name"]:
                CustomMessageBox.information(self, t.get('msg_title_input_error'), t.get('msg_empty_name_error'))
                self.overlay.hide()
                return
            
            mode = "编辑" if entry else "添加"
            logger.info(f"正在保存 ({mode}) 条目: {data['name']}")
            self.data_manager.save_entry(data["category"], data["name"], data["details"])
            self.load_data()
        
        self.overlay.hide()

    def add_new_entry(self):
        logger.debug("用户点击'添加新条目'。")
        self._open_add_edit_dialog()

    def edit_selected_entry(self):
        if not self.current_selected_id: return
        entry = next((e for e in self.entries if e["id"] == self.current_selected_id), None)
        if entry:
            logger.debug(f"用户点击'编辑条目' (ID: {self.current_selected_id})。")
            self._open_add_edit_dialog(entry)

    def resizeEvent(self, event):
        if hasattr(self, 'overlay') and self.overlay.isVisible():
            self.overlay.setGeometry(self.rect())
        super().resizeEvent(event)
    
    def load_data(self):
        logger.info("正在从数据库加载并解密所有条目...")
        self.entries = self.data_manager.get_entries()
        self.populate_categories()
        self.filter_entries()
        self.clear_details()

    def populate_categories(self):
        self.category_list.blockSignals(True)
        
        current_item = self.category_list.currentItem()
        current_text = current_item.text() if current_item else t.get('all_categories')
        
        self.category_list.clear()
        self.category_list.addItem(t.get('all_categories'))
        
        categories = sorted(list(set(e["category"] for e in self.entries if e["category"])))
        self.category_list.addItems(categories)
        
        items = self.category_list.findItems(current_text, Qt.MatchFlag.MatchExactly)
        if items:
            self.category_list.setCurrentItem(items[0])
        else:
            self.category_list.setCurrentRow(0)
            
        self.category_list.blockSignals(False)

    def filter_entries(self):
        search_text = self.search_input.text().lower()
        cat_item = self.category_list.currentItem()
        
        category = cat_item.text() if cat_item else t.get('all_categories')
        
        self.entry_list.blockSignals(True)
        self.entry_list.clear()
        
        for entry in self.entries:
            cat_match = (category == t.get('all_categories') or entry["category"] == category)
            text_match = search_text in entry["name"].lower()
            
            if cat_match and text_match:
                item = QListWidgetItem(entry["name"])
                item.setData(Qt.ItemDataRole.UserRole, entry["id"])
                self.entry_list.addItem(item)
        
        self.entry_list.blockSignals(False)
        
        if self.entry_list.count() > 0:
            self.entry_list.setCurrentRow(0)
        else:
            self.clear_details()

    def on_category_selected(self):
        self.filter_entries()

    def on_entry_selected(self):
        items = self.entry_list.selectedItems()
        if not items:
            self.current_selected_id = None
            self.clear_details()
            return
        
        entry_id = items[0].data(Qt.ItemDataRole.UserRole)
        if self.current_selected_id == entry_id:
            return

        self.current_selected_id = entry_id
        entry = next((e for e in self.entries if e["id"] == entry_id), None)
        if entry:
            self.display_entry_details(entry)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

    def clear_details(self):
        self.current_selected_id = None
        self.clear_layout(self.details_layout)
        placeholder = QLabel(t.get('details_placeholder'))
        placeholder.setObjectName("placeholderLabel")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_layout.addWidget(placeholder, 1, Qt.AlignmentFlag.AlignCenter)
    
    def delete_selected_entry(self):
        if not self.current_selected_id: return
        entry = next((e for e in self.entries if e["id"] == self.current_selected_id), None)
        if not entry: return
        
        logger.debug(f"用户尝试删除条目 '{entry['name']}' (ID: {self.current_selected_id})。")
        confirm = CustomMessageBox.question(
            self, 
            t.get('msg_title_confirm_delete'),
            t.get('msg_confirm_delete', name=entry["name"])
        )
        
        if confirm == QDialog.DialogCode.Accepted:
            logger.info(f"用户确认删除条目 '{entry['name']}' (ID: {self.current_selected_id})。")
            self.data_manager.delete_entry(self.current_selected_id)
            self.load_data()

    def _minimize_window(self):
        top_level_window = self.window()
        if top_level_window:
            top_level_window.showMinimized()

    def _open_generator_window(self):
        dialog = GeneratorWindow(self)
        dialog.exec()

    def _is_password_strong(self, password: str) -> bool:
        if len(password) < 8: return False
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_digit = any(c in string.digits for c in password)
        return has_lower and has_upper and has_digit

    def _open_change_password_dialog(self):
        dialog = ChangePasswordDialog(self)
        if dialog.exec():
            passwords, reason = dialog.get_passwords()
            
            if not passwords:
                msg_key = f'msg_pass_change_fail_{reason}'
                msg = t.get(msg_key, "Unknown error")
                CustomMessageBox.information(self, t.get('msg_title_input_error'), msg)
                logger.warning(f"更改主密码失败: {reason}")
                return

            old_pass, new_pass = passwords
            if not self._is_password_strong(new_pass):
                CustomMessageBox.information(self, t.get('msg_title_input_error'), t.get('msg_pass_change_fail_weak'))
                logger.warning("更改主密码失败: 新密码强度不足。")
                return

            success = self.data_manager.change_master_password(old_pass, new_pass)
            if success:
                CustomMessageBox.information(self, t.get('msg_title_pass_change_success'), t.get('msg_pass_change_success'))
                logger.info("主密码已成功更改。")
            else:
                CustomMessageBox.information(self, t.get('msg_title_pass_change_fail'), t.get('msg_pass_change_fail_old_wrong'))

    def _open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.change_password_requested.connect(self._open_change_password_dialog)
        
        if dialog.exec():
            selected_lang = dialog.get_selected_language()
            settings = load_settings()
            
            if settings.get('language') != selected_lang:
                settings['language'] = selected_lang
                save_settings(settings)
                logger.info(f"语言设置已更改为 '{selected_lang}'。")
                
                t.set_language(selected_lang)
                self.retranslate_ui()
                
                CustomMessageBox.information(self, 
                                           t.get('settings_title'), 
                                           t.get('settings_restart_msg'))