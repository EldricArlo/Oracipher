# 为 SafeKey 贡献

您好！我们非常欢迎并感谢您有兴趣为 SafeKey 做出贡献。SafeKey 是一个注重安全和隐私、完全运行于本地的密码管理器。您的每一份贡献，无论是报告一个bug、提出功能建议，还是提交代码，都对这个项目至关重要。

在开始之前，请花几分钟时间阅读本指南。

## 行为准则

为了营造一个开放、友好的社区环境，我们期望所有参与者都能遵守我们的 [行为准则](CODE_OF_CONDUCT.md)。请确保您在参与社区讨论和代码贡献时，能够尊重每一位成员。

## 如何贡献

您可以通过多种方式为 SafeKey 做出贡献：

### 报告 Bug

如果您在使用中发现了 Bug，请通过 [GitHub Issues](https://github.com/EldricArlo/Simple-Safekey/blob/10.4.1-version/issues) 提交一个详细的报告。一个好的 Bug 报告应包含以下信息：

*   **清晰的标题**：简明扼要地描述问题。
*   **操作系统**：例如 Windows 11, macOS Sonoma, Ubuntu 22.04。
*   **复现步骤**：详细描述如何一步步地触发这个 Bug。
*   **期望行为** vs **实际行为**：描述您认为应该发生什么，以及实际发生了什么。
*   **截图或录屏**：如果可能，请附上截图或动图，这能极大地帮助我们理解问题。
*   **日志文件**：附上位于项目 `logs/safekey.log` 目录下的日志文件，这对于调试至关重要。

### 提出功能建议

如果您有关于新功能或改进现有功能的想法，也欢迎通过 [GitHub Issues](https://github.com/EldricArlo/Simple-Safekey/blob/10.4.1-version/issues) 提出。请在建议中详细说明：

*   **解决了什么问题**：描述这个新功能要解决的用户痛点或使用场景。
*   **功能描述**：详细描述这个功能应该如何工作。
*   **相关参考**：如果其他应用有类似的功能，可以附上截图或链接作为参考。

### 提交代码 (Pull Requests)

我们非常欢迎您通过 Pull Request (PR) 直接为项目贡献代码。

1.  **Fork 仓库**：点击仓库右上角的 "Fork" 按钮，将项目 Fork 到您自己的 GitHub 账户下。
2.  **克隆您的 Fork**：`git clone https://github.com/YOUR_USERNAME/SafeKey.git`
3.  **创建新分支**：`git checkout -b feature/your-awesome-feature` 或 `fix/bug-description`。
4.  **进行修改**：在本地进行代码修改和开发。
5.  **提交更改**：遵循我们的 [Git 提交规范](#git-提交规范)。
6.  **推送到您的 Fork**：`git push origin feature/your-awesome-feature`
7.  **创建 Pull Request**：在 GitHub 上，从您的 Fork 创建一个 Pull Request 到主仓库的 `main` 分支。请在 PR 描述中详细说明您的修改内容和目的。

---

## 本地开发环境搭建

要开始在本地开发 SafeKey，请按以下步骤操作：

1.  **安装 Python**
    确保您已安装 Python 3.10 或更高版本。

2.  **克隆仓库**
    ```bash
    git clone https://github.com/YOUR_USERNAME/SafeKey.git
    cd SafeKey
    ```

3.  **创建并激活虚拟环境**
    我们强烈建议使用虚拟环境来隔离项目依赖。
    ```bash
    # Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4.  **安装依赖**
    项目依赖项定义在 `requirements.txt` 文件中。
    ```bash
    pip install -r requirements.txt
    ```
    *如果您是第一个设置此文件的，请根据项目使用的库创建 `requirements.txt`：*
    ```
    PyQt6
    cryptography
    argon2-cffi
    pyzbar
    Pillow
    requests
    python-dotenv
    pyotp
    ```

5.  **运行应用**
    一切就绪后，您可以运行主程序：
    ```bash
    python main.py
    ```

---

## 项目结构概览

了解项目结构有助于您快速定位到需要修改的代码。

```
SafeKey/
├── core/                   # 核心后端逻辑 (与UI无关)
│   ├── crypto.py           # 加密/解密、密钥派生
│   ├── database.py         # 数据库交互 (SQLite)
│   ├── data_handler.py     # 数据导入/导出逻辑
│   └── ...
├── language/               # 多语言翻译文件
│   ├── locales/
│   │   ├── en.py
│   │   └── zh_CN.py
│   └── manager.py          # 语言管理器
├── ui/                     # 所有用户界面 (UI) 相关代码
│   ├── assets/             # 静态资源 (图标、QSS样式表)
│   ├── components/         # 可复用的自定义UI组件
│   ├── controllers/        # 控制器 (连接视图和核心逻辑)
│   ├── dialogs/            # 对话框窗口
│   ├── logic/              # UI相关的辅助逻辑 (如图标获取)
│   ├── views/              # 主要的UI视图面板
│   └── theme_manager.py    # 主题加载与应用
├── utils/                  # 通用工具模块
├── main.py                 # 应用程序主入口
└── app.py                  # 主窗口 (QMainWindow) 容器
```

## 风格指南

### Python 代码

*   请遵循 **PEP 8** 规范。
*   我们推荐使用 `black` 进行代码格式化，使用 `flake8` 进行代码风格检查，以保持代码库的一致性。
*   请为所有新的函数和类添加清晰的 Docstrings。

### Git 提交规范

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。这有助于保持提交历史的清晰，并为自动化生成更新日志打下基础。

提交消息的格式为：`<type>(<scope>): <subject>`

*   **type**: `feat` (新功能), `fix` (修复bug), `docs` (文档), `style` (代码风格), `refactor` (代码重构), `test` (测试), `chore` (构建过程或辅助工具变动)。
*   **scope** (可选): 修改的范围，例如 `ui`, `core`, `crypto`。
*   **subject**: 简明扼要的描述。

**示例:**
*   `feat(ui): Add 2FA code scanning from screen`
*   `fix(core): Correctly handle CSV import with empty lines`
*   `docs: Update CONTRIBUTING.md with project structure`

### UI 和 QSS 样式

*   **组件化**: 尽可能将UI元素封装成可复用的组件，放在 `ui/components/` 目录下。
*   **关注点分离**: 视图（Views）应只负责展示，所有逻辑应放在控制器（Controllers）中处理。
*   **QSS 模块化**:
    *   基础窗口布局样式位于 `style.qss` 和 `style_dark.qss`。
    *   通用UI组件样式位于 `app_ui.qss` 和 `app_ui_dark.qss`。
    *   这些主文件通过 `@import` 导入位于 `ui/assets/styles/` 目录下的具体模块化样式文件。
    *   在修改样式时，请找到对应的模块文件（如 `buttons.qss`, `lists.qss`）进行修改。

## 贡献新的翻译

我们非常欢迎您为 SafeKey 添加新的语言支持！

1.  在 `language/locales/` 目录下，复制 `en.py` 并将其重命名为您要添加的语言代码（例如 `fr.py`）。
2.  打开新创建的文件，将 `translations` 字典中的所有英文字符串值翻译成您的语言。
3.  打开 `language/manager.py`，导入您的新语言文件，并将其添加到 `TRANSLATIONS` 字典中。
4.  提交包含这些修改的 Pull Request。

---

再次感谢您的时间和贡献！