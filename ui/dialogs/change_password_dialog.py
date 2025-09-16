# ui/dialogs/change_password_dialog.py

import logging
from typing import Optional, Tuple

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QWidget,
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent

# --- MODIFICATION START: Import zxcvbn for strength checking ---
from zxcvbn import zxcvbn
# --- MODIFICATION END ---

from language import t

logger = logging.getLogger(__name__)


class ChangePasswordDialog(QDialog):
    """
    一个用于更改主密码的专用对话框。
    (已升级为使用 zxcvbn 进行高级密码强度验证)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumSize(450, 350)
        self.drag_pos: QPoint = QPoint()

        self.init_ui()
        logger.debug("ChangePasswordDialog opened.")

    def init_ui(self) -> None:
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title_label = QLabel(t.get("change_pass_title"))
        title_label.setObjectName("dialogTitle")

        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        self.old_pass_input = QLineEdit()
        self.old_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_pass_input.setPlaceholderText(t.get("placeholder_old_pass"))
        self.new_pass_input = QLineEdit()
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setPlaceholderText(t.get("placeholder_new_pass"))
        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pass_input.setPlaceholderText(t.get("placeholder_confirm_pass"))

        form_layout.addWidget(QLabel(t.get("label_old_pass")), 0, 0)
        form_layout.addWidget(self.old_pass_input, 0, 1)
        form_layout.addWidget(QLabel(t.get("label_new_pass")), 1, 0)
        form_layout.addWidget(self.new_pass_input, 1, 1)
        form_layout.addWidget(QLabel(t.get("label_confirm_pass")), 2, 0)
        form_layout.addWidget(self.confirm_pass_input, 2, 1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton(t.get("button_cancel"))
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        save_button = QPushButton(t.get("button_save"))
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

    # --- MODIFICATION START: Replaced simple validation with zxcvbn ---
    def _check_password_strength(self, password: str) -> Tuple[bool, str]:
        """使用 zxcvbn 检查密码强度并提供反馈。"""
        if not password:
            return False, t.get("msg_pass_change_fail_empty")

        result = zxcvbn(password)

        # 我们认为分数低于2（即0或1）的密码为弱密码。
        # zxcvbn的分数范围是0-4。
        if result["score"] < 2:
            # 尝试从 zxcvbn 的反馈中获取具体的警告信息
            warning = result.get("feedback", {}).get("warning", "")
            if "short" in warning:
                return False, t.get("zxcvbn_feedback_short")
            if "common" in warning or "names" in warning or "dictionary" in warning:
                return False, t.get("zxcvbn_feedback_common")

            # 如果没有具体的警告，返回一个通用的“弱密码”提示
            return False, t.get("zxcvbn_feedback_weak")

        return True, ""

    # --- MODIFICATION END ---

    def get_passwords(self) -> Tuple[Optional[Tuple[str, str]], Optional[str]]:
        """
        获取并验证用户输入的密码。
        如果验证失败，返回 (None, "失败原因")。
        失败原因可以是 "empty", "mismatch", 或 "weak:具体反馈"。
        """
        old_pass = self.old_pass_input.text()
        new_pass = self.new_pass_input.text()
        confirm_pass = self.confirm_pass_input.text()

        if not all([old_pass, new_pass, confirm_pass]):
            return None, "empty"
        if new_pass != confirm_pass:
            return None, "mismatch"

        # --- MODIFICATION START: Use new strength checker and return its feedback ---
        is_strong, feedback = self._check_password_strength(new_pass)
        if not is_strong:
            # 返回一个特殊格式的字符串，其中包含具体的反馈信息，
            # 以便调用者（控制器）可以向用户显示更详细的提示。
            return None, f"weak:{feedback}"
        # --- MODIFICATION END ---

        return (old_pass, new_pass), None

    def mousePressEvent(self, a0: Optional[QMouseEvent]) -> None:
        if not a0:
            return
        if a0.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = a0.globalPosition().toPoint()
            a0.accept()

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        if not a0:
            return
        if a0.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + a0.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = a0.globalPosition().toPoint()
            a0.accept()