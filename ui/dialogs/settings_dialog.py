# ui/dialogs/settings_dialog.py

import logging
from typing import Optional, Tuple

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QWidget,
    QTextEdit,
    QTabWidget,
    QComboBox,
    QCheckBox,
    QSpinBox,
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QEvent, QObject
from PyQt6.QtGui import QMouseEvent, QIcon, QShowEvent

from language import t
from config import load_settings
from utils.paths import resource_path
from ..theme_manager import get_current_theme

logger = logging.getLogger(__name__)


# --- MODIFICATION START: Custom ComboBox to manage state ---
class PopupBlockingComboBox(QComboBox):
    """
    一个自定义的QComboBox，它能发出信号来通知父窗口其弹出列表的显示和隐藏状态。
    这对于帮助无边框父窗口锁定其拖动机制至关重要。
    """

    popupOpened = pyqtSignal()
    popupClosed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        # 弹出列表（view）本身是另一个窗口的一部分。我们需要在那个窗口上安装事件过滤器
        # 来可靠地捕获其隐藏事件。
        view = self.view()
        if view:
            view_parent = view.parentWidget()
            if view_parent:
                view_parent.installEventFilter(self)

    def showPopup(self) -> None:
        """重写 showPopup，在显示时发出信号。"""
        self.popupOpened.emit()
        super().showPopup()

    def hidePopup(self) -> None:
        """
        重写 hidePopup。注意：此方法不总是在用户点击别处时被调用，
        因此 eventFilter 是更可靠的方式。
        """
        super().hidePopup()
        self.popupClosed.emit()

    def eventFilter(self, a0: Optional[QObject], a1: Optional[QEvent]) -> bool:
        """
        在弹出列表的父窗口上监听事件。
        """
        view = self.view()
        if view and a1 and a0 == view.parentWidget() and a1.type() == QEvent.Type.Hide:
            # 当弹出列表的窗口被隐藏时，发出 closed 信号。
            self.popupClosed.emit()
        return super().eventFilter(a0, a1)


# --- MODIFICATION END ---


class SettingsDialog(QDialog):
    change_password_requested = pyqtSignal()
    import_requested = pyqtSignal()
    export_requested = pyqtSignal()
    theme_changed = pyqtSignal(str)
    settings_cancelled = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumSize(600, 550)
        self.drag_pos: QPoint = QPoint()
        self._is_first_show = True

        # --- MODIFICATION START: Add flag to lock dragging ---
        self._is_dragging_locked = False
        # --- MODIFICATION END ---

        self.init_ui()
        logger.debug("SettingsDialog opened.")

    def showEvent(self, a0: Optional[QShowEvent]) -> None:
        super().showEvent(a0)
        if self._is_first_show:
            settings = load_settings()
            is_enabled = settings.get("auto_lock_enabled", True)
            timeout_minutes = settings.get("auto_lock_timeout_minutes", 15)
            self.auto_lock_checkbox.setChecked(is_enabled)
            self.auto_lock_spinbox.setValue(timeout_minutes)
            self._is_first_show = False
            self._update_auto_lock_controls(self.auto_lock_checkbox.checkState())

    # --- MODIFICATION START: Add slots to handle popup state ---
    def _lock_dragging(self):
        self._is_dragging_locked = True

    def _unlock_dragging(self):
        self._is_dragging_locked = False

    # --- MODIFICATION END ---

    def init_ui(self) -> None:
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        title_label = QLabel(t.get("settings_title"))
        title_label.setObjectName("dialogTitle")

        self.tabs = QTabWidget()
        settings_tab, instructions_tab = QWidget(), QWidget()
        self.tabs.addTab(settings_tab, t.get("tab_settings"))
        self.tabs.addTab(instructions_tab, t.get("tab_instructions"))

        self._init_settings_tab(settings_tab)
        self._init_instructions_tab(instructions_tab)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        done_button = QPushButton(t.get("button_done"))
        done_button.setObjectName("saveButton")
        done_button.clicked.connect(self.accept)
        button_layout.addWidget(done_button)

        main_layout.addWidget(title_label)
        main_layout.addWidget(self.tabs)
        main_layout.addLayout(button_layout)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)

    def _create_section_widget(self, title_text: str) -> tuple[QWidget, QVBoxLayout]:
        section_container = QWidget()
        section_layout = QVBoxLayout(section_container)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(10)
        title_label = QLabel(title_text)
        title_label.setObjectName("sectionTitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_frame = QFrame()
        card_frame.setObjectName("settingsGroupFrame")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(20)
        section_layout.addWidget(title_label)
        section_layout.addWidget(card_frame)
        return section_container, card_layout

    def _create_setting_row(
        self, title_text: str, desc_text: str, control_widget: QWidget
    ) -> QWidget:
        row_widget = QWidget()
        row_widget.setObjectName("settingRow")
        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        title_label = QLabel(title_text)
        title_label.setObjectName("settingTitleLabel")
        desc_label = QLabel(desc_text)
        desc_label.setObjectName("settingDescLabel")
        desc_label.setWordWrap(True)
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        layout.addWidget(text_widget, 1)
        layout.addWidget(control_widget, 0, Qt.AlignmentFlag.AlignVCenter)
        return row_widget

    def _init_settings_tab(self, parent_tab: QWidget) -> None:
        settings = load_settings()
        settings_layout = QVBoxLayout(parent_tab)
        settings_layout.setSpacing(25)
        settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- 常规设置 ---
        general_section, general_card_layout = self._create_section_widget(
            t.get("settings_section_general")
        )

        # --- MODIFICATION START: Use the new custom ComboBox ---
        self.lang_combo = PopupBlockingComboBox()
        self.lang_combo.setFixedWidth(200)
        # --- MODIFICATION END ---

        available_languages = t.get_available_languages()
        for code, name in available_languages.items():
            self.lang_combo.addItem(name, userData=code)
        index = self.lang_combo.findData(settings.get("language", "zh_CN"))
        if index != -1:
            self.lang_combo.setCurrentIndex(index)
        lang_row = self._create_setting_row(
            t.get("settings_lang_title"), t.get("settings_lang_desc"), self.lang_combo
        )
        general_card_layout.addWidget(lang_row)

        # --- MODIFICATION START: Use the new custom ComboBox ---
        self.theme_combo = PopupBlockingComboBox()
        self.theme_combo.setFixedWidth(200)
        # --- MODIFICATION END ---

        self.theme_combo.addItem(t.get("theme_light"), userData="light")
        self.theme_combo.addItem(t.get("theme_dark"), userData="dark")
        theme_index = self.theme_combo.findData(get_current_theme())
        if theme_index != -1:
            self.theme_combo.setCurrentIndex(theme_index)
        self.theme_combo.currentIndexChanged.connect(
            lambda: self.theme_changed.emit(self.get_selected_theme())
        )
        theme_row = self._create_setting_row(
            t.get("settings_theme_title"),
            t.get("settings_theme_desc"),
            self.theme_combo,
        )
        general_card_layout.addWidget(theme_row)
        settings_layout.addWidget(general_section)

        # --- MODIFICATION START: Connect the new signals ---
        self.lang_combo.popupOpened.connect(self._lock_dragging)
        self.lang_combo.popupClosed.connect(self._unlock_dragging)
        self.theme_combo.popupOpened.connect(self._lock_dragging)
        self.theme_combo.popupClosed.connect(self._unlock_dragging)
        # --- MODIFICATION END ---

        # --- 安全设置 ---
        security_section, security_card_layout = self._create_section_widget(
            t.get("settings_section_security")
        )
        change_pass_button = QPushButton(t.get("settings_change_pass_button"))
        change_pass_button.setObjectName("inlineButton")
        change_pass_button.setFixedWidth(200)
        change_pass_button.clicked.connect(self.change_password_requested.emit)
        pass_row = self._create_setting_row(
            t.get("change_pass_title"),
            t.get("settings_change_pass_desc"),
            change_pass_button,
        )
        security_card_layout.addWidget(pass_row)

        # --- 自动锁定设置UI ---
        self.auto_lock_checkbox = QCheckBox()
        self.auto_lock_checkbox.stateChanged.connect(
            lambda state: self._update_auto_lock_controls(Qt.CheckState(state))
        )
        self.auto_lock_spinbox = QSpinBox()
        self.auto_lock_spinbox.setRange(1, 120)
        self.auto_lock_spinbox.setSuffix(f" {t.get('minutes_suffix')}")
        self.auto_lock_spinbox.setFixedWidth(120)
        line_edit = self.auto_lock_spinbox.lineEdit()
        if line_edit:
            line_edit.setReadOnly(True)
        auto_lock_controls_widget = QWidget()
        auto_lock_controls_layout = QHBoxLayout(auto_lock_controls_widget)
        auto_lock_controls_layout.setContentsMargins(0, 0, 0, 0)
        auto_lock_controls_layout.setSpacing(15)
        auto_lock_controls_layout.addWidget(self.auto_lock_spinbox)
        auto_lock_controls_layout.addWidget(self.auto_lock_checkbox)
        auto_lock_controls_layout.addStretch()
        auto_lock_row = self._create_setting_row(
            t.get("settings_auto_lock_title"),
            t.get("settings_auto_lock_desc"),
            auto_lock_controls_widget,
        )
        security_card_layout.addWidget(auto_lock_row)
        settings_layout.addWidget(security_section)

        # --- 数据管理 ---
        data_section, data_card_layout = self._create_section_widget(
            t.get("settings_section_data")
        )
        import_button = QPushButton(f" {t.get('button_import')}")
        import_button.setIcon(QIcon(str(resource_path("ui/assets/icons/import.svg"))))
        import_button.setFixedWidth(150)
        import_button.clicked.connect(self.import_requested.emit)
        export_button = QPushButton(f" {t.get('button_export')}")
        export_button.setIcon(QIcon(str(resource_path("ui/assets/icons/export.svg"))))
        export_button.setFixedWidth(150)
        export_button.clicked.connect(self.export_requested.emit)
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        buttons_layout.addWidget(import_button)
        buttons_layout.addWidget(export_button)
        data_row = self._create_setting_row(
            t.get("label_data_management"), t.get("settings_data_desc"), buttons_widget
        )
        data_card_layout.addWidget(data_row)
        settings_layout.addWidget(data_section)

        settings_layout.addStretch()

    def _update_auto_lock_controls(self, state: Qt.CheckState) -> None:
        is_checked = state == Qt.CheckState.Checked
        self.auto_lock_spinbox.setEnabled(is_checked)

        spinbox_style = self.auto_lock_spinbox.style()
        if spinbox_style:
            spinbox_style.unpolish(self.auto_lock_spinbox)
            spinbox_style.polish(self.auto_lock_spinbox)
        self.auto_lock_spinbox.update()

        checkbox_style = self.auto_lock_checkbox.style()
        if checkbox_style:
            checkbox_style.unpolish(self.auto_lock_checkbox)
            checkbox_style.polish(self.auto_lock_checkbox)

    def _init_instructions_tab(self, parent_tab: QWidget) -> None:
        layout = QVBoxLayout(parent_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        instructions_text = QTextEdit()
        instructions_text.setReadOnly(True)
        instructions_text.setObjectName("instructionsText")
        instructions_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        instructions_text.setHtml(t.get("text_import_instructions"))
        layout.addWidget(instructions_text)

    def get_selected_language(self) -> str:
        return str(self.lang_combo.currentData())

    def get_selected_theme(self) -> str:
        return str(self.theme_combo.currentData())

    def get_auto_lock_settings(self) -> Tuple[bool, int]:
        is_enabled = self.auto_lock_checkbox.isChecked()
        minutes = self.auto_lock_spinbox.value()
        return is_enabled, minutes

    def mousePressEvent(self, a0: Optional[QMouseEvent]) -> None:
        if self._is_dragging_locked or not a0:
            return
        if a0.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = a0.globalPosition().toPoint()
            a0.accept()

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        if self._is_dragging_locked or not a0:
            return
        if a0.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + a0.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = a0.globalPosition().toPoint()
            a0.accept()

    def reject(self) -> None:
        self.settings_cancelled.emit()
        super().reject()