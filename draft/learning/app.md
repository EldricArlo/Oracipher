### 1. 文件概述

`app.py` 定义了 `SafeKeyApp` 类，它继承自 `QMainWindow`，是应用程序的顶级窗口。但它不仅仅是一个简单的窗口，它扮演着多个关键角色：

*   **UI 容器 (UI Container)**: 它本身不包含太多复杂的界面元素，而是作为一个“舞台”，内部持有一个 `QStackedWidget`（堆叠窗口），用于在不同的主要界面（如“解锁屏幕”和“主功能界面”）之间进行切换。
*   **状态管理器 (State Manager)**: 它管理着应用程序的核心状态，最主要的就是“锁定”和“解锁”状态。它决定了用户当前应该看到哪个界面。
*   **事件中心 (Event Hub)**: 它通过事件过滤器（Event Filter）监听整个应用的活动，以实现像“闲置自动锁定”这样的全局功能。同时，它也处理自身的窗口事件，如拖动、关闭等。
*   **生命周期协调者 (Lifecycle Coordinator)**: 它负责应用程序的启动、初始化核心逻辑（加密、数据管理）、以及最重要的——**优雅地关闭**应用程序，确保所有资源（如数据库连接）都被正确释放。
*   **核心逻辑的拥有者 (Owner of Core Logic)**: 它实例化并持有着 `CryptoHandler` 和 `DataManager` 的实例，是UI层和核心业务逻辑层连接的桥梁。

---

### 2. 代码逐行解析与知识拓展

#### **导入模块 (Imports)**

```python
# app.py

import logging
from typing import Optional

from PyQt6.QtWidgets import ( ... )
from PyQt6.QtCore import Qt, QPoint, QTimer, QEvent, QObject
from PyQt6.QtGui import QMouseEvent, QCloseEvent

from config import APP_DATA_DIR, load_settings
from core.crypto import CryptoHandler
from core.database import DataManager
from language import t
from ui.theme_manager import apply_theme, get_current_theme
from ui.unlock_screen import UnlockScreen
from ui.main_window import MainWindow
from ui.task_manager import task_manager
```
*   **PyQt6 导入**:
    *   `QMainWindow`: PyQt中用于创建主窗口的基类，可以包含菜单栏、工具栏、状态栏等。
    *   `QStackedWidget`: **核心控件**，一个可以容纳多个子控件（页面）的容器，但一次只显示一个。这是实现界面切换的关键。
    *   `QTimer`: 一个定时器类，用于在指定时间间隔后触发一个动作，这里用于实现自动锁定。
    *   `QEvent`, `QObject`: 事件系统的基础。`eventFilter` 需要用到它们。
    *   `QMouseEvent`, `QCloseEvent`: 专门用于描述鼠标事件和窗口关闭事件的对象。
*   **项目内导入**:
    *   `config`, `core`, `language`, `ui`: 这清晰地展示了项目的分层结构。`app.py` 位于UI层，它依赖于 `core` 层的业务逻辑，并使用 `config` 和 `language` 获取配置与文本，同时组织 `ui` 子模块中的其他界面组件。
    *   `task_manager`: 导入一个任务管理器，暗示了程序中有一些操作需要异步或在后台执行。

---

#### **`SafeKeyApp` 类 - `__init__` 构造函数**

这是类的入口，负责所有初始化的工作。

```python
    def __init__(self):
        super().__init__()
        logger.info("Initializing SafeKeyApp main window container...")

        self.setWindowTitle(t.get("app_title"))
        self.resize(1000, 700)
```
*   **逐行解释**: 调用父类的构造函数，设置窗口标题（从语言模块获取）和初始大小。

```python
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
```
*   **逐行解释**: 这两行是创建**自定义外观窗口**的关键。
    *   `FramelessWindowHint`: 移除了操作系统的标准窗口边框和标题栏。这允许开发者用自定义的UI元素来替代它们（例如自定义的关闭、最小化按钮）。
    *   `WA_TranslucentBackground`: 使窗口背景透明。这通常与自定义的背景面板（`QFrame`）结合使用，通过样式表（CSS）可以实现圆角、阴影等现代UI效果。
*   **知识拓展**: 拥有了无边框窗口后，一个直接的“副作用”是用户无法再通过标题栏拖动窗口了。因此，开发者必须自己实现窗口拖动的功能，后面的 `mousePressEvent` 和 `mouseMoveEvent` 就是为了解决这个问题。

```python
        self.drag_pos: QPoint = QPoint()
        self._is_shutting_down = False
```
*   **逐行解释**: 初始化两个状态变量。
    *   `drag_pos`: 用于存储鼠标按下时相对于屏幕的位置，是实现自定义拖动的关键。
    *   `_is_shutting_down`: 一个布尔标志位，用于防止在程序关闭过程中重复触发关闭逻辑，确保关闭过程只执行一次。

```python
        self.auto_lock_timer = QTimer(self)
        self.auto_lock_timer.setSingleShot(True)
        self.auto_lock_timer.timeout.connect(self.lock_vault)
```
*   **逐行解释**: 设置自动锁定计时器。
    *   `QTimer(self)`: 创建一个定时器，`self` 作为其父对象，这样当主窗口销毁时，定时器也会被自动清理。
    *   `setSingleShot(True)`: 设置为“单次触发”模式。计时器在倒计时结束后会触发一次 `timeout` 信号，然后停止。如果想让它重新计时，必须再次调用 `start()`。这完美符合“用户活动后重置计时”的需求。
    *   `timeout.connect(self.lock_vault)`: **信号与槽机制**。将定时器的 `timeout` 信号连接到 `self.lock_vault` 这个槽函数（方法）。当时间到时，`lock_vault` 方法会被自动调用。

```python
        self.crypto_handler: CryptoHandler = CryptoHandler(APP_DATA_DIR)
        self.data_manager: DataManager = DataManager(APP_DATA_DIR, self.crypto_handler)
```
*   **逐行解释**: 实例化核心业务逻辑类。`SafeKeyApp` 作为顶层窗口，负责创建和管理这两个贯穿应用生命周期的核心对象。

```python
        app_instance = QApplication.instance()
        if isinstance(app_instance, QApplication):
            apply_theme(app_instance, get_current_theme())
            app_instance.installEventFilter(self)
```
*   **逐行解释**:
    *   获取全局唯一的 `QApplication` 实例。
    *   `apply_theme(...)`: 应用全局主题（样式表）。
    *   `app_instance.installEventFilter(self)`: **非常关键的一行**。将 `SafeKeyApp` 实例 (`self`) 安装为应用程序级别的**事件过滤器**。这意味着，应用中发生的**任何**事件（键盘、鼠标等），在被分发到其目标控件之前，都会先经过 `SafeKeyApp` 的 `eventFilter` 方法。这是实现全局用户活动监测（用于重置自动锁定计时器）的最高效方式。

---

#### **UI初始化和切换逻辑**

```python
    def init_ui(self) -> None:
        # ...
        self.stacked_widget = QStackedWidget()
        # ...
        self.unlock_screen = UnlockScreen(...)
        self.unlock_screen.unlocked.connect(self.show_main_app)
        self.stacked_widget.addWidget(self.unlock_screen)
        self.main_widget: Optional[MainWindow] = None
```
*   **逐行解释**:
    *   创建 `QStackedWidget` 作为界面切换器。
    *   创建 `UnlockScreen` 实例，它是启动时显示的第一个页面。
    *   `unlocked.connect(self.show_main_app)`: 再次体现信号槽。当 `UnlockScreen` 成功验证密码后，会发出 `unlocked` 信号，该信号会触发 `show_main_app` 方法，从而切换到主界面。
    *   `self.main_widget = None`: **懒加载（Lazy Loading）**。主界面 `MainWindow` 是一个复杂的控件，可能需要较多资源来初始化。这里将其设置为 `None`，只在用户成功解锁后才真正创建它。这可以加快应用程序的初始启动速度。

```python
    def show_main_app(self) -> None:
        if not self.main_widget:
            self.main_widget = MainWindow(...)
            self.stacked_widget.addWidget(self.main_widget)
        self.stacked_widget.setCurrentWidget(self.main_widget)
        self._setup_auto_lock()
```
*   **逐行解释**:
    *   检查 `self.main_widget` 是否已创建。如果是首次解锁，就创建 `MainWindow` 实例并将其添加到 `stacked_widget` 中。
    *   `setCurrentWidget(self.main_widget)`: **执行切换**。告诉 `stacked_widget` 将 `main_widget` 显示在最顶层。
    *   `_setup_auto_lock()`: 成功进入主界面后，才开始启动自动锁定计时器。

```python
    def lock_vault(self) -> None:
        # ...
        self.crypto_handler.key = None
        if self.main_widget:
            self.main_widget.deleteLater()
            self.main_widget = None
        self.stacked_widget.setCurrentWidget(self.unlock_screen)
```*   **逐行解释**: 这是 `show_main_app` 的逆向操作。
    *   `self.crypto_handler.key = None`: **核心安全步骤**。清除内存中存储的解密密钥。此时，即使有人能访问内存，也无法解密数据。
    *   `self.main_widget.deleteLater()`: **安全的Qt对象销毁**。`deleteLater()` 会将对象的删除操作排入事件队列，在当前事件处理完成后再执行。直接使用 `del self.main_widget` 在复杂的GUI程序中有时会导致程序崩溃，因为可能还有事件正要被发送给这个对象。`deleteLater()` 是官方推荐的安全做法。
    *   将 `self.main_widget` 设回 `None`，以便下次解锁时重新创建。
    *   切换回解锁屏幕。

---

#### **自动锁定和事件处理**

```python
    def _setup_auto_lock(self) -> None:
        # ... 从设置加载超时时间 ...
        if self._auto_lock_enabled and self._auto_lock_timeout_ms > 0:
            self.auto_lock_timer.start(self._auto_lock_timeout_ms)
```
*   **逐行解释**: 从配置文件加载设置，如果启用了自动锁定，就用`start()`启动（或重置）计时器。

```python
    def eventFilter(self, a0: "QObject | None", a1: "QEvent | None") -> bool:
        # ...
        if event.type() in [QEvent.Type.KeyPress, QEvent.Type.MouseButtonPress, QEvent.Type.MouseMove]:
            self.auto_lock_timer.start(self._auto_lock_timeout_ms)
        return super().eventFilter(watched, event)
```
*   **逐行解释**: 这就是之前安装的事件过滤器的具体实现。
    *   只要监测到键盘按键、鼠标点击或鼠标移动这几类代表“用户正在活动”的事件，就立即调用 `self.auto_lock_timer.start()`。这会**重置**计时器的倒计时，重新开始计算闲置时间。
    *   `return super().eventFilter(...)`: **至关重要**。在完成自己的逻辑后，必须调用父类的 `eventFilter` 方法，以确保事件能够被正常地继续传递和处理。否则，整个应用程序的鼠标键盘输入都会失效。

---

#### **窗口拖动和关闭**

```python
    def mousePressEvent(self, a0: "QMouseEvent | None") -> None:
        # ...
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
```
*   **逐行解释**: 当在窗口上按下鼠标左键时，记录下当前鼠标的**全局屏幕坐标**。

```python
    def mouseMoveEvent(self, a0: "QMouseEvent | None") -> None:
        # ...
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
```
*   **逐行解释**:
    *   当按住左键并移动鼠标时，这个方法会被持续调用。
    *   `event.globalPosition().toPoint() - self.drag_pos`: 计算出鼠标从上一个位置移动到当前位置的**位移向量**。
    *   `self.move(self.pos() + ...)`: 将窗口的当前位置 (`self.pos()`) 加上这个位移向量，从而实现窗口的同步移动。
    *   `self.drag_pos = ...`: 移动后，立刻更新 `drag_pos` 为当前位置，为下一次移动计算做准备。

```python
    def closeEvent(self, a0: "QCloseEvent | None") -> None:
        # ...
        self.hide()
        event.ignore()

        task_manager.run_in_background(
            task=self.data_manager.close,
            on_success=on_shutdown_finished,
        )
```
*   **逐行解释**: 实现了**优雅关闭 (Graceful Shutdown)**。
    *   `event.ignore()`: 拦截用户的关闭请求（例如点击窗口的“X”按钮）。它告诉系统：“别关，我知道了，我自己来处理关闭流程。”
    *   `self.hide()`: 立即隐藏窗口，给用户一种程序已经关闭的即时反馈。
    *   `task_manager.run_in_background(...)`: **异步处理耗时操作**。关闭数据库连接可能会涉及文件I/O，可能会有延迟。如果直接在主线程中执行 `self.data_manager.close()`，UI会卡住直到操作完成。这里将其交给后台任务管理器执行。
    *   `on_success=on_shutdown_finished`: 注册一个回调函数。当后台的数据库关闭任务成功完成后，`on_shutdown_finished` 会被调用。
    *   `on_shutdown_finished` 内部调用 `app.quit()`: 这是真正退出应用程序的命令。它会终止Qt的事件循环。

---

### 3. 总结

`app.py` 是一个设计精良的应用程序主框架。它出色地展示了现代桌面应用开发的多个重要概念：

*   **模型-视图-控制器 (MVC) 的变体**: `SafeKeyApp` 充当了**控制器 (Controller)** 的角色，它协调 `core` 里的**模型 (Model)**（数据和业务逻辑）与 `ui` 包里的**视图 (View)**（解锁屏幕、主窗口）之间的交互。
*   **关注点分离**: 将窗口拖动、自动锁定、界面切换、生命周期管理等不同的职责清晰地实现在各自的方法中。
*   **事件驱动编程**: 大量使用信号与槽机制和事件过滤器来响应用户输入和内部状态变化，代码解耦度高。
*   **性能与安全意识**: 通过懒加载提升启动速度，通过异步任务避免UI卡顿，在锁定和关闭时严格处理密钥和资源，体现了良好的编程实践。