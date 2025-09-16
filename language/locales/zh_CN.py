# language/locales/zh_CN.py

translations = {
    "2fa_delete_denied_title": "删除被阻止",
    "2fa_delete_denied_message": "此条目受两步验证 (2FA) 保护，无法直接删除。\n\n请先进入编辑模式，清除该条目的2FA密钥后，再执行删除操作。",
    "button_2fa_remove_key": "移除密钥",
    "settings_section_general": "常规设置",
    "settings_section_security": "安全设置",
    "settings_section_data": "数据管理",
    "settings_lang_title": "界面语言",
    "settings_lang_desc": "选择应用程序界面的显示语言。",
    "settings_change_pass_desc": "更改用于加密和解密您整个保险库的主密码。",
    "settings_change_pass_button": "更改...",
    "label_data_management": "保险库数据",
    "settings_data_desc": "为您的保险库创建一个安全的备份，或从其他文件导入数据。",
    "app_title": "Oracipher",
    "button_ok": "确 定",
    "button_save": "保 存",
    "button_cancel": "取 消",
    "button_done": "完 成",
    "button_exit": "退 出",
    "button_import": "导 入",
    "button_export": "导 出",
    "tooltip_set_cat_icon": "为该分类设置自定义图标",
    "error_cat_name_required": "请先输入分类名称，再设置图标。",
    "dialog_select_cat_icon": "为分类选择图标",
    "info_title_cat_icon_set": "图标已设置",
    "info_msg_cat_icon_set": "分类 '{name}' 的图标已设置。保存此条目后，图标将生效。",
    "setup_welcome": "欢迎使用 Oracipher",
    "setup_instruction": "请创建一个用于加密您所有数据的主密码。\n这个密码非常重要，请务必牢记。",
    "setup_placeholder": "设置主密码 (至少8位，建议包含混合字符)",
    "setup_confirm_placeholder": "确认主密码",
    "setup_button": "创建保险库",
    "unlock_welcome": "欢迎回来",
    "unlock_placeholder": "主密码",
    "unlock_button": "解 锁",
    "search_placeholder": "搜索...",
    "all_categories": "所有项目",
    "details_placeholder": "从列表中选择一个项目",
    "button_add_icon": "＋",
    "button_settings": "设置",
    "button_generate_password": "创建强密码",
    "button_add_account": "添加账户",
    "button_minimize": "最小化",
    "default_category": "未分类",
    "button_edit_icon": "✎",
    "button_delete_icon": "🗑",
    "button_copy": "复制",
    "button_copied": "已复制!",
    "button_show": "显示",
    "button_hide": "隐藏",
    "label_user": "用户名",
    "label_pass": "密码",
    "label_notes": "备注",
    "label_url": "网址",
    "label_backup_codes": "备用代码",
    "label_email": "邮箱",
    "tab_main": "主要",
    "tab_advanced": "高级",
    "tab_security": "TOTP",
    "tab_info": "附录",
    "add_title": "添加新条目",
    "edit_title": "编辑条目",
    "label_name": "账户名称",
    "label_cat": "分类",
    "placeholder_email": "例如: contact@example.com",
    "placeholder_name": "例如: Google",
    "placeholder_user": "例如: user@example.com",
    "placeholder_url": "例如: www.google.com",
    "placeholder_cat": "例如: 工作",
    "placeholder_backup_codes": "在此处粘贴您的备用代码。程序将自动为您排序和去重。",
    "button_fetch_icon": "获取图标",
    "button_custom_icon": "自定义图标",
    "tooltip_custom_icon": "点击设置自定义图标",
    "label_2fa_code": "身份验证器代码 (TOTP)",
    "label_2fa_status": "两步验证器:",
    "2fa_status_not_setup": "未设置",
    "2fa_status_enabled": "已启用",
    "2fa_status_enabled_pending_save": "已启用 (待保存)",
    "button_2fa_setup": "输入密钥...",
    "button_2fa_scan_qr": "从文件扫描...",
    "2fa_enter_secret_title": "输入两步验证 (2FA) 密钥",
    "2fa_enter_secret_instructions": "请输入服务提供商提供的密钥（通常被称为“手动设置密钥”）。程序会自动忽略空格。",
    "2fa_enter_secret_placeholder": "例如: JBSWY3DPEHPK3PXP",
    "2fa_error_invalid_key": "您输入的密钥似乎不是一个有效的Base32格式密钥，请检查后重试。",
    "2fa_error_invalid_qr": "在所选图像中未找到有效的两步验证二维码，请重试。",
    "gen_title": "密码生成器",
    "button_generate": "生成",
    "gen_label_len": "长度: {length}",
    "gen_check_upper": "大写字母 (A-Z)",
    "gen_check_num": "数字 (0-9)",
    "gen_check_sym": "符号 (!@#$)",
    "gen_no_charset": "请选择字符集",
    "settings_title": "设置",
    "tab_settings": "设置",
    "tab_instructions": "指南",
    "settings_theme_title": "应用主题",
    "settings_theme_desc": "选择应用程序的视觉外观。",
    "theme_light": "卢米娜亮色",
    "theme_dark": "德古拉暗色",
    "text_import_instructions": """
        <div style="text-align:center; margin-bottom: 20px;">
    <!-- 修改: 使用占位符 -->
    <img src="{app_icon_path}" alt="Logo" width="48" height="48">
    <h2 style="margin: 10px 0;">Oracipher</h2>
    <p style="margin-bottom: 15px;">简洁、安全、开源的本地密码管理器</p>
    <div style="text-align: center; margin-bottom: 15px;">
        <a href="https://github.com/EldricArlo/Oracipher/tree/10.8.0-version" style="text-decoration: none; margin: 0 5px;">
            <!-- 修改: 使用占位符 -->
            <img src="./images/github.svg" alt="GitHub" height="20">
        </a>
        <a href="https://t.me/+dHEs5v_mLfNjYjk0" style="text-decoration: none; margin: 0 5px;">
            <!-- 修改: 使用占位符 -->
            <img src="./images/telegram.svg" alt="Telegram" height="20">
        </a>
        <a href="https://www.python.org/" style="text-decoration: none; margin: 0 5px;">
            <!-- 修改: 使用占位符 -->
            <img src="./images/python.svg" alt="Python" height="20">
        </a>
        <a href="https://www.qt.io/" style="text-decoration: none; margin: 0 5px;">
            <img src="./images/qt.svg" alt="Qt" height="20">
        </a>
        <a href="https://www.samsung.com/" style="text-decoration: none; margin: 0 5px;">
            <img src="./images/samsung.svg" alt="Samsung" height="20">
        </a>
        <a href="https://www.google.com/" style="text-decoration: none; margin: 0 5px;">
            <img src="./images/google.svg" alt="Google" height="20">
        </a>
    </div>
</div>
<hr>

<h4>核心安全架构</h4>
<p>您的安全是我们的最高优先级。Oracipher 建立在一套经过严格验证的现代密码学原则之上，确保您的数据在任何时候都处于绝对安全的状态。</p>
<ul>
    <li><strong>零知识原则：</strong> 您的主密码是您唯一的私钥，它<strong>绝不会</strong>以任何形式被存储或传输。我们无法访问、查看或为您恢复它。<strong>您是您数据唯一的控制者。</strong></li>
    <li><strong>密钥派生 (Argon2id)：</strong> 我们使用目前业界最强大的密钥派生函数 <strong>Argon2id</strong>，将您的主密码“锤炼”成一个极其强大的256位加密密钥，有效抵御暴力破解。</li>
    <li><strong>认证加密 (AES-256-GCM)：</strong> 您的所有数据都使用 <strong>AES-256-GCM</strong> 算法进行加密，同时保证了数据的<strong>机密性</strong>（无法被读取）和<strong>完整性</strong>（无法被篡改）。</li>
</ul>
<hr>

<h4>隐私承诺</h4>
<p>我们坚信，您的数字身份和隐私应由您自己完全掌控。</p>
<ul>
    <li><strong>完全本地化存储：</strong> 您的整个加密保险库完全存储在您自己的本地设备上。没有任何云端服务器参与。</li>
    <li><strong>无追踪，无分析：</strong> 本应用程序不包含任何形式的用户行为追踪、数据分析或遥测代码。</li>
    <li><strong>开源透明：</strong> Oracipher 是一个开源项目，所有源代码都是公开的，任何人都可以审查我们的代码以验证我们的安全承诺。</li>
</ul>
<hr>

<h4>数据管理</h4>
<p>您可以通过设置中的导入和导出功能，完全掌控您的数据。</p>
<ul>
    <li><strong>安全备份 (<code>.pher</code> 格式)：</strong> 这是备份和迁移您保险库的<strong>唯一推荐方式</strong>。导出的 <code>.pher</code> 文件是一个完全加密的容器，受到您的主密码的保护。</li>
    <li><strong>从其他服务导入：</strong> 我们支持从主流密码管理器（如谷歌密码、三星密码本等）导出的标准文件进行导入。</li>
    <li><strong>非安全导出 (<code>.csv</code> 格式)：</strong> <strong>请务必谨慎使用此功能！</strong> 导出的CSV文件是一个**纯文本文件**，其中包含您所有的用户名和密码。</li>
</ul>
<hr>

<h4>关于与支持</h4>
<ul>
    <li><strong>发现问题或有功能建议？</strong> 我们欢迎任何形式的反馈！请在我们的 GitHub 仓库中提交一个 Issue。</li>
    <li><strong>GitHub 仓库：</strong> <a href="https://github.com/EldricArlo/Oracipher/tree/10.8.0-version">https://github.com/EldricArlo/Oracipher/tree/10.8.0-version</a></li>
    <li><strong>联系开发者：</strong> <a href="mailto:eldric520lol@gmail.com">eldric520lol@gmail.com</a></li>
    <li><strong>加入telegram群：</strong> <a href="https://t.me/+dHEs5v_mLfNjYjk0">https://t.me/+dHEs5v_mLfNjYjk0</a></li>
</ul>
    """,
    "change_pass_title": "修改主密码",
    "label_old_pass": "旧主密码",
    "label_new_pass": "新主密码",
    "label_confirm_pass": "确认新密码",
    "placeholder_old_pass": "输入您当前的主密码",
    "placeholder_new_pass": "设置新主密码",
    "placeholder_confirm_pass": "再次输入新主密码",
    "setup_success_title": "成功",
    "setup_success_msg": "保险库已创建！请使用您的新主密码解锁。",
    "error_title_generic": "错误",
    "error_title_weak_password": "密码强度不足",
    "error_title_mismatch": "密码不匹配",
    "error_msg_weak_password": "密码必须至少8位，且包含大写字母、小写字母和数字。",
    "error_msg_mismatch": "两次输入的密码不一致！",
    "error_msg_wrong_password": "主密码错误！",
    "msg_title_input_error": "输入错误",
    "msg_empty_name_error": "账户名称不能为空。",
    "msg_title_confirm_delete": "确认删除",
    "msg_confirm_delete": "您确定要删除 '{name}' 吗？",
    "msg_title_pass_change_success": "成功",
    "msg_pass_change_success": "主密码已成功修改！",
    "msg_title_pass_change_fail": "操作失败",
    "msg_pass_change_fail_old_wrong": "旧主密码不正确！",
    "msg_pass_change_fail_mismatch": "两次输入的新密码不一致！",
    "msg_pass_change_fail_weak": "新密码强度不足。",
    "msg_pass_change_fail_empty": "所有密码字段均不能为空。",
    "error_url_required": "请输入有效的网址以获取图标。",
    "error_fetch_failed": "无法从该网址获取图标。",
    "error_loading_icon": "加载所选图标文件时出错。",
    "settings_restart_msg": "请重启应用程序以使更改生效。",
    "dialog_select_icon": "选择一个图标文件",
    "dialog_image_files": "图片文件",
    "dialog_export_title": "导出保险库",
    "dialog_import_title": "导入保险库",
    "dialog_export_filter": "Oracipher 加密文件 (*.pher);;三星密码本 加密文件 (*.spass);;CSV (非安全) (*.csv)",
    "dialog_import_files": "所有支持的文件 (*.pher *.skey *.spass *.csv *.txt *.md);;Oracipher 加密文件 (*.pher);;三星密码本 (*.spass);;谷歌密码 (*.csv);;旧版 Oracipher 文件 (*.skey);;通用CSV文件 (*.csv);;文本文件 (*.txt *.md)",
    "msg_export_success_title": "导出成功",
    "msg_export_success": "{count} 个条目已成功导出到:\n{path}",
    "msg_export_fail_title": "导出失败",
    "msg_export_fail": "导出过程中发生错误: {error}",
    "msg_import_confirm_title": "确认导入",
    "msg_import_confirm": "您即将导入条目。\n这是一个智能合并操作。是否继续？",
    "msg_import_success_title": "导入成功",
    "msg_import_success": "操作完成！\n新增: {added_count}  更新: {updated_count}  跳过: {skipped_count}",
    "msg_import_fail_title": "导入失败",
    "msg_import_fail_message": "导入过程中发生错误:\n{error}",
    "dialog_input_password_label_pher": "请输入您要导入的 .pher 文件的创建密码：",
    "dialog_input_password_label_skey": "请输入您要导入的 .skey 文件的创建密码：",
    "dialog_input_password_label_spass": "请输入您要导入的 .spass 文件的创建密码：",
    "dialog_input_password_title": "需要密码",
    "warning_unsecure_export_title": "安全警告",
    "warning_unsecure_export_text": "您即将将数据导出为未加密的 CSV 文件。此文件为纯文本，任何人都可以读取您的密码。如需备份，请务必使用安全的 .pher 格式。\n\n您理解此风险并确定要继续吗？",
    "warning_include_totp_title": "包含 TOTP 密钥？",
    "warning_include_totp_text": "您是否要在未加密的CSV文件中包含2FA/TOTP密钥？\n\n警告：这样做极度危险！任何能接触到此文件的人都将能够生成您的两步验证码。\n\n您确定要继续吗？",
    "settings_auto_lock_title": "自动锁定保险库",
    "settings_auto_lock_desc": "在一段时间无操作后，自动锁定保险库以保护您的数据安全。",
    "minutes_suffix": "分钟",
    "error_import_file_not_found": "导入失败：无法找到所选文件。",
    "error_import_permission_denied": "导入失败：读取文件权限被拒绝。",
    "error_import_parsing_failed": "导入失败：无法解析文件内容。文件可能已损坏或格式不受支持。\n\n详情: {error}",
    "error_fetch_icon_network": "无法获取图标：发生网络错误。请检查您的网络连接。",
    "zxcvbn_feedback_weak": "这个密码太弱了。",
    "zxcvbn_feedback_common": "这是一个常用密码，不安全。",
    "zxcvbn_feedback_short": "这个密码太短了。",
    "acc_name_edit_entry": "编辑此条目",
    "acc_name_delete_entry": "删除此条目",
    "acc_name_copy_value": "复制内容",
    "acc_name_toggle_visibility": "切换密码可见性",
    "acc_name_set_category_icon": "为该分类设置自定义图标"
}