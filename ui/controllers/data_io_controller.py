# ui/controllers/data_io_controller.py

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, List, Dict, Any, Callable, Optional, Tuple

from PyQt6.QtWidgets import (QFileDialog, QDialog, QMainWindow)
from PyQt6.QtCore import QObject

from core.data_handler import DataHandler
from core.icon_fetcher import IconFetcher
from language import t
from ..dialogs.message_box_dialog import CustomMessageBox
from ..dialogs.password_prompt_dialog import PasswordPromptDialog
from ..task_manager import task_manager

if TYPE_CHECKING:
    from core.database import DataManager

logger = logging.getLogger(__name__)

class DataIOController(QObject):
    def __init__(
        self,
        main_window: QMainWindow,
        data_manager: 'DataManager',
        on_finish_callback: Callable[[], None]
    ):
        super().__init__()
        self.main_window = main_window
        self.data_manager = data_manager
        self.on_finish_callback = on_finish_callback

    def handle_import(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self.main_window, t.get('dialog_import_title'), "", t.get('dialog_import_files'))
        if not file_path: return

        if CustomMessageBox.question(self.main_window, t.get('msg_import_confirm_title'), t.get('msg_import_confirm')) != QDialog.DialogCode.Accepted: return

        password: Optional[str] = None
        if os.path.splitext(file_path)[1].lower() == '.skey':
            password, ok = PasswordPromptDialog.getPassword(self.main_window)
            if not ok:
                logger.warning("Import cancelled by user (no password provided for .skey).")
                return

        def on_import_error(err: Exception, tb: str):
            CustomMessageBox.information(self.main_window, t.get('msg_import_fail_title'), t.get('msg_import_fail', error=str(err)))

        def on_parse_success(parsed_entries: List[Dict[str, Any]]):
            if not parsed_entries:
                self.on_finish_callback()
                return
            task_manager.run_in_background(
                task=self._fetch_icons_for_entries,
                on_success=on_fetch_icons_success,
                on_error=on_import_error,
                entries=parsed_entries
            )

        def on_fetch_icons_success(processed_entries: List[Dict[str, Any]]):
            task_manager.run_in_background(
                task=self.data_manager.save_multiple_entries,
                on_success=on_db_save_success,
                on_error=on_import_error,
                entries=processed_entries
            )
            
        def on_db_save_success(result: Tuple[int, int, int]):
            added_count, updated_count, skipped_count = result
            CustomMessageBox.information(
                self.main_window, 
                t.get('msg_import_success_title'), 
                t.get('msg_import_success', added_count=added_count, updated_count=updated_count, skipped_count=skipped_count)
            )
            self.on_finish_callback()

        task_manager.run_in_background(
            task=DataHandler.import_from_file,
            on_success=on_parse_success,
            on_error=on_import_error,
            file_path=file_path,
            password=password
        )

    def _fetch_one_icon(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        details = entry.get('details', {})
        url = details.get('url')
        if url and not details.get('icon_data'):
            icon_data = IconFetcher.fetch_icon_from_url(url)
            if icon_data: details['icon_data'] = icon_data
        return entry

    def _fetch_icons_for_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        entries_to_process = [e for e in entries if e.get('details', {}).get('url') and not e.get('details', {}).get('icon_data')]
        if not entries_to_process: return entries
        with ThreadPoolExecutor(max_workers=10) as executor:
            processed_results = list(executor.map(self._fetch_one_icon, entries_to_process))
        processed_map = {item['name']: item for item in processed_results}
        final_entries = [processed_map.get(e['name'], e) for e in entries]
        return final_entries

    def handle_export(self, all_entries: List[Dict[str, Any]]) -> None:
        file_path, selected_filter = QFileDialog.getSaveFileName(self.main_window, t.get('dialog_export_title'), "oracipher_export", t.get('dialog_export_filter'))
        if not file_path: return

        is_csv = 'csv' in selected_filter.lower()
        
        def on_error(err: Exception, tb: str):
            CustomMessageBox.information(self.main_window, t.get('msg_export_fail_title'), t.get('msg_export_fail', error=str(err)))
            
        def on_success(content: Any):
            mode = 'w' if isinstance(content, str) else 'wb'
            try:
                with open(file_path, mode, encoding='utf-8' if mode == 'w' else None) as f: f.write(content)
                CustomMessageBox.information(self.main_window, t.get('msg_export_success_title'), t.get('msg_export_success', count=len(all_entries), path=file_path))
            except Exception as e: on_error(e, "")
            
        if not is_csv:
            task_manager.run_in_background(DataHandler.export_to_encrypted_json, on_success=on_success, on_error=on_error, entries=all_entries, crypto_handler=self.data_manager.crypto)
            return

        if CustomMessageBox.question(self.main_window, t.get('warning_unsecure_export_title'), t.get('warning_unsecure_export_text')) != QDialog.DialogCode.Accepted:
            return
        
        reply = CustomMessageBox.question(self.main_window, t.get('warning_include_totp_title'), t.get('warning_include_totp_text'))
        
        if reply == QDialog.DialogCode.Rejected:
             return

        include_totp = (reply == QDialog.DialogCode.Accepted)
        
        task_manager.run_in_background(DataHandler.export_to_csv, on_success=on_success, on_error=on_error, entries=all_entries, include_totp=include_totp)