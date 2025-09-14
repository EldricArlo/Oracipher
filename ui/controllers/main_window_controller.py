# ui/controllers/main_window_controller.py

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, List, Dict, Any, Optional

from PyQt6.QtWidgets import (QDialog, QApplication, QMainWindow, QWidget, QListWidgetItem)
from PyQt6.QtCore import QObject, Qt # 修正: 在这里导入 Qt

from language import t
from config import load_settings, save_settings
from ..dialogs.add_edit_dialog import AddEditDialog
from ..dialogs.change_password_dialog import ChangePasswordDialog
from ..dialogs.generator_dialog import GeneratorWindow
from ..dialogs.message_box_dialog import CustomMessageBox
from ..dialogs.settings_dialog import SettingsDialog
from ..task_manager import task_manager
from ..theme_manager import apply_theme, get_current_theme
from .data_io_controller import DataIOController

if TYPE_CHECKING:
    from ..views.sidebar_view import SidebarView
    from ..views.main_content_view import MainContentView
    from core.database import DataManager

logger = logging.getLogger(__name__)

class MainWindowController(QObject):
    def __init__(
        self,
        main_app_window: QMainWindow,
        sidebar_view: 'SidebarView',
        content_view: 'MainContentView',
        data_manager: 'DataManager'
    ):
        super().__init__()
        self.main_app_window = main_app_window
        self.sidebar_view = sidebar_view
        self.content_view = content_view
        self.data_manager = data_manager

        self.io_controller = DataIOController(
            main_app_window, data_manager, self.load_initial_data
        )

        self.all_entries: List[Dict[str, Any]] = []
        self.entries_by_name: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.category_icons: Dict[str, str] = {}
        
        self.current_category: str = t.get('all_categories')
        self.current_search_term: str = ""
        
        self._connect_signals()

    def _connect_signals(self) -> None:
        self.sidebar_view.category_clicked.connect(self.on_category_selected)
        self.sidebar_view.add_account_button.clicked.connect(self._open_add_dialog)
        self.sidebar_view.generate_password_button.clicked.connect(self._open_generator_dialog)
        self.sidebar_view.settings_button.clicked.connect(self._open_settings_dialog)
        self.sidebar_view.minimize_button.clicked.connect(self.main_app_window.showMinimized)
        self.sidebar_view.exit_button.clicked.connect(self.main_app_window.close)
        
        self.content_view.add_button.clicked.connect(self._open_add_dialog)
        self.content_view.search_input.textChanged.connect(self.on_search_term_changed)
        self.content_view.entry_list.currentItemChanged.connect(self.on_entry_selected)
        self.content_view.details_view.edit_requested.connect(self._open_edit_dialog)
        self.content_view.details_view.delete_requested.connect(self.on_delete_entry)

    def load_initial_data(self) -> None:
        def on_success(data):
            self.all_entries, self.category_icons = data
            self._organize_entries()
            self._update_sidebar()
            self._filter_and_display_entries()
            
        def on_error(err: Exception, tb: str):
            logger.error(f"Failed to load initial data: {err}\nTraceback:\n{tb}")
            CustomMessageBox.information(self.main_app_window, t.get('error_title_generic'), str(err))
        
        task_manager.run_in_background(
            lambda: (self.data_manager.get_entries(), self.data_manager.get_category_icons()),
            on_success=on_success,
            on_error=on_error
        )

    def _organize_entries(self) -> None:
        self.entries_by_name = defaultdict(list)
        for entry in self.all_entries:
            self.entries_by_name[entry['name']].append(entry)

    def _update_sidebar(self) -> None:
        all_categories = sorted(list(set(e['category'] for e in self.all_entries if e['category'])))
        self.sidebar_view.populate_categories(all_categories, self.category_icons)
        self.sidebar_view.set_active_category(self.current_category)

    def _filter_and_display_entries(self) -> None:
        if self.current_category == t.get('all_categories'):
            filtered_by_cat = self.all_entries
        else:
            filtered_by_cat = [e for e in self.all_entries if e['category'] == self.current_category]

        if self.current_search_term:
            term = self.current_search_term.lower()
            filtered_by_search = [
                entry for entry in filtered_by_cat if (
                    term in entry.get('name', '').lower() or
                    term in entry.get('category', '').lower() or
                    term in entry.get('details', {}).get('username', '').lower() or
                    term in entry.get('details', {}).get('url', '').lower()
                )
            ]
        else:
            filtered_by_search = filtered_by_cat
        
        entries_to_display = defaultdict(list)
        for entry in filtered_by_search:
            entries_to_display[entry['name']].append(entry)
            
        current_selection = self.content_view.get_selected_entry_name()
        self.content_view.populate_entry_list(entries_to_display, current_selection)
        
        current_item = self.content_view.entry_list.currentItem()
        self.on_entry_selected(current_item, None)
        
    def on_category_selected(self, category_name: str) -> None:
        self.current_category = category_name
        self.sidebar_view.set_active_category(category_name)
        self._filter_and_display_entries()

    def on_search_term_changed(self, term: str) -> None:
        self.current_search_term = term
        self._filter_and_display_entries()

    def on_entry_selected(self, current_item: Optional[QListWidgetItem], previous_item: Optional[QListWidgetItem]) -> None:
        if not current_item:
            self.content_view.details_view.clear_details()
            return

        selected_name = current_item.data(Qt.ItemDataRole.UserRole)
        
        if selected_name and selected_name in self.entries_by_name:
            self.content_view.details_view.display_entry_group(self.entries_by_name[selected_name])
        else:
            self.content_view.details_view.clear_details()

    def on_delete_entry(self, entry_id: int) -> None:
        entry_to_delete = next((e for e in self.all_entries if e['id'] == entry_id), None)
        if not entry_to_delete: return
        
        if entry_to_delete.get('details', {}).get('totp_secret'):
            CustomMessageBox.information(
                self.main_app_window,
                t.get('2fa_delete_denied_title'),
                t.get('2fa_delete_denied_message')
            )
            return

        reply = CustomMessageBox.question(
            self.main_app_window,
            t.get('msg_title_confirm_delete'),
            t.get('msg_confirm_delete', name=entry_to_delete['name'])
        )
        if reply == QDialog.DialogCode.Accepted:
            self.data_manager.delete_entry(entry_id)
            self.load_initial_data()
    
    def _open_add_dialog(self) -> None:
        dialog = AddEditDialog(self.main_app_window)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                CustomMessageBox.information(self.main_app_window, t.get('msg_title_input_error'), t.get('msg_empty_name_error'))
                return
            
            self.data_manager.save_entry_and_category_icon(
                entry_id=None,
                category=data['category'],
                name=data['name'],
                details=data['details'],
                category_icon_data=dialog.new_category_icon_data
            )
            self.load_initial_data()
    
    def _open_edit_dialog(self, entry_id: int) -> None:
        entry_to_edit = next((e for e in self.all_entries if e['id'] == entry_id), None)
        if not entry_to_edit: return
        
        dialog = AddEditDialog(self.main_app_window, entry_to_edit)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                CustomMessageBox.information(self.main_app_window, t.get('msg_title_input_error'), t.get('msg_empty_name_error'))
                return
            
            self.data_manager.save_entry_and_category_icon(
                entry_id=entry_id,
                category=data['category'],
                name=data['name'],
                details=data['details'],
                category_icon_data=dialog.new_category_icon_data
            )
            self.load_initial_data()
    
    def _open_generator_dialog(self) -> None:
        GeneratorWindow(self.main_app_window).exec()

    def _open_settings_dialog(self) -> None:
        dialog = SettingsDialog(self.main_app_window)
        
        dialog.change_password_requested.connect(self._handle_change_password)
        dialog.import_requested.connect(self.io_controller.handle_import)
        dialog.export_requested.connect(lambda: self.io_controller.handle_export(self.all_entries))

        original_lang = t._language
        original_theme = get_current_theme()

        if dialog.exec():
            selected_lang = dialog.get_selected_language()
            selected_theme = dialog.get_selected_theme()

            settings_changed = (selected_lang != original_lang) or \
                               (selected_theme != original_theme)

            if settings_changed:
                settings = load_settings()
                settings['language'] = selected_lang
                settings['theme'] = selected_theme
                save_settings(settings)
            
            if selected_theme != original_theme:
                self._apply_theme(selected_theme)

            if selected_lang != original_lang:
                t.set_language(selected_lang)
                self.main_app_window.retranslate_ui()

    def _apply_theme(self, theme_name: str) -> None:
        app = QApplication.instance()
        if not app: return
        apply_theme(app, theme_name)
        
        for window in app.topLevelWindows():
            if isinstance(window, QWidget):
                window.style().unpolish(window)
                window.style().polish(window)
        
        logger.info(f"Theme '{theme_name}' applied and UI refreshed.")

    def _handle_change_password(self):
        dialog = ChangePasswordDialog(self.main_app_window)
        if not dialog.exec(): return

        passwords, reason = dialog.get_passwords()
        
        error_map = {
            "empty": "msg_pass_change_fail_empty",
            "mismatch": "msg_pass_change_fail_mismatch",
            "weak": "msg_pass_change_fail_weak"
        }
        if reason in error_map:
            CustomMessageBox.information(self.main_app_window, t.get('msg_title_pass_change_fail'), t.get(error_map[reason]))
            return

        if passwords is None: return
        old_pass, new_pass = passwords

        def on_success(success: bool):
            if success:
                CustomMessageBox.information(self.main_app_window, t.get('msg_title_pass_change_success'), t.get('msg_pass_change_success'))
            else:
                CustomMessageBox.information(self.main_app_window, t.get('msg_title_pass_change_fail'), t.get('msg_pass_change_fail_old_wrong'))
        
        def on_error(err: Exception, tb: str):
            logger.error(f"Failed to change password: {err}\nTraceback:\n{tb}")
            CustomMessageBox.information(self.main_app_window, t.get('error_title_generic'), str(err))

        task_manager.run_in_background(
            self.data_manager.change_master_password, on_success=on_success,
            on_error=on_error, old_password=old_pass, new_password=new_pass
        )
    
    def handle_language_change(self):
        self.current_category = t.get('all_categories')
        self.load_initial_data()