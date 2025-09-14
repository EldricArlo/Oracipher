# language/locales/en.py

translations = {
    "2fa_delete_denied_title": "Deletion Denied",
    "2fa_delete_denied_message": "This entry is protected by 2FA and cannot be deleted directly.\n\nPlease edit the entry and remove the 2FA secret key first.",
    "button_2fa_remove_key": "Remove Key",
    "settings_section_general": "General",
    "settings_section_security": "Security",
    "settings_section_data": "Data Management",
    "settings_lang_title": "Language",
    "settings_lang_desc": "Choose the display language for the user interface.",
    "settings_change_pass_desc": "Change the password used to encrypt and decrypt your entire vault.",
    "settings_change_pass_button": "Change...",
    "label_data_management": "Vault Data",
    "settings_data_desc": "Create a secure backup of your vault, or import data from another file.",
    "app_title": "Oracipher",
    "button_ok": "OK",
    "button_save": "Save",
    "button_cancel": "Cancel",
    "button_done": "Done",
    "button_exit": "Exit",
    "button_import": "Import",
    "button_export": "Export",
    "tooltip_set_cat_icon": "Set custom icon for this category",
    "error_cat_name_required": "Please enter a category name before setting an icon.",
    "dialog_select_cat_icon": "Select Icon for Category",
    "info_title_cat_icon_set": "Icon Set",
    "info_msg_cat_icon_set": "Icon for '{name}' is set. It will be saved when you save this entry.",
    "setup_welcome": "Welcome to Oracipher",
    "setup_instruction": "Please create a master password to encrypt all your data.\nThis password is very important, remember it well.",
    "setup_placeholder": "Set Master Password (min. 8 chars, mixed)",
    "setup_confirm_placeholder": "Confirm Master Password",
    "setup_button": "Create Vault",
    "unlock_welcome": "Welcome Back",
    "unlock_placeholder": "Master Password",
    "unlock_button": "Unlock",
    "search_placeholder": "Search...",
    "all_categories": "All Items",
    "details_placeholder": "Select an item from the list",
    "button_add_icon": "＋",
    "button_settings": "Settings",
    "button_generate_password": "Generate Password",
    "button_add_account": "Add Account",
    "button_minimize": "Minimize",
    "default_category": "Uncategorized",
    "button_edit_icon": "✎",
    "button_delete_icon": "🗑",
    "button_copy": "Copy",
    "button_copied": "Copied!",
    "button_show": "Show",
    "button_hide": "Hide",
    "label_user": "Username",
    "label_pass": "Password",
    "label_notes": "Notes",
    "label_url": "URL",
    "label_backup_codes": "Backup Codes",
    "label_email": "Email",
    "tab_main": "Main",
    "tab_advanced": "Advanced",
    "tab_security": "TOTP",
    # --- MODIFICATION START: Renamed the tab ---
    "tab_info": "Appendix",
    # --- MODIFICATION END ---
    "add_title": "Add New Entry",
    "edit_title": "Edit Entry",
    "label_name": "Account Name",
    "label_cat": "Category",
    "placeholder_email": "e.g., contact@example.com",
    "placeholder_name": "e.g., Google",
    "placeholder_user": "e.g., user@example.com",
    "placeholder_url": "e.g., www.google.com",
    "placeholder_cat": "e.g., Work",
    "placeholder_backup_codes": "Paste your codes here. They will be automatically sorted and deduplicated.",
    "button_fetch_icon": "Fetch Icon",
    "button_custom_icon": "Custom Icon",
    "tooltip_custom_icon": "Click to set a custom icon",
    "label_2fa_code": "Authenticator Code (TOTP)",
    "label_2fa_status": "2FA Authenticator:",
    "2fa_status_not_setup": "Not set up",
    "2fa_status_enabled": "Enabled",
    "2fa_status_enabled_pending_save": "Enabled (pending save)",
    "button_2fa_setup": "Enter Key...",
    "button_2fa_scan_qr": "Scan from File...",
    "2fa_enter_secret_title": "Enter 2FA Secret Key",
    "2fa_enter_secret_instructions": "Enter the secret key (often called 'manual setup key') provided by the service. Spaces will be ignored.",
    "2fa_enter_secret_placeholder": "e.g., JBSWY3DPEHPK3PXP",
    "2fa_error_invalid_key": "The key you entered does not appear to be a valid Base32 secret key. Please check and try again.",
    "2fa_error_invalid_qr": "No valid 2FA QR code was found in the selected image. Please try again.",
    "gen_title": "Password Generator",
    "button_generate": "Generate",
    "gen_label_len": "Length: {length}",
    "gen_check_upper": "Uppercase (A-Z)",
    "gen_check_num": "Numbers (0-9)",
    "gen_check_sym": "Symbols (!@#$)",
    "gen_no_charset": "Please select a character set",
    "settings_title": "Settings",
    "tab_settings": "Settings",
    "tab_instructions": "Guide",
    "settings_theme_title": "Application Theme",
    "settings_theme_desc": "Choose the visual appearance of the application.",
    "theme_light": "Lumina Glow",
    "theme_dark": "Dracula Dark",
    "text_import_instructions": """
        <div style="text-align:center; margin-bottom: 20px;">
    <!-- 修改: 使用占位符 -->
    <img src="{app_icon_path}" alt="Logo" width="48" height="48">
    <h2 style="margin: 10px 0;">Oracipher</h2>
    <p style="margin-bottom: 15px;">A simple, secure, and open-source local password manager.</p>
    <div style="text-align: center; margin-bottom: 15px;">
        <a href="https://github.com/EldricArlo/Oracipher/tree/10.8.0-version" style="text-decoration: none; margin: 0 5px;">
            <!-- 修改: 使用占位符 -->
            <img src="{github_icon_path}" alt="GitHub" height="20">
        </a>
        <a href="https://t.me/+dHEs5v_mLfNjYjk0" style="text-decoration: none; margin: 0 5px;">
            <!-- 修改: 使用占位符 -->
            <img src="{telegram_icon_path}" alt="Telegram" height="20">
        </a>
        <a href="https://www.python.org/" style="text-decoration: none; margin: 0 5px;">
            <!-- 修改: 使用占位符 -->
            <img src="{python_icon_path}" alt="Python" height="20">
        </a>
    </div>
</div>
<hr>

<h4>Core Security Architecture</h4>
<p>Your security is our highest priority. Oracipher is built on a set of rigorously vetted, modern cryptographic principles to ensure your data is safe at all times.</p>
<ul>
    <li><strong>Zero-Knowledge Principle:</strong> Your Master Password is your private key. It is <strong>never</strong> stored or transmitted in any form. We cannot access, view, or recover it for you. <strong>You are in sole control of your data.</strong></li>
    <li><strong>Key Derivation (Argon2id):</strong> We use the industry-leading KDF <strong>Argon2id</strong> to forge your password into an incredibly strong 256-bit encryption key, providing powerful resistance against brute-force attacks.</li>
    <li><strong>Authenticated Encryption (AES-256-GCM):</strong> All your data is encrypted using <strong>AES-256-GCM</strong>, which provides both <strong>Confidentiality</strong> (it cannot be read) and <strong>Integrity</strong> (it cannot be tampered with).</li>
</ul>
<hr>

<h4>Privacy Commitment</h4>
<p>We firmly believe that your digital identity and privacy should be under your complete control.</p>
<ul>
    <li><strong>Fully Local Storage:</strong> Your entire encrypted vault is stored exclusively on your own local device. No cloud servers are involved.</li>
    <li><strong>No Tracking, No Analytics:</strong> This application contains no user tracking, data analytics, or telemetry code of any kind.</li>
    <li><strong>Open-Source Transparency:</strong> Oracipher is an open-source project. All source code is publicly available for anyone to review and audit.</li>
</ul>
<hr>

<h4>Data Management</h4>
<p>You have full control over your data via the Import and Export functions in the settings.</p>
<ul>
    <li><strong>Secure Backup (<code>.skey</code> format):</strong> This is the <strong>only recommended way</strong> to back up your vault. The exported <code>.skey</code> file is a fully encrypted container protected by your Master Password.</li>
    <li><strong>Importing from Other Services:</strong> We support importing from standard files exported by major password managers like Google Password and Samsung Pass.</li>
    <li><strong>Unsecured Export (<code>.csv</code> format):</strong> <strong>Use with extreme caution!</strong> The exported CSV is a <strong>plain text file</strong> containing all of your usernames and passwords.</li>
</ul>
<hr>

<h4>About & Support</h4>
<ul>
    <li><strong>Found an issue or have a suggestion?</strong> We welcome all feedback! Please open an Issue on our GitHub repository.</li>
    <li><strong>GitHub Repository:</strong> <a href="https://github.com/EldricArlo/Oracipher/tree/10.8.0-version">https://github.com/EldricArlo/Oracipher/tree/10.8.0-version</a></li>
    <li><strong>Contact the Developer:</strong> <a href="mailto:eldric520lol@gmail.com">eldric520lol@gmail.com</a></li>
    <li><strong>Join group of Telegram</strong> <a href="https://t.me/+dHEs5v_mLfNjYjk0">https://t.me/+dHEs5v_mLfNjYjk0</a></li>
</ul>
    """,
    "change_pass_title": "Change Master Password",
    "label_old_pass": "Old Password",
    "label_new_pass": "New Password",
    "label_confirm_pass": "Confirm New",
    "placeholder_old_pass": "Enter your current master password",
    "placeholder_new_pass": "Set a new master password",
    "placeholder_confirm_pass": "Confirm the new master password",
    "setup_success_title": "Success",
    "setup_success_msg": "Vault created! Please unlock with your new master password.",
    "error_title_generic": "Error",
    "error_title_weak_password": "Weak Password",
    "error_title_mismatch": "Passwords Do Not Match",
    "error_msg_weak_password": "Password must be at least 8 characters and contain uppercase, lowercase, and digits.",
    "error_msg_mismatch": "The passwords entered do not match!",
    "error_msg_wrong_password": "Incorrect master password!",
    "msg_title_input_error": "Input Error",
    "msg_empty_name_error": "Account name cannot be empty.",
    "msg_title_confirm_delete": "Confirm Deletion",
    "msg_confirm_delete": "Are you sure you want to delete '{name}'?",
    "msg_title_pass_change_success": "Success",
    "msg_pass_change_success": "Master password has been changed successfully!",
    "msg_title_pass_change_fail": "Operation Failed",
    "msg_pass_change_fail_old_wrong": "The old master password is not correct!",
    "msg_pass_change_fail_mismatch": "The new passwords do not match!",
    "msg_pass_change_fail_weak": "New password is too weak.",
    "msg_pass_change_fail_empty": "All password fields are required.",
    "error_url_required": "Please enter a valid URL to fetch an icon.",
    "error_fetch_failed": "Could not fetch an icon from this URL.",
    "error_loading_icon": "There was an error loading the selected icon file.",
    "settings_restart_msg": "Please restart the application for changes to take effect.",
    "dialog_select_icon": "Select an Icon File",
    "dialog_image_files": "Image Files",
    "dialog_export_title": "Export Vault",
    "dialog_import_title": "Import Vault",
    "dialog_export_filter": "Oracipher Encrypted File (*.skey);;CSV (Unsecure) (*.csv)",
    "dialog_import_files": "All Supported Files (*.skey *.spass *.csv *.txt *.md);;Samsung Pass (*.spass);;Google Chrome (*.csv);;Oracipher Encrypted File (*.skey);;Generic CSV (*.csv);;Text Files (*.txt *.md)",
    "msg_export_success_title": "Export Successful",
    "msg_export_success": "{count} entries have been successfully exported to:\n{path}",
    "msg_export_fail_title": "Export Failed",
    "msg_export_fail": "An error occurred during export: {error}",
    "msg_import_confirm_title": "Confirm Import",
    "msg_import_confirm": "You are about to import entries.\nThis is a smart merge operation. Continue?",
    "msg_import_success_title": "Import Successful",
    "msg_import_success": "Operation complete!\nAdded: {added_count}  Updated: {updated_count}  Skipped: {skipped_count}",
    "msg_import_fail_title": "Import Failed",
    # --- MODIFICATION START: Add new keys ---
    "msg_import_fail_message": "An error occurred during import:\n{error}",
    "dialog_input_password_label_skey": "Please enter the password for the .skey file you are importing:",
    "dialog_input_password_label_spass": "Please enter the password for the .spass file you are importing:",
    # --- MODIFICATION END ---
    "warning_unsecure_export_title": "Security Warning",
    "warning_unsecure_export_text": "You are about to export your data as an unencrypted CSV file. This file will be human-readable and contain all your passwords in plain text. For backups, please use the secure .skey format.\n\nDo you understand the risk and wish to continue?",
    "warning_include_totp_title": "Include TOTP Secrets?",
    "warning_include_totp_text": "Do you want to include 2FA/TOTP secret keys in the unencrypted CSV file?\n\nWARNING: This is extremely dangerous! Anyone with access to this file will be able to generate your two-factor codes.\n\nAre you sure you want to continue?",
    "settings_auto_lock_title": "Auto-lock Vault",
    "settings_auto_lock_desc": "Automatically lock the vault after a period of inactivity to keep your data safe.",
    "minutes_suffix": "min",
}
