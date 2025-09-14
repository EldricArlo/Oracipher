# ui/main_interface.py

import logging
import string
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QSplitter, QApplication,
    QTextEdit, QDialog, QLayout, QFileDialog, QStyledItemDelegate, QStyleOptionViewItem,
    QStyle
)
from PyQt6.QtGui import QIcon, QResizeEvent, QPainter
from PyQt6.QtCore import Qt, QTimer, QSize, QModelIndex

from core.data_manager import DataManager
from core.icon_fetcher import IconFetcher
from core.data_handler import DataHandler
from language import t
from config import load_settings, save_settings
from ui.dialogs.add_edit_dialog import AddEditDialog
from ui.dialogs.generator_dialog import GeneratorWindow
from ui.dialogs.change_password_dialog import ChangePasswordDialog
from ui.dialogs.message_box_dialog import CustomMessageBox
from ui.dialogs.settings_dialog import SettingsDialog
from utils import resource_path

logger = logging.getLogger(__name__)


# --- 核心修改 START: 创建自定义委托以移除焦点框 ---
class NoFocusDelegate(QStyledItemDelegate):
    """
    一个自定义的样式委托，其唯一目的是在绘制项目时移除焦点指示器。
    """
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        # 检查当前项目是否处在“有焦点”的状态
        if option.state & QStyle.StateFlag.State_HasFocus:
            # 如果是，就从状态中移除这个标志
            # 使用位操作 "AND NOT" 来精确地去掉这个状态位
            option.state = option.state & ~QStyle.StateFlag.State_HasFocus
        
        # 使用被我们修改过的'option'来调用父类的原始paint方法
        # 这样一来，所有正常的绘制都会进行，唯独绘制焦点框这一步会被跳过
        super().paint(painter, option, index)

# --- 核心修改 END ---


class EntryListItemWidget(QWidget):
    def __init__(self, entry: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.entry_data = entry
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(28, 28)
        self.icon_label.setScaledContents(True)
        details = entry.get("details", {})
        icon_data = details.get("icon_data")
        pixmap = IconFetcher.pixmap_from_base64(icon_data)
        self.icon_label.setPixmap(pixmap)
        self.name_label = QLabel(entry.get("name", "Unnamed"))
        self.name_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        layout.addStretch()


class MainWindow(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager: DataManager = data_manager
        self.entries: List[Dict[str, Any]] = []
        self.current_selected_id: Optional[int] = None
        self.setObjectName("MainWindow")
        self.init_ui()
        self.load_data()
        logger.info("主界面 (MainWindow) 初始化完成。")

    def init_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebarContainer")
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 5, 10, 0)
        sidebar_layout.setSpacing(15)
        
        self.category_list = QListWidget()
        self.category_list.itemSelectionChanged.connect(self.on_category_selected)
        
        self.entry_list = QListWidget()
        self.entry_list.itemSelectionChanged.connect(self.on_entry_selected)

        # --- 核心修改 START: 应用自定义委托 ---
        no_focus_delegate = NoFocusDelegate(self)
        self.category_list.setItemDelegate(no_focus_delegate)
        self.entry_list.setItemDelegate(no_focus_delegate)
        # --- 核心修改 END ---

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
        sidebar_layout.addWidget(self.category_list, stretch=0)
        sidebar_layout.addStretch(1)
        sidebar_layout.addWidget(self.settings_button)
        sidebar_layout.addWidget(self.minimize_button)
        sidebar_layout.addWidget(self.generate_password_button)
        sidebar_layout.addWidget(self.add_account_button)
        sidebar_layout.addWidget(self.exit_button)
        content_widget = QWidget()
        content_widget.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 5, 0, 0)
        content_layout.setSpacing(20)
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
        inner_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.details_container = QWidget()
        self.details_layout = QVBoxLayout(self.details_container)
        self.details_layout.setContentsMargins(15, 0, 0, 0)
        self.details_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        inner_splitter.addWidget(self.entry_list)
        inner_splitter.addWidget(self.details_container)
        inner_splitter.setSizes([220, 480])
        content_layout.addLayout(top_toolbar_layout)
        content_layout.addWidget(inner_splitter)
        main_splitter.addWidget(sidebar_widget)
        main_splitter.addWidget(content_widget)
        main_splitter.setSizes([240, 560])
        main_layout.addWidget(main_splitter)
        self.retranslate_ui()
        self.clear_details()
        logger.debug("主界面UI布局构建完成。")

    def retranslate_ui(self) -> None:
        self.settings_button.setText(t.get('button_settings'))
        self.generate_password_button.setText(t.get('button_generate_password'))
        self.add_account_button.setText(t.get('button_add_account'))
        self.minimize_button.setText(t.get('button_minimize'))
        self.exit_button.setText(t.get('button_exit'))
        self.search_input.setPlaceholderText(t.get('search_placeholder'))
        self.add_button.setText(t.get('button_add_icon'))
        self.populate_categories()
        self.clear_details()

    def display_entry_details(self, entry: Dict[str, Any]) -> None:
        self.clear_layout(self.details_layout)
        self.details_layout.setSpacing(20)
        details = entry.get("details", {})
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        icon_label = QLabel()
        icon_label.setFixedSize(52, 52)
        icon_label.setScaledContents(True)
        icon_data = details.get("icon_data")
        pixmap = IconFetcher.pixmap_from_base64(icon_data)
        icon_label.setPixmap(pixmap)
        name_label = QLabel(str(entry.get("name", "Unnamed")))
        name_label.setObjectName("detailsNameLabel")
        name_label.setWordWrap(True)
        header_layout.addWidget(icon_label)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        edit_icon_path = resource_path("ui/assets/icons/edit.svg")
        delete_icon_path = resource_path("ui/assets/icons/delete.svg")
        edit_button = QPushButton()
        edit_button.setObjectName("detailsActionButton")
        edit_button.setFixedSize(40, 40)
        edit_icon = QIcon(str(edit_icon_path))
        if not edit_icon.isNull():
            edit_button.setIcon(edit_icon)
            edit_button.setIconSize(QSize(22, 22))
        else:
            edit_button.setText(t.get('button_edit_icon'))
            logger.warning(f"编辑图标加载失败或未找到: {edit_icon_path}")
        edit_button.setToolTip(t.get('edit_title'))
        edit_button.clicked.connect(self.edit_selected_entry)
        delete_button = QPushButton()
        delete_button.setObjectName("detailsActionButton")
        delete_button.setFixedSize(40, 40)
        delete_icon = QIcon(str(delete_icon_path))
        if not delete_icon.isNull():
            delete_button.setIcon(delete_icon)
            delete_button.setIconSize(QSize(22, 22))
        else:
            delete_button.setText(t.get('button_delete_icon'))
            logger.warning(f"删除图标加载失败或未找到: {delete_icon_path}")
        delete_button.setToolTip(t.get('msg_title_confirm_delete'))
        delete_button.clicked.connect(self.delete_selected_entry)
        header_layout.addWidget(edit_button)
        header_layout.addSpacing(10)
        header_layout.addWidget(delete_button)
        def create_detail_field(title_text: str, value_text: str, is_password: bool = False, multiline: bool = False) -> QFrame:
            field_frame = QFrame()
            field_frame.setObjectName("detailField")
            field_layout = QVBoxLayout(field_frame)
            title_label = QLabel(title_text)
            title_label.setObjectName("fieldTitleLabel")
            value_layout = QHBoxLayout()
            value_display: QLineEdit | QTextEdit
            if multiline:
                value_display = QTextEdit(value_text)
                value_display.setReadOnly(True)
                value_display.setObjectName("fieldValueDisplay")
                value_display.setMinimumHeight(80)
                doc_height = int(value_display.document().size().height())
                value_display.setFixedHeight(max(80, doc_height + 15))
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
                def toggle_visibility(checked: bool) -> None:
                    value_display.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
                    show_hide_button.setText(t.get('button_hide') if checked else t.get('button_show'))
                show_hide_button.toggled.connect(toggle_visibility)
                value_layout.addWidget(show_hide_button)
            copy_button = QPushButton(t.get('button_copy'))
            copy_button.setObjectName("inlineButton")
            def copy_and_feedback() -> None:
                clipboard = QApplication.clipboard()
                text_to_copy = value_display.toPlainText() if isinstance(value_display, QTextEdit) else value_display.text()
                clipboard.setText(text_to_copy)
                original_text = copy_button.text()
                copy_button.setText(t.get('button_copied'))
                copy_button.setEnabled(False)
                QTimer.singleShot(1500, lambda: (copy_button.setText(original_text), copy_button.setEnabled(True)))
                QTimer.singleShot(30000, lambda: clipboard.clear() if clipboard.text() == text_to_copy else None)
                logger.debug(f"已复制字段 '{title_text}' 的内容到剪贴板。")
            copy_button.clicked.connect(copy_and_feedback)
            value_layout.addWidget(copy_button)
            field_layout.addWidget(title_label)
            field_layout.addLayout(value_layout)
            return field_frame
        username_field = create_detail_field(t.get('label_user'), details.get("username", "N/A"))
        password_field = create_detail_field(t.get('label_pass'), details.get("password", "N/A"), is_password=True)
        self.details_layout.addLayout(header_layout)
        self.details_layout.addWidget(username_field)
        self.details_layout.addWidget(password_field)
        notes = details.get("notes", "")
        if notes:
            notes_field = create_detail_field(t.get('label_notes'), notes, multiline=True)
            self.details_layout.addWidget(notes_field)
        self.details_layout.addStretch()

    def _open_add_edit_dialog(self, entry: Optional[Dict[str, Any]] = None) -> None:
        dialog = AddEditDialog(self, entry=entry)
        if dialog.exec():
            data = dialog.get_data()
            if not data.get("name"):
                CustomMessageBox.information(self, t.get('msg_title_input_error'), t.get('msg_empty_name_error'))
                return
            if not data["category"]:
                data["category"] = t.get('default_category')
                logger.info(f"条目 '{data['name']}' 的分类为空，已设置为默认分类。")
            mode = "编辑" if entry else "添加"
            logger.info(f"正在保存 ({mode}) 条目: {data['name']}")
            self.data_manager.save_entry(data["category"], data["name"], data["details"])
            self.load_data()

    def add_new_entry(self) -> None:
        logger.debug("用户点击'添加新条目'。")
        self._open_add_edit_dialog()

    def edit_selected_entry(self) -> None:
        if not self.current_selected_id: return
        entry = next((e for e in self.entries if e["id"] == self.current_selected_id), None)
        if entry:
            logger.debug(f"用户点击'编辑条目' (ID: {self.current_selected_id})。")
            self._open_add_edit_dialog(entry)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
    
    def load_data(self) -> None:
        logger.info("正在从数据库加载并解密所有条目...")
        self.entries = self.data_manager.get_entries()
        self.clear_details()
        self.populate_categories()
        self.filter_entries()

    def populate_categories(self) -> None:
        self.category_list.blockSignals(True)
        current_item = self.category_list.currentItem()
        current_text = current_item.text() if current_item else t.get('all_categories')
        self.category_list.clear()
        self.category_list.addItem(QListWidgetItem(t.get('all_categories')))
        categories = sorted(list(set(e["category"] for e in self.entries if e["category"])))
        for cat in categories:
            self.category_list.addItem(QListWidgetItem(cat))
        items = self.category_list.findItems(current_text, Qt.MatchFlag.MatchExactly)
        if items:
            self.category_list.setCurrentItem(items[0])
        else:
            self.category_list.setCurrentRow(0)
        self.category_list.blockSignals(False)

    def filter_entries(self) -> None:
        search_text = self.search_input.text().lower()
        cat_item = self.category_list.currentItem()
        category = cat_item.text() if cat_item else t.get('all_categories')
        self.entry_list.blockSignals(True)
        self.entry_list.clear()
        item_to_select = None
        for entry in self.entries:
            cat_match = (category == t.get('all_categories') or entry["category"] == category)
            text_match = search_text in entry["name"].lower()
            if cat_match and text_match:
                list_item = QListWidgetItem(self.entry_list)
                list_item.setData(Qt.ItemDataRole.UserRole, entry["id"])
                list_item.setSizeHint(QSize(0, 48))
                widget = EntryListItemWidget(entry)
                self.entry_list.addItem(list_item)
                self.entry_list.setItemWidget(list_item, widget)
                if entry["id"] == self.current_selected_id:
                    item_to_select = list_item
        if item_to_select:
            self.entry_list.setCurrentItem(item_to_select)
        elif self.entry_list.count() > 0:
            self.entry_list.setCurrentRow(0)
        self.entry_list.blockSignals(False)
        if self.entry_list.count() == 0:
            self.clear_details()
        else:
            if not self.entry_list.selectedItems():
                self.entry_list.setCurrentRow(0)
            self.on_entry_selected()

    def on_category_selected(self) -> None:
        self.filter_entries()

    def on_entry_selected(self) -> None:
        selected_items = self.entry_list.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        if self.current_selected_id == entry_id:
            return
        self.current_selected_id = entry_id
        entry = next((e for e in self.entries if e["id"] == entry_id), None)
        if entry:
            self.display_entry_details(entry)
        else:
            self.clear_details()

    def clear_layout(self, layout: QLayout) -> None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

    def clear_details(self) -> None:
        self.current_selected_id = None
        self.clear_layout(self.details_layout)
        placeholder = QLabel(t.get('details_placeholder'))
        placeholder.setObjectName("placeholderLabel")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_layout.addWidget(placeholder, 1, Qt.AlignmentFlag.AlignCenter)
    
    def delete_selected_entry(self) -> None:
        if not self.current_selected_id: return
        entry = next((e for e in self.entries if e["id"] == self.current_selected_id), None)
        if not entry: return
        logger.debug(f"用户尝试删除条目 '{entry['name']}' (ID: {self.current_selected_id})。")
        confirm = CustomMessageBox.question(self, t.get('msg_title_confirm_delete'), t.get('msg_confirm_delete', name=entry["name"]))
        if confirm == QDialog.DialogCode.Accepted:
            logger.info(f"用户确认删除条目 '{entry['name']}' (ID: {self.current_selected_id})。")
            self.data_manager.delete_entry(self.current_selected_id)
            self.load_data()

    def _minimize_window(self) -> None:
        top_level_window = self.window()
        if top_level_window:
            top_level_window.showMinimized()

    def _open_generator_window(self) -> None:
        dialog = GeneratorWindow(self)
        dialog.exec()

    def _is_password_strong(self, password: str) -> bool:
        if len(password) < 8: return False
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_digit = any(c in string.digits for c in password)
        return has_lower and has_upper and has_digit

    def _open_change_password_dialog(self) -> None:
        dialog = ChangePasswordDialog(self)
        if dialog.exec():
            passwords, reason = dialog.get_passwords()
            if not passwords:
                msg_key = f'msg_pass_change_fail_{reason}'
                msg = t.get(msg_key, "Unknown error")
                CustomMessageBox.information(self, t.get('msg_title_pass_change_fail'), msg)
                logger.warning(f"更改主密码失败: {reason}")
                return
            old_pass, new_pass = passwords
            if not self._is_password_strong(new_pass):
                CustomMessageBox.information(self, t.get('msg_title_pass_change_fail'), t.get('msg_pass_change_fail_weak'))
                logger.warning("更改主密码失败: 新密码强度不足。")
                return
            success = self.data_manager.change_master_password(old_pass, new_pass)
            if success:
                CustomMessageBox.information(self, t.get('msg_title_pass_change_success'), t.get('msg_pass_change_success'))
                logger.info("主密码已成功更改。")
            else:
                CustomMessageBox.information(self, t.get('msg_title_pass_change_fail'), t.get('msg_pass_change_fail_old_wrong'))

    def _open_settings_dialog(self) -> None:
        dialog = SettingsDialog(self)
        dialog.change_password_requested.connect(self._open_change_password_dialog)
        dialog.import_requested.connect(self._handle_import_data)
        dialog.export_requested.connect(self._handle_export_data)
        if dialog.exec():
            selected_lang = dialog.get_selected_language()
            settings = load_settings()
            if settings.get('language') != selected_lang:
                settings['language'] = selected_lang
                save_settings(settings)
                logger.info(f"语言设置已更改为 '{selected_lang}'。")
                t.set_language(selected_lang)
                self.retranslate_ui() 
                CustomMessageBox.information(self, t.get('settings_title'), t.get('settings_restart_msg'))

    def _handle_export_data(self) -> None:
        logger.info("用户请求导出数据。")
        file_path, _ = QFileDialog.getSaveFileName(self, t.get('dialog_export_title'), "safekey_export.csv", f"{t.get('dialog_csv_files')} (*.csv)")
        if not file_path:
            logger.info("用户取消了导出操作。")
            return
        try:
            entries = self.data_manager.get_entries()
            csv_data = DataHandler.export_to_csv(entries)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(csv_data)
            logger.info(f"成功导出 {len(entries)} 个条目到 {file_path}")
            CustomMessageBox.information(self, t.get('msg_export_success_title'), t.get('msg_export_success', count=len(entries), path=file_path))
        except Exception as e:
            logger.error(f"导出数据到 {file_path} 失败。", exc_info=True)
            CustomMessageBox.information(self, t.get('msg_export_fail_title'), t.get('msg_export_fail', error=str(e)))

    def _handle_import_data(self) -> None:
        logger.info("用户请求导入数据。")
        confirm = CustomMessageBox.question(self, t.get('msg_import_confirm_title'), t.get('msg_import_confirm'))
        if confirm != QDialog.DialogCode.Accepted:
            logger.info("用户取消了导入操作。")
            return
        file_path, _ = QFileDialog.getOpenFileName(self, t.get('dialog_import_title'), "", f"{t.get('dialog_csv_files')} (*.csv)")
        if not file_path:
            logger.info("用户在文件选择阶段取消了导入操作。")
            return
        try:
            entries_to_import = DataHandler.import_from_csv(file_path)
            if not entries_to_import:
                 CustomMessageBox.information(self, t.get('msg_import_fail_title'), "CSV文件为空或格式不正确。")
                 return
            for entry in entries_to_import:
                self.data_manager.save_entry(entry['category'], entry['name'], entry['details'])
            logger.info(f"成功从 {file_path} 导入 {len(entries_to_import)} 个条目。")
            self.load_data()
            CustomMessageBox.information(self, t.get('msg_import_success_title'), t.get('msg_import_success', count=len(entries_to_import)))
        except Exception as e:
            logger.error(f"从 {file_path} 导入数据失败。", exc_info=True)
            CustomMessageBox.information(self, t.get('msg_import_fail_title'), t.get('msg_import_fail', error=str(e)))