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
    # --- MODIFICATION START: Renamed the tab ---
    "tab_info": "附录",
    # --- MODIFICATION END ---
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
        <h2>欢迎使用 Oracipher</h2>
        <p>本指南将为您提供关于此密码管理器的安全性、隐私保护和核心功能的关键信息。</p>
        <hr>
        <h4>核心安全架构</h4>
        <p>您的安全是我们的最高优先级。Oracipher 建立在经过验证的、现代的密码学原则之上：</p>
        <ul>
            <li><strong>零知识 (Zero-Knowledge):</strong> 您的主密码是您的私钥。它<strong>绝不会</strong>被存储在您的设备上，也绝不会被传输到任何地方。我们无法访问、查看或为您恢复它。<em>您是唯一的控制者。</em></li>
            <li><strong>密钥派生 (Argon2id):</strong> 我们使用 Argon2id 将您的主密码转换为一个强大的加密密钥。这是一个内存困难型函数，可以有效抵御暴力破解攻击。</li>
            <li><strong>认证加密 (AES-256):</strong> 您保险库中的所有数据都使用 AES-256-GCM 进行加密。这同时确保了数据的机密性（您的数据是秘密的）和完整性（您的数据无法被悄悄篡改）。</li>
        </ul>
        <h4>您的隐私承诺</h4>
        <p>我们坚信，您的数据只属于您自己。</p>
        <ul>
            <li><strong>本地优先存储:</strong> 您的整个加密保险库完全存储在您的本地设备中。没有云服务器，您的数据除非您明确导出，否则绝不会离开您的计算机。</li>
            <li><strong>无追踪，无分析:</strong> 本应用程序不收集任何使用数据、遥测信息或崩溃报告。您在应用内的所有活动都只属于您自己。</li>
        </ul>
        <hr>
        <h4>数据管理</h4>
        <p>您可以通过设置中的导入和导出功能完全控制您的数据。</p>
        <ul>
            <li><strong>安全备份 (.skey):</strong> <em>.skey</em> 格式是备份保险库的推荐方式。它是一个完全加密的文件，包含了您的所有条目，并受您的主密码保护。</li>
            <li><strong>非安全导出 (.csv):</strong> 提供CSV格式是为了与其他应用程序兼容。<strong>警告：</strong>CSV文件是一个纯文本文件。任何能访问此文件的人都可以读取您所有的用户名和密码。请极其谨慎地使用此格式。</li>
        </ul>
        <hr>
        <h4>关于与联系</h4>
        <p>Oracipher 是一个注重安全和隐私的开源项目。</p>
        <ul>
            <li><strong>发现问题或有功能建议？</strong>欢迎在我们的 GitHub 仓库中提交 Issue。</li>
            <li><strong>GitHub:</strong> <a href="https://github.com/your-repo/oracipher">github.com/your-repo/oracipher</a></li>
            <li><strong>联系开发者:</strong> <a href="mailto:developer@example.com">developer@example.com</a></li>
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
    "dialog_export_filter": "Oracipher 加密文件 (*.skey);;CSV (非安全) (*.csv)",
    "dialog_import_files": "所有支持的文件 (*.skey *.csv *.txt *.md);;Oracipher 加密文件 (*.skey);;CSV 文件 (*.csv);;文本文件 (*.txt *.md)",
    "msg_export_success_title": "导出成功",
    "msg_export_success": "{count} 个条目已成功导出到:\n{path}",
    "msg_export_fail_title": "导出失败",
    "msg_export_fail": "导出过程中发生错误: {error}",
    "msg_import_confirm_title": "确认导入",
    "msg_import_confirm": "您即将导入条目。\n这是一个智能合并操作。是否继续？",
    "msg_import_success_title": "导入成功",
    "msg_import_success": "操作完成！\n新增: {added_count}  更新: {updated_count}  跳过: {skipped_count}",
    "msg_import_fail_title": "导入失败",
    "dialog_input_password_title": "需要密码",
    "dialog_input_password_label": "请输入您要导入的 .skey 文件的创建密码：",
    "warning_unsecure_export_title": "安全警告",
    "warning_unsecure_export_text": "您即将将数据导出为未加密的 CSV 文件。此文件为纯文本，任何人都可以读取您的密码。如需备份，请务必使用安全的 .skey 格式。\n\n您理解此风险并确定要继续吗？",
    "warning_include_totp_title": "包含 TOTP 密钥？",
    "warning_include_totp_text": "您是否要在未加密的CSV文件中包含2FA/TOTP密钥？\n\n警告：这样做极度危险！任何能接触到此文件的人都将能够生成您的两步验证码。\n\n您确定要继续吗？",
    "settings_auto_lock_title": "自动锁定保险库",
    "settings_auto_lock_desc": "在一段时间无操作后，自动锁定保险库以保护您的数据安全。",
    "minutes_suffix": "分钟",
}