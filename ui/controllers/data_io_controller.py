# ui/controllers/data_io_controller.py

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, List, Dict, Any, Callable, Optional, Tuple

from PyQt6.QtWidgets import QFileDialog, QDialog, QMainWindow
from PyQt6.QtCore import QObject

from core.data_handler import DataHandler
from core.icon_fetcher import IconFetcher
from language import t
from ..dialogs.message_box_dialog import CustomMessageBox
from ..dialogs.password_prompt_dialog import PasswordPromptDialog
from ..task_manager import task_manager

if TYPE_CHECKING:
    from core.database import DataManager
    from core.data_handler import Exporter # 引入Exporter类型提示

logger = logging.getLogger(__name__)


class DataIOController(QObject):
    def __init__(
        self,
        main_window: QMainWindow,
        data_manager: "DataManager",
        on_finish_callback: Callable[[], None],
    ):
        super().__init__()
        self.main_window = main_window
        self.data_manager = data_manager
        self.on_finish_callback = on_finish_callback

    def handle_import(self) -> None:
        # vvv MODIFICATION START vvv
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            t.get("dialog_import_title"),
            "",
            DataHandler.get_import_filter(),  # 使用动态生成的过滤器
        )
        # ^^^ MODIFICATION END ^^^

        if not file_path:
            return

        if (
            CustomMessageBox.question(
                self.main_window,
                t.get("msg_import_confirm_title"),
                t.get("msg_import_confirm"),
            )
            != QDialog.DialogCode.Accepted
        ):
            return

        password: Optional[str] = None
        file_ext = os.path.splitext(file_path)[1].lower()

        # vvv MODIFICATION START vvv
        # 简化密码逻辑：现在只需要检查扩展名是否在需要密码的导入器列表中
        needs_password = any(
            file_ext in importer.extensions and importer.requires_password
            for importer in DataHandler._IMPORTERS.values()
        )
        if needs_password:
        # ^^^ MODIFICATION END ^^^
            # 根据不同的文件类型生成不同的提示文本
            if file_ext == ".pher":
                instruction = t.get("dialog_input_password_label_pher")
            elif file_ext == ".skey":
                instruction = t.get("dialog_input_password_label_skey")
            elif file_ext == ".spass":
                instruction = t.get("dialog_input_password_label_spass")
            else:
                # 提供一个通用的后备提示
                instruction = "Please enter the password for the selected file:"

            password, ok = PasswordPromptDialog.getPassword(
                self.main_window, instruction_text=instruction
            )
            if not ok:
                logger.warning(
                    f"Import cancelled by user (no password provided for {file_ext})."
                )
                return

        def on_import_error(err: Exception, tb: str):
            error_key = "msg_import_fail_message"
            if isinstance(err, FileNotFoundError):
                error_message = t.get("error_import_file_not_found")
            elif isinstance(err, PermissionError):
                error_message = t.get("error_import_permission_denied")
            elif isinstance(err, ValueError):
                error_message = t.get("error_import_parsing_failed", error=str(err))
            else:
                error_message = t.get(error_key, error=str(err))
            CustomMessageBox.information(
                self.main_window, t.get("msg_import_fail_title"), error_message
            )

        def on_parse_success(parsed_entries: List[Dict[str, Any]]):
            if not parsed_entries:
                self.on_finish_callback()
                return
            task_manager.run_in_background(
                task=self._fetch_icons_for_entries,
                on_success=on_fetch_icons_success,
                on_error=on_import_error,
                entries=parsed_entries,
            )

        def on_fetch_icons_success(processed_entries: List[Dict[str, Any]]):
            task_manager.run_in_background(
                task=self.data_manager.save_multiple_entries,
                on_success=on_db_save_success,
                on_error=on_import_error,
                entries=processed_entries,
            )

        def on_db_save_success(result: Tuple[int, int, int]):
            added_count, updated_count, skipped_count = result
            CustomMessageBox.information(
                self.main_window,
                t.get("msg_import_success_title"),
                t.get(
                    "msg_import_success",
                    added_count=added_count,
                    updated_count=updated_count,
                    skipped_count=skipped_count,
                ),
            )
            self.on_finish_callback()

        task_manager.run_in_background(
            task=DataHandler.import_from_file, # 调用统一的导入方法
            on_success=on_parse_success,
            on_error=on_import_error,
            file_path=file_path,
            password=password,
        )

    def _fetch_one_icon(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        details = entry.get("details", {})
        url = details.get("url")
        if url and not details.get("icon_data"):
            icon_data = IconFetcher.fetch_icon_from_url(url)
            if icon_data:
                details["icon_data"] = icon_data
        return entry

    def _fetch_icons_for_entries(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        entries_to_process = [
            e
            for e in entries
            if e.get("details", {}).get("url")
            and not e.get("details", {}).get("icon_data")
        ]
        if not entries_to_process:
            return entries
        with ThreadPoolExecutor(max_workers=10) as executor:
            processed_results = list(
                executor.map(self._fetch_one_icon, entries_to_process)
            )
        processed_map = {item["name"]: item for item in processed_results}
        final_entries = [processed_map.get(e["name"], e) for e in entries]
        return final_entries

    def handle_export(self, all_entries: List[Dict[str, Any]]) -> None:
        # vvv MODIFICATION START vvv
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.main_window,
            t.get("dialog_export_title"),
            "oracipher_export.pher",
            DataHandler.get_export_filter(), # 使用动态生成的过滤器
        )
        # ^^^ MODIFICATION END ^^^

        if not file_path:
            return

        # vvv MODIFICATION START: 简化导出逻辑 vvv
        # 从选择的过滤器中找到对应的导出器
        selected_exporter: Optional["Exporter"] = next(
            (exporter for exporter in DataHandler._EXPORTERS.values() if exporter.name == selected_filter),
            None
        )

        if not selected_exporter:
            logger.error(f"No exporter found for filter: {selected_filter}")
            return

        kwargs_for_exporter = {'entries': all_entries}

        # 处理需要密码的导出格式 (如 Samsung Pass)
        if selected_exporter.requires_password:
            password, ok = PasswordPromptDialog.getPassword(
                self.main_window, instruction_text=t.get("dialog_input_password_label_spass")
            )
            if not ok or not password:
                logger.warning(f"Export to {selected_exporter.name} cancelled by user.")
                return
            kwargs_for_exporter['password'] = password

        # 处理特殊的CSV导出选项
        if selected_exporter.extension == ".csv":
            if (
                CustomMessageBox.question(
                    self.main_window,
                    t.get("warning_unsecure_export_title"),
                    t.get("warning_unsecure_export_text"),
                )
                != QDialog.DialogCode.Accepted
            ):
                return

            reply = CustomMessageBox.question(
                self.main_window,
                t.get("warning_include_totp_title"),
                t.get("warning_include_totp_text"),
            )

            if reply == QDialog.DialogCode.Rejected:
                return
                
            kwargs_for_exporter['include_totp'] = (reply == QDialog.DialogCode.Accepted)

        # 添加 crypto_handler (如果需要，例如导出为.pher格式)
        if selected_exporter.extension == ".pher":
            kwargs_for_exporter['crypto_handler'] = self.data_manager.crypto

        def on_error(err: Exception, tb: str):
            error_message = t.get("msg_export_fail", error=str(err))
            CustomMessageBox.information(
                self.main_window, t.get("msg_export_fail_title"), error_message
            )

        def on_success(content: Any):
            mode = "w" if isinstance(content, str) else "wb"
            try:
                with open(
                    file_path, mode, encoding="utf-8" if mode == "w" else None
                ) as f:
                    f.write(content)
                CustomMessageBox.information(
                    self.main_window,
                    t.get("msg_export_success_title"),
                    t.get("msg_export_success", count=len(all_entries), path=file_path),
                )
            except Exception as e:
                on_error(e, "")

        task_manager.run_in_background(
            selected_exporter.handler,
            on_success=on_success,
            on_error=on_error,
            **kwargs_for_exporter
        )