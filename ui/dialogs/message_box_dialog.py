# ui/dialogs/message_box_dialog.py

import logging
from enum import Enum
from typing import Optional

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QWidget)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent

from language import t

logger = logging.getLogger(__name__)

class CustomMessageBox(QDialog):
    class DialogType(Enum):
        Information = 1
        Question = 2

    def __init__(self, parent: Optional[QWidget], dialog_type: DialogType, title: str, message: str):
        super().__init__(parent)
        self.dialog_type = dialog_type
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumWidth(380)
        self.drag_pos: QPoint = QPoint()
        self.init_ui(title, message)
        log_type = "Question" if dialog_type == self.DialogType.Question else "Information"
        logger.debug(f"显示 CustomMessageBox ({log_type}): Title='{title}', Message='{message}'")
        
    def init_ui(self, title: str, message: str) -> None:
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)
        title_label = QLabel(title)
        title_label.setObjectName("dialogTitle")
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        if self.dialog_type == self.DialogType.Question:
            cancel_button = QPushButton(t.get('button_cancel'))
            cancel_button.setObjectName("cancelButton")
            cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(cancel_button)
        ok_button = QPushButton(t.get('button_ok'))
        ok_button.setObjectName("saveButton")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        main_layout.addWidget(title_label)
        main_layout.addWidget(message_label)
        main_layout.addSpacing(10)
        main_layout.addLayout(button_layout)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)
        self.adjustSize()

    @staticmethod
    def information(parent: Optional[QWidget], title: str, message: str) -> QDialog.DialogCode:
        dialog = CustomMessageBox(parent, CustomMessageBox.DialogType.Information, title, message)
        return dialog.exec()

    @staticmethod
    def question(parent: Optional[QWidget], title: str, message: str) -> QDialog.DialogCode:
        dialog = CustomMessageBox(parent, CustomMessageBox.DialogType.Question, title, message)
        return dialog.exec()
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()