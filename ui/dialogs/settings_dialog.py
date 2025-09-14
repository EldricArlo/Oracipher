# ui/dialogs/settings_dialog.py

import logging
from typing import Optional

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QWidget,
                             QTextEdit, QTabWidget, QComboBox)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QEvent, QObject
from PyQt6.QtGui import QMouseEvent, QIcon

from language import t
from config import load_settings
from utils.paths import resource_path
from ..theme_manager import get_current_theme

logger = logging.getLogger(__name__)


class PositionAwareComboBox(QComboBox):
    """
    一个自定义QComboBox，在弹出菜单显示前会发出一个信号，
    用于解决某些平台下窗口位置跳动的问题。
    """
    popupAboutToShow = pyqtSignal()

    def showPopup(self) -> None:
        self.popupAboutToShow.emit()
        super().showPopup()


class SettingsDialog(QDialog):
    change_password_requested = pyqtSignal()
    import_requested = pyqtSignal()
    export_requested = pyqtSignal()
    theme_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumSize(600, 550)
        self.drag_pos: QPoint = QPoint()

        self._last_pos: Optional[QPoint] = None

        self.init_ui()
        logger.debug("SettingsDialog opened.")

    def _save_position(self) -> None:
        """在下拉菜单弹出前，保存当前窗口的位置。"""
        self._last_pos = self.pos()

    def _restore_position(self) -> None:
        """在下拉菜单关闭后，如果位置发生变化，则恢复它。"""
        if self._last_pos is not None and self.pos() != self._last_pos:
            self.move(self._last_pos)
        self._last_pos = None

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """
        事件过滤器，用于捕获下拉菜单窗口的 Hide 事件。
        """
        if event.type() == QEvent.Type.Hide:
            if hasattr(watched, 'view') and hasattr(watched.view(), 'window'):
                if watched is self.lang_combo or watched is self.theme_combo:
                    self._restore_position()

        return super().eventFilter(watched, event)

    def init_ui(self) -> None:
        container = QFrame(self); container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25); main_layout.setSpacing(15)

        title_label = QLabel(t.get('settings_title')); title_label.setObjectName("dialogTitle")

        self.tabs = QTabWidget()
        settings_tab, instructions_tab = QWidget(), QWidget()
        self.tabs.addTab(settings_tab, t.get('tab_settings')); self.tabs.addTab(instructions_tab, t.get('tab_instructions'))

        self._init_settings_tab(settings_tab)
        self._init_instructions_tab(instructions_tab)

        button_layout = QHBoxLayout(); button_layout.addStretch()
        done_button = QPushButton(t.get('button_done')); done_button.setObjectName("saveButton")
        done_button.clicked.connect(self.accept)
        button_layout.addWidget(done_button)

        main_layout.addWidget(title_label); main_layout.addWidget(self.tabs); main_layout.addLayout(button_layout)

        dialog_layout = QVBoxLayout(self); dialog_layout.addWidget(container)

    def _create_section_widget(self, title_text: str) -> tuple[QWidget, QVBoxLayout]:
        section_container = QWidget()
        section_layout = QVBoxLayout(section_container)
        section_layout.setContentsMargins(0, 0, 0, 0); section_layout.setSpacing(10)
        title_label = QLabel(title_text); title_label.setObjectName("sectionTitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_frame = QFrame(); card_frame.setObjectName("settingsGroupFrame")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(20, 20, 20, 20); card_layout.setSpacing(20)
        section_layout.addWidget(title_label); section_layout.addWidget(card_frame)
        return section_container, card_layout

    def _create_setting_row(self, title_text: str, desc_text: str, control_widget: QWidget) -> QWidget:
        row_widget = QWidget(); row_widget.setObjectName("settingRow")
        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(20)
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0); text_layout.setSpacing(2)
        title_label = QLabel(title_text); title_label.setObjectName("settingTitleLabel")
        desc_label = QLabel(desc_text); desc_label.setObjectName("settingDescLabel"); desc_label.setWordWrap(True)
        text_layout.addWidget(title_label); text_layout.addWidget(desc_label)
        layout.addWidget(text_widget, 1)
        layout.addWidget(control_widget, 0, Qt.AlignmentFlag.AlignVCenter)
        return row_widget

    def _init_settings_tab(self, parent_tab: QWidget) -> None:
        settings_layout = QVBoxLayout(parent_tab)
        settings_layout.setSpacing(25); settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        general_section, general_card_layout = self._create_section_widget(t.get('settings_section_general'))

        self.lang_combo = PositionAwareComboBox(); self.lang_combo.setFixedWidth(200)
        
        icon_path = str(resource_path("ui/assets/icons/chevron-down.svg")).replace('\\', '/')
        self.lang_combo.setStyleSheet(f"QComboBox::down-arrow {{ image: url({icon_path}); width: 14px; height: 14px; }}")
        
        available_languages = t.get_available_languages()
        current_lang_code = load_settings().get('language', 'zh_CN')
        for code, name in available_languages.items(): self.lang_combo.addItem(name, userData=code)
        index = self.lang_combo.findData(current_lang_code)
        if index != -1: self.lang_combo.setCurrentIndex(index)

        self.lang_combo.popupAboutToShow.connect(self._save_position)
        if self.lang_combo.view() and self.lang_combo.view().window():
             self.lang_combo.view().window().installEventFilter(self)

        lang_row = self._create_setting_row(t.get('settings_lang_title'), t.get('settings_lang_desc'), self.lang_combo)
        general_card_layout.addWidget(lang_row)

        self.theme_combo = PositionAwareComboBox(); self.theme_combo.setFixedWidth(200)
        self.theme_combo.addItem(t.get('theme_light'), userData="light")
        self.theme_combo.addItem(t.get('theme_dark'), userData="dark")
        current_theme = get_current_theme()
        theme_index = self.theme_combo.findData(current_theme)
        if theme_index != -1: self.theme_combo.setCurrentIndex(theme_index)
        self.theme_combo.currentTextChanged.connect(lambda: self.theme_changed.emit(self.get_selected_theme()))

        self.theme_combo.popupAboutToShow.connect(self._save_position)
        if self.theme_combo.view() and self.theme_combo.view().window():
            self.theme_combo.view().window().installEventFilter(self)

        theme_row = self._create_setting_row(t.get('settings_theme_title'), t.get('settings_theme_desc'), self.theme_combo)
        general_card_layout.addWidget(theme_row)

        settings_layout.addWidget(general_section)

        security_section, security_card_layout = self._create_section_widget(t.get('settings_section_security'))
        change_pass_button = QPushButton(t.get('settings_change_pass_button')); change_pass_button.setObjectName("inlineButton")
        change_pass_button.setFixedWidth(200)
        change_pass_button.clicked.connect(self.change_password_requested.emit)
        pass_row = self._create_setting_row(t.get('change_pass_title'), t.get('settings_change_pass_desc'), change_pass_button)
        security_card_layout.addWidget(pass_row)
        settings_layout.addWidget(security_section)

        data_section, data_card_layout = self._create_section_widget(t.get('settings_section_data'))
        import_button = QPushButton(f" {t.get('button_import')}"); import_button.setIcon(QIcon(str(resource_path("ui/assets/icons/import.svg"))))
        import_button.setFixedWidth(150); import_button.clicked.connect(self.import_requested.emit)
        export_button = QPushButton(f" {t.get('button_export')}"); export_button.setIcon(QIcon(str(resource_path("ui/assets/icons/export.svg"))))
        export_button.setFixedWidth(150); export_button.clicked.connect(self.export_requested.emit)
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget); buttons_layout.setContentsMargins(0,0,0,0); buttons_layout.setSpacing(10)
        buttons_layout.addWidget(import_button); buttons_layout.addWidget(export_button)
        data_row = self._create_setting_row(t.get('label_data_management'), t.get('settings_data_desc'), buttons_widget)
        data_card_layout.addWidget(data_row)
        settings_layout.addWidget(data_section)
        
        settings_layout.addStretch()

    def _init_instructions_tab(self, parent_tab: QWidget) -> None:
        layout = QVBoxLayout(parent_tab); layout.setContentsMargins(10, 10, 10, 10)
        instructions_text = QTextEdit(); instructions_text.setReadOnly(True)
        instructions_text.setObjectName("instructionsText"); instructions_text.setHtml(t.get('text_import_instructions'))
        layout.addWidget(instructions_text)

    def get_selected_language(self) -> str:
        return str(self.lang_combo.currentData())

    def get_selected_theme(self) -> str:
        return str(self.theme_combo.currentData())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()