# ui/controllers/main_window_controller.py

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, List, Dict, Any, Optional

from PyQt6.QtWidgets import QDialog, QApplication, QMainWindow, QWidget, QListWidgetItem
from PyQt6.QtCore import QObject, Qt, pyqtSignal, QTimer

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
    settings_changed = pyqtSignal()

    def __init__(
        self,
        main_app_window: QMainWindow,
        sidebar_view: "SidebarView",
        content_view: "MainContentView",
        data_manager: "DataManager",
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
        self.current_category: str = t.get("all_categories")
        self.current_search_term: str = ""
        
        # --- MODIFICATION START: Add an attribute to hold active dialog references ---
        self.active_dialog: Optional[QDialog] = None
        # --- MODIFICATION END ---
        
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
            CustomMessageBox.information(
                self.main_app_window, t.get("error_title_generic"), str(err)
            )
        task_manager.run_in_background(
            lambda: (
                self.data_manager.get_entries(),
                self.data_manager.get_category_icons(),
            ),
            on_success=on_success,
            on_error=on_error,
        )

    def _organize_entries(self) -> None:
        self.entries_by_name = defaultdict(list)
        for entry in self.all_entries:
            self.entries_by_name[entry["name"]].append(entry)

    def _update_sidebar(self) -> None:
        all_categories = sorted(
            list(set(e["category"] for e in self.all_entries if e["category"]))
        )
        self.sidebar_view.populate_categories(all_categories, self.category_icons)
        self.sidebar_view.set_active_category(self.current_category)
        self.sidebar_view.retranslate_ui()

    def _filter_and_display_entries(self) -> None:
        filtered_by_cat = self.all_entries
        if self.current_category != t.get("all_categories"):
            filtered_by_cat = [
                e for e in self.all_entries if e["category"] == self.current_category
            ]
        
        filtered_entries = filtered_by_cat
        if self.current_search_term:
            term = self.current_search_term.lower()
            filtered_entries = [
                entry for entry in filtered_by_cat
                if (
                    term in entry.get("name", "").lower() or
                    term in entry.get("details", {}).get("username", "").lower() or
                    term in entry.get("details", {}).get("url", "").lower()
                )
            ]

        entries_to_display = defaultdict(list)
        for entry in filtered_entries:
            entries_to_display[entry["name"]].append(entry)
        
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

    def on_entry_selected(
        self, current_item: Optional[QListWidgetItem], previous_item: Optional[QListWidgetItem]
    ) -> None:
        if not current_item:
            self.content_view.details_view.clear_details()
            return
        selected_name = current_item.data(Qt.ItemDataRole.UserRole)
        if selected_name in self.entries_by_name:
            self.content_view.details_view.display_entry_group(
                self.entries_by_name[selected_name]
            )
        else:
            self.content_view.details_view.clear_details()

    def on_delete_entry(self, entry_id: int) -> None:
        entry_to_delete = next((e for e in self.all_entries if e["id"] == entry_id), None)
        if not entry_to_delete: return

        if entry_to_delete.get("details", {}).get("totp_secret"):
            CustomMessageBox.information(
                self.main_app_window,
                t.get("2fa_delete_denied_title"),
                t.get("2fa_delete_denied_message"),
            )
            return

        reply = CustomMessageBox.question(
            self.main_app_window,
            t.get("msg_title_confirm_delete"),
            t.get("msg_confirm_delete", name=entry_to_delete["name"]),
        )
        if reply == QDialog.DialogCode.Accepted:
            self.data_manager.delete_entry(entry_id)
            self.load_initial_data()
    
    # --- MODIFICATION START: Use instance attribute for the dialog ---
    def _open_add_dialog(self) -> None:
        self.active_dialog = AddEditDialog(self.main_app_window)
        if self.active_dialog.exec():
            data = self.active_dialog.get_data()
            if not data["name"]:
                CustomMessageBox.information(
                    self.main_app_window, t.get("msg_title_input_error"), t.get("msg_empty_name_error"),
                )
                return
            self.data_manager.save_entry_and_category_icon(
                entry_id=None,
                category=data["category"],
                name=data["name"],
                details=data["details"],
                category_icon_data=self.active_dialog.new_category_icon_data,
            )
            self.load_initial_data()
        self.active_dialog = None # Release the reference
    # --- MODIFICATION END ---

    # --- MODIFICATION START: Use instance attribute for the dialog ---
    def _open_edit_dialog(self, entry_id: int) -> None:
        entry_to_edit = next((e for e in self.all_entries if e["id"] == entry_id), None)
        if not entry_to_edit: return

        self.active_dialog = AddEditDialog(self.main_app_window, entry_to_edit)
        if self.active_dialog.exec():
            data = self.active_dialog.get_data()
            if not data["name"]:
                CustomMessageBox.information(
                    self.main_app_window, t.get("msg_title_input_error"), t.get("msg_empty_name_error"),
                )
                return
            self.data_manager.save_entry_and_category_icon(
                entry_id=entry_id,
                category=data["category"],
                name=data["name"],
                details=data["details"],
                category_icon_data=self.active_dialog.new_category_icon_data,
            )
            self.load_initial_data()
        self.active_dialog = None # Release the reference
    # --- MODIFICATION END ---

    # --- MODIFICATION START: Use instance attribute for the dialog ---
    def _open_generator_dialog(self) -> None:
        self.active_dialog = GeneratorWindow(self.main_app_window)
        self.active_dialog.exec()
        self.active_dialog = None # Release the reference
    # --- MODIFICATION END ---

    # --- MODIFICATION START: Use instance attribute for the dialog ---
    def _open_settings_dialog(self) -> None:
        self.active_dialog = SettingsDialog(self.main_app_window)
        self.active_dialog.change_password_requested.connect(self._handle_change_password)
        self.active_dialog.import_requested.connect(self.io_controller.handle_import)
        self.active_dialog.export_requested.connect(
            lambda: self.io_controller.handle_export(self.all_entries)
        )
        self.active_dialog.theme_changed.connect(self._apply_theme)
        
        original_theme = get_current_theme()
        original_settings = load_settings()
        
        def on_cancel():
            if get_current_theme() != original_theme:
                self._apply_theme(original_theme)
                
        self.active_dialog.rejected.connect(on_cancel)
        
        if self.active_dialog.exec():
            settings_changed = False
            new_settings = original_settings.copy()
            
            selected_lang = self.active_dialog.get_selected_language()
            if new_settings["language"] != selected_lang:
                new_settings["language"] = selected_lang
                settings_changed = True
                
            selected_theme = self.active_dialog.get_selected_theme()
            if new_settings["theme"] != selected_theme:
                new_settings["theme"] = selected_theme
                settings_changed = True
                
            auto_lock_enabled, auto_lock_minutes = self.active_dialog.get_auto_lock_settings()
            if (
                new_settings["auto_lock_enabled"] != auto_lock_enabled or
                new_settings["auto_lock_timeout_minutes"] != auto_lock_minutes
            ):
                new_settings["auto_lock_enabled"] = auto_lock_enabled
                new_settings["auto_lock_timeout_minutes"] = auto_lock_minutes
                settings_changed = True

            if settings_changed:
                save_settings(new_settings)
                self.settings_changed.emit()
                if new_settings["language"] != original_settings["language"]:
                    t.set_language(new_settings["language"])
                    self.handle_language_change()

        self.active_dialog = None # Release the reference
    # --- MODIFICATION END ---

    def _apply_theme(self, theme_name: str) -> None:
        app = QApplication.instance()
        if not isinstance(app, QApplication): return
        apply_theme(app, theme_name)
        for window in app.topLevelWindows():
            if isinstance(window, QWidget):
                style = window.style()
                if style:
                    style.unpolish(window)
                    style.polish(window)

    # --- MODIFICATION START: Use instance attribute for the dialog AND handle detailed feedback ---
    def _handle_change_password(self):
        self.active_dialog = ChangePasswordDialog(self.main_app_window)
        if not self.active_dialog.exec(): 
            self.active_dialog = None
            return
            
        passwords, reason = self.active_dialog.get_passwords()
        self.active_dialog = None # Release the reference
        
        if reason:
            error_map = {
                "empty": "msg_pass_change_fail_empty",
                "mismatch": "msg_pass_change_fail_mismatch",
            }
            if reason in error_map:
                message = t.get(error_map[reason])
            elif reason.startswith("weak:"):
                # Extract the specific feedback from zxcvbn
                message = reason.split(":", 1)[1]
            else: # Fallback for 'weak' without specific feedback from older code path
                message = t.get("msg_pass_change_fail_weak")
                
            CustomMessageBox.information(
                self.main_app_window, t.get("msg_title_pass_change_fail"), message,
            )
            return
            
        if passwords is None: return
        
        old_pass, new_pass = passwords
        def on_success(success: bool):
            if success:
                CustomMessageBox.information(
                    self.main_app_window, t.get("msg_title_pass_change_success"), t.get("msg_pass_change_success"),
                )
            else:
                CustomMessageBox.information(
                    self.main_app_window, t.get("msg_title_pass_change_fail"), t.get("msg_pass_change_fail_old_wrong"),
                )
        task_manager.run_in_background(
            self.data_manager.change_master_password,
            on_success=on_success,
            on_error=lambda err, tb: CustomMessageBox.information(self.main_app_window, t.get("error_title_generic"), str(err)),
            old_password=old_pass,
            new_password=new_pass,
        )
    # --- MODIFICATION END ---

    def handle_language_change(self):
        self.current_category = t.get("all_categories")
        self.load_initial_data()