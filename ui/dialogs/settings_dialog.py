# ui/dialogs/settings_dialog.py

import logging
from typing import Optional

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QFrame, QComboBox, QWidget)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QMouseEvent

from language import t
from config import load_settings

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    change_password_requested = pyqtSignal()
    import_requested = pyqtSignal()
    export_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumSize(450, 400)
        self.drag_pos: QPoint = QPoint()
        self.init_ui()
        logger.debug("SettingsDialog 打开。")

    def init_ui(self) -> None:
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        title_label = QLabel(t.get('settings_title'))
        title_label.setObjectName("dialogTitle")
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.setColumnStretch(1, 1)

        self.lang_combo = QComboBox()
        available_languages = t.get_available_languages()
        current_settings = load_settings()
        current_lang_code = current_settings.get('language', 'en')
        for code, name in available_languages.items():
            self.lang_combo.addItem(name, userData=code)
            if code == current_lang_code:
                self.lang_combo.setCurrentText(name)
        form_layout.addWidget(QLabel(t.get('settings_lang_label')), 0, 0)
        form_layout.addWidget(self.lang_combo, 0, 1)

        change_pass_button = QPushButton(t.get('change_pass_title'))
        change_pass_button.setObjectName("inlineButton")
        change_pass_button.clicked.connect(self.change_password_requested.emit)
        form_layout.addWidget(QLabel(t.get('label_pass')), 1, 0)
        form_layout.addWidget(change_pass_button, 1, 1)
        
        data_management_label = QLabel(t.get('label_data_management'))
        data_management_label.setObjectName("fieldTitleLabel")
        data_management_label.setStyleSheet("margin-top: 15px;")
        import_button = QPushButton(t.get('button_import'))
        import_button.setObjectName("inlineButton")
        import_button.clicked.connect(self.import_requested.emit)
        export_button = QPushButton(t.get('button_export'))
        export_button.setObjectName("inlineButton")
        export_button.clicked.connect(self.export_requested.emit)
        form_layout.addWidget(data_management_label, 2, 0, 1, 2)
        form_layout.addWidget(import_button, 3, 1)
        form_layout.addWidget(export_button, 4, 1)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton(t.get('button_cancel'))
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        save_button = QPushButton(t.get('button_done'))
        save_button.setObjectName("saveButton")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)

    def get_selected_language(self) -> str:
        lang_code = self.lang_combo.currentData()
        return str(lang_code) if lang_code is not None else 'en'

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()