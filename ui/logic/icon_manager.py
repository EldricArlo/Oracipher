# ui/logic/icon_manager.py

import base64
import logging
from typing import Optional, TYPE_CHECKING

from PyQt6.QtWidgets import QFileDialog, QWidget, QPushButton, QLineEdit

from core.icon_fetcher import IconFetcher
from language import t
from ..dialogs.message_box_dialog import CustomMessageBox
from ..task_manager import task_manager

logger = logging.getLogger(__name__)

class IconManager:
    """
    负责处理添加/编辑对话框中所有与条目图标相关的逻辑。
    """
    def __init__(
        self,
        parent_widget: QWidget,
        icon_preview_button: QPushButton,
        url_input: QLineEdit
    ):
        self.parent = parent_widget
        self.icon_preview_button = icon_preview_button
        self.url_input = url_input
        self.current_icon_base64: Optional[str] = None

    def set_initial_icon(self, icon_base64: Optional[str]) -> None:
        """
        设置并显示初始图标。
        """
        self.current_icon_base64 = icon_base64 or IconFetcher.get_default_icon_base64()
        self.update_icon_preview()

    def update_icon_preview(self) -> None:
        """根据当前的Base64数据更新图标预览按钮的图标。"""
        icon = IconFetcher.icon_from_base64(self.current_icon_base64)
        self.icon_preview_button.setIcon(icon)

    def fetch_icon_from_url(self) -> None:
        """
        从URL输入框中的地址异步抓取网站图标。
        """
        url = self.url_input.text().strip()
        if not url:
            CustomMessageBox.information(self.parent, t.get('msg_title_input_error'), t.get('error_url_required'))
            return
        
        self.icon_preview_button.setEnabled(False)
        
        def on_success(fetched_icon_base64: Optional[str]):
            if fetched_icon_base64:
                self.current_icon_base64 = fetched_icon_base64
                logger.info(f"Successfully fetched icon for URL: {url}")
            else:
                CustomMessageBox.information(self.parent, t.get('error_title_generic'), t.get('error_fetch_failed'))
                logger.warning(f"Failed to fetch icon for URL: {url}")
            
            self.update_icon_preview()
            self.icon_preview_button.setEnabled(True)

        def on_error(err: Exception, tb: str):
            CustomMessageBox.information(self.parent, t.get('error_title_generic'), t.get('error_fetch_failed'))
            logger.error(f"Error fetching icon: {err}\n{tb}")
            self.icon_preview_button.setEnabled(True)

        task_manager.run_in_background(
            task=IconFetcher.fetch_icon_from_url,
            on_success=on_success,
            on_error=on_error,
            url=url
        )

    def select_icon_from_file(self) -> None:
        """打开文件对话框，让用户从本地选择一个图标文件。"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, 
            t.get('dialog_select_icon'), 
            "",
            f"{t.get('dialog_image_files')} (*.png *.jpg *.jpeg *.ico *.svg)"
        )
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    self.current_icon_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                self.update_icon_preview()
                logger.info(f"Successfully loaded custom icon from: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load custom icon: {e}", exc_info=True)
                CustomMessageBox.information(self.parent, t.get('error_title_generic'), t.get('error_loading_icon'))
    
    def get_icon_data(self) -> Optional[str]:
        """返回当前管理的图标的Base64数据。"""
        return self.current_icon_base64