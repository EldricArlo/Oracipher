# language.py

import logging

logger = logging.getLogger(__name__)

class LanguageManager:
    """
    管理应用程序中的所有UI文本翻译。

    这个类被实现为一个“事实上的”单例模式。一个全局实例 `t` 在模块末尾被创建，
    应用程序的所有其他部分都应该导入并使用这个实例，以确保语言设置的一致性。
    """
    def __init__(self):
        """
        初始化语言管理器。
        """
        self._language = 'en'  # 默认语言
        # TRANSLATIONS 字典是所有翻译的中央存储库。
        # 键是语言代码 (如 'en', 'zh_CN')，值是另一个字典，
        # 其中包含该语言的所有翻译键和对应的文本。
        self.TRANSLATIONS = {
            'en': {
                # --- General & Shared ---
                'app_title': "SafeKey",
                'button_ok': "OK",
                'button_save': "Save",
                'button_cancel': "Cancel",
                'button_generate': "Generate",
                'button_show': "Show",
                'button_hide': "Hide",
                'button_copy': "Copy",
                'button_copied': "Copied!",
                'button_done': "Done",
                'label_name': "Account Name",
                'label_user': "Username / Email",
                'label_pass': "Password",
                'label_cat': "Category",
                'label_notes': "Notes",

                # --- Unlock Screen ---
                'setup_welcome': "Welcome to SafeKey",
                'setup_instruction': "Please create a master password to encrypt all your data.\nThis password is very important, remember it well.",
                'setup_placeholder': "Set Master Password (min. 8 chars, mixed)",
                'setup_confirm_placeholder': "Confirm Master Password",
                'setup_button': "Create Vault",
                'setup_success_title': "Success",
                'setup_success_msg': "Vault created! Please unlock with your new master password.",
                'unlock_welcome': "Welcome Back",
                'unlock_placeholder': "Master Password",
                'unlock_button': "Unlock",
                'button_exit': "Exit",
                'error_title_generic': "Error",
                'error_title_weak_password': "Weak Password",
                'error_title_mismatch': "Passwords Do Not Match",
                'error_msg_weak_password': "Password must be at least 8 characters and contain uppercase, lowercase, and digits.",
                'error_msg_mismatch': "The passwords entered do not match!",
                'error_msg_wrong_password': "Incorrect master password!",

                # --- Main Interface ---
                'search_placeholder': "Search...",
                'all_categories': "All Items",
                'details_placeholder': "Select an item from the list",
                'button_add_icon': "＋",
                'button_edit_icon': "✎",
                'button_delete_icon': "🗑",
                'button_settings': "Settings",
                'button_generate_password': "Generate Password",
                'button_add_account': "Add Account",
                'button_minimize': "—",
                'msg_title_input_error': "Input Error",
                'msg_empty_name_error': "Account name cannot be empty.",
                'msg_title_confirm_delete': "Confirm Deletion",
                'msg_confirm_delete': "Are you sure you want to delete '{name}'?",
                'msg_title_pass_change_success': "Success",
                'msg_pass_change_success': "Master password has been changed successfully!",
                'msg_title_pass_change_fail': "Operation Failed",
                'msg_pass_change_fail_old_wrong': "The old master password is not correct!",
                'msg_pass_change_fail_mismatch': "The new passwords do not match!",
                'msg_pass_change_fail_weak': "New password is too weak. It must be at least 8 characters and contain uppercase, lowercase, and digits.",
                'msg_pass_change_fail_empty': "All password fields are required.",

                # --- Dialogs ---
                'add_title': "Add New Entry",
                'edit_title': "Edit Entry",
                'placeholder_name': "e.g., Google",
                'placeholder_user': "e.g., user@example.com",
                'placeholder_cat': "e.g., Work",
                'gen_title': "Password Generator",
                'gen_label_len': "Length: {length}",
                'gen_check_upper': "Uppercase (A-Z)",
                'gen_check_num': "Numbers (0-9)",
                'gen_check_sym': "Symbols (!@#$)",
                'gen_no_charset': "Please select a character set",
                'change_pass_title': "Change Master Password",
                'label_old_pass': "Old Password",
                'label_new_pass': "New Password",
                'label_confirm_pass': "Confirm New",
                'placeholder_old_pass': "Enter your current master password",
                'placeholder_new_pass': "Set a new master password",
                'placeholder_confirm_pass': "Confirm the new master password",
                'settings_title': "Settings",
                'settings_lang_label': "Language",
                'settings_restart_msg': "Language settings saved. Please restart the application for changes to take effect.",
            },
            'zh_CN': {
                # --- 通用 & 共享 ---
                'app_title': "SafeKey",
                'button_ok': "确 定",
                'button_save': "保 存",
                'button_cancel': "取 消",
                'button_generate': "生成",
                'button_show': "显示",
                'button_hide': "隐藏",
                'button_copy': "复制",
                'button_copied': "已复制!",
                'button_done': "完 成",
                'label_name': "账户名称",
                'label_user': "用户名/邮箱",
                'label_pass': "密码",
                'label_cat': "分类",
                'label_notes': "备注",

                # --- 解锁界面 ---
                'setup_welcome': "欢迎使用 SafeKey",
                'setup_instruction': "请创建一个用于加密您所有数据的主密码。\n这个密码非常重要，请务必牢记。",
                'setup_placeholder': "设置主密码 (至少8位，建议包含混合字符)",
                'setup_confirm_placeholder': "确认主密码",
                'setup_button': "创建保险库",
                'setup_success_title': "成功",
                'setup_success_msg': "保险库已创建！请使用您的新主密码解锁。",
                'unlock_welcome': "欢迎回来",
                'unlock_placeholder': "主密码",
                'unlock_button': "解 锁",
                'button_exit': "退 出",
                'error_title_generic': "错误",
                'error_title_weak_password': "密码强度不足",
                'error_title_mismatch': "密码不匹配",
                'error_msg_weak_password': "密码必须至少8位，且包含大写字母、小写字母和数字。",
                'error_msg_mismatch': "两次输入的密码不一致！",
                'error_msg_wrong_password': "主密码错误！",

                # --- 主界面 ---
                'search_placeholder': "搜索...",
                'all_categories': "所有项目",
                'details_placeholder': "从列表中选择一个项目",
                'button_add_icon': "＋",
                'button_edit_icon': "✎",
                'button_delete_icon': "🗑",
                'button_settings': "设 置",
                'button_generate_password': "创建强密码",
                'button_add_account': "添加账户",
                'button_minimize': "—",
                'msg_title_input_error': "输入错误",
                'msg_empty_name_error': "账户名称不能为空。",
                'msg_title_confirm_delete': "确认删除",
                'msg_confirm_delete': "您确定要删除 '{name}' 吗？",
                'msg_title_pass_change_success': "成功",
                'msg_pass_change_success': "主密码已成功修改！",
                'msg_title_pass_change_fail': "操作失败",
                'msg_pass_change_fail_old_wrong': "旧主密码不正确！",
                'msg_pass_change_fail_mismatch': "两次输入的新密码不一致！",
                'msg_pass_change_fail_weak': "新密码强度不足。必须至少8位，且包含大写字母、小写字母和数字。",
                'msg_pass_change_fail_empty': "所有密码字段均不能为空。",

                # --- 对话框 ---
                'add_title': "添加新条目",
                'edit_title': "编辑条目",
                'placeholder_name': "例如: Google",
                'placeholder_user': "例如: user@example.com",
                'placeholder_cat': "例如: 工作",
                'gen_title': "密码生成器",
                'gen_label_len': "长度: {length}",
                'gen_check_upper': "大写字母 (A-Z)",
                'gen_check_num': "数字 (0-9)",
                'gen_check_sym': "符号 (!@#$)",
                'gen_no_charset': "请选择字符集",
                'change_pass_title': "修改主密码",
                'label_old_pass': "旧主密码",
                'label_new_pass': "新主密码",
                'label_confirm_pass': "确认新密码",
                'placeholder_old_pass': "输入您当前的主密码",
                'placeholder_new_pass': "设置新主密码",
                'placeholder_confirm_pass': "再次输入新主密码",
                'settings_title': "设置",
                'settings_lang_label': "语言",
                'settings_restart_msg': "语言设置已保存。请重启应用程序以使更改生效。",
            }
        }
    
    def set_language(self, lang_code: str):
        """
        设置当前要使用的语言。

        Args:
            lang_code (str): 目标语言的代码 (例如 'en', 'zh_CN')。
        """
        if lang_code in self.TRANSLATIONS:
            self._language = lang_code
        else:
            logger.warning(f"语言代码 '{lang_code}' 未在翻译库中找到。将回退到 'en'。")
            self._language = 'en'

    def get(self, key: str, **kwargs) -> str:
        """
        获取指定键的翻译文本。

        此方法支持带占位符的字符串格式化。

        Args:
            key (str): 翻译字典中的键。
            **kwargs: 用于格式化字符串的键值对。
                      例如: t.get('msg_confirm_delete', name="MyAccount")

        Returns:
            str: 翻译后的文本。如果找不到键，则返回键本身作为备用。
        """
        try:
            translation = self.TRANSLATIONS[self._language][key]
            if kwargs:
                return translation.format(**kwargs)
            return translation
        except KeyError:
            logger.warning(f"翻译键 '{key}' 在语言 '{self._language}' 中未找到。")
            return key # Fallback to the key itself

    def get_available_languages(self) -> dict[str, str]:
        """
        获取所有可用语言的代码和显示名称的字典。

        Returns:
            dict[str, str]: 一个映射 {language_code: display_name} 的字典。
        """
        return {
            'en': 'English',
            'zh_CN': '简体中文'
        }

# 创建全局实例，以便在整个应用程序中轻松访问。
# 在其他模块中，只需 `from language import t` 即可使用。
t = LanguageManager()