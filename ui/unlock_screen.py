# ui/unlock_screen.py

import logging
from typing import Optional, Tuple

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from zxcvbn import zxcvbn

from core.crypto import CryptoHandler
from language import t
from ui.dialogs.message_box_dialog import CustomMessageBox
from ui.task_manager import task_manager

logger = logging.getLogger(__name__)


class UnlockScreen(QWidget):
    unlocked = pyqtSignal()
    exit_requested = pyqtSignal()

    def __init__(self, crypto_handler: CryptoHandler, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.crypto = crypto_handler
        self.setObjectName("UnlockScreen")
        self.is_setup_mode = not self.crypto.is_key_setup()
        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QFrame(self)
        container.setObjectName("unlockContainer")
        layout = QVBoxLayout(container)
        layout.setSpacing(20)

        self.logo_label = QLabel()
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.welcome_label = QLabel()
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._attempt_unlock)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.returnPressed.connect(self._attempt_unlock)

        self.action_button = QPushButton()
        self.action_button.setObjectName("mainActionButton")
        self.action_button.clicked.connect(self._attempt_unlock)

        self.exit_button = QPushButton()
        self.exit_button.setObjectName("unlockExitButton")
        self.exit_button.clicked.connect(self.exit_requested.emit)

        layout.addWidget(self.logo_label)
        layout.addWidget(self.welcome_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(self.action_button)
        layout.addWidget(self.exit_button)

        main_layout.addWidget(container)
        self.update_ui_for_mode()

    def retranslate_ui(self) -> None:
        if self.is_setup_mode:
            self.welcome_label.setText(t.get("setup_instruction"))
            self.password_input.setPlaceholderText(t.get("setup_placeholder"))
            self.confirm_password_input.setPlaceholderText(
                t.get("setup_confirm_placeholder")
            )
            self.action_button.setText(t.get("setup_button"))
        else:
            self.welcome_label.setText(t.get("unlock_welcome"))
            self.password_input.setPlaceholderText(t.get("unlock_placeholder"))
            self.action_button.setText(t.get("unlock_button"))

        self.logo_label.setText(t.get("app_title"))
        self.exit_button.setText(t.get("button_exit"))

    def update_ui_for_mode(self) -> None:
        self.retranslate_ui()
        self.confirm_password_input.setVisible(self.is_setup_mode)

    # --- MODIFICATION START: Replaced simple validation with zxcvbn ---
    def _check_password_strength(self, password: str) -> Tuple[bool, str]:
        """Checks password strength using zxcvbn and provides feedback."""
        if not password:
            # This case should be caught by the mismatch check, but as a fallback.
            return False, t.get("error_msg_mismatch")

        result = zxcvbn(password)

        # We consider a score of 2 or less to be weak.
        # (0=too guessable, 1=very guessable, 2=somewhat guessable, 3=safely unguessable, 4=very unguessable)
        if result['score'] < 2:
            # Extract the main warning from zxcvbn's feedback
            warning = result.get('feedback', {}).get('warning', '')
            if "short" in warning:
                return False, t.get("zxcvbn_feedback_short")
            if "common" in warning or "names" in warning or "dictionary" in warning:
                return False, t.get("zxcvbn_feedback_common")
            # Provide a generic "weak" message if no specific warning matches
            return False, t.get("zxcvbn_feedback_weak")

        return True, ""
    # --- MODIFICATION END ---

    def _set_ui_locked(self, locked: bool) -> None:
        self.password_input.setEnabled(not locked)
        self.confirm_password_input.setEnabled(not locked)
        self.action_button.setEnabled(not locked)
        if locked:
            self.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        else:
            self.unsetCursor()

    def _attempt_unlock(self) -> None:
        password = self.password_input.text()
        self._set_ui_locked(True)

        if self.is_setup_mode:
            confirm_password = self.confirm_password_input.text()
            if password != confirm_password:
                CustomMessageBox.information(
                    self, t.get("error_title_mismatch"), t.get("error_msg_mismatch")
                )
                self._set_ui_locked(False)
                return

            # --- MODIFICATION START: Use new strength checker and provide detailed feedback ---
            is_strong, feedback_message = self._check_password_strength(password)
            if not is_strong:
                CustomMessageBox.information(
                    self,
                    t.get("error_title_weak_password"),
                    feedback_message,
                )
                self._set_ui_locked(False)
                return
            # --- MODIFICATION END ---

            task_manager.run_in_background(
                self.crypto.set_master_password,
                on_success=self._on_setup_success,
                password=password,
            )
        else:
            task_manager.run_in_background(
                self.crypto.unlock_with_master_password,
                on_success=self._on_unlock_result,
                on_error=self._on_unlock_error,
                password=password,
            )

    def _on_unlock_result(self, success: bool) -> None:
        self._set_ui_locked(False)
        if success:
            self.unlocked.emit()
        else:
            CustomMessageBox.information(
                self, t.get("error_title_generic"), t.get("error_msg_wrong_password")
            )
            self.password_input.clear()

    def _on_unlock_error(self, err: Exception, tb: str) -> None:
        self._set_ui_locked(False)
        CustomMessageBox.information(self, t.get("error_title_generic"), str(err))

    def _on_setup_success(self, _=None) -> None:
        self._set_ui_locked(False)
        CustomMessageBox.information(
            self, t.get("setup_success_title"), t.get("setup_success_msg")
        )
        self.is_setup_mode = False
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.update_ui_for_mode()