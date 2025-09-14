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
        <h2>Welcome to Oracipher</h2>
        <p>This guide provides essential information about the security, privacy, and core functions of your new password manager.</p>
        <hr>
        <h4>Core Security Architecture</h4>
        <p>Your security is our highest priority. Oracipher is built on a foundation of proven, modern cryptographic principles:</p>
        <ul>
            <li><strong>Zero-Knowledge:</strong> Your Master Password is your private key. It is <em>never</em> stored on your device or transmitted anywhere. We cannot access, view, or recover it for you. <em>You are in sole control.</em></li>
            <li><strong>Key Derivation (Argon2id):</strong> We use Argon2id to transform your Master Password into a powerful encryption key. This is a memory-hard function that provides strong resistance against brute-force attacks.</li>
            <li><strong>Authenticated Encryption (AES-256):</strong> All data in your vault is encrypted using AES-256 with GCM. This ensures both confidentiality (your data is secret) and integrity (your data cannot be tampered with undetected).</li>
        </ul>
        <h4>Your Privacy Commitment</h4>
        <p>We believe that your data belongs to you, and only you.</p>
        <ul>
            <li><strong>Local-First Storage:</strong> Your entire encrypted vault is stored exclusively on your local device. There is no cloud server, and your data never leaves your computer unless you explicitly export it.</li>
            <li><strong>No Tracking, No Analytics:</strong> This application does not collect any usage data, telemetry, or crash reports. Your activity within the app is your business alone.</li>
        </ul>
        <hr>
        <h4>Data Management</h4>
        <p>You have full control over your data through the Import and Export functions in the settings.</p>
        <ul>
            <li><strong>Secure Backup (.skey):</strong> The <em>.skey</em> format is the recommended way to back up your vault. It's a fully encrypted file that contains all your entries and is protected by your master password.</li>
            <li><strong>Unsecured Export (.csv):</strong> The CSV format is provided for compatibility with other applications. <strong>Warning:</strong> A CSV file is a plain text file. Anyone with access to it can read all your usernames and passwords. Use this format with extreme caution.</li>
        </ul>
        <hr>
        <h4>About & Contact</h4>
        <p>Oracipher is an open-source project developed with a focus on security and privacy.</p>
        <ul>
            <li><strong>Found an issue or have a suggestion?</strong> Please open an issue on our GitHub repository.</li>
            <li><strong>GitHub:</strong> <a href="https://github.com/your-repo/oracipher">github.com/your-repo/oracipher</a></li>
            <li><strong>Contact the developer:</strong> <a href="mailto:developer@example.com">developer@example.com</a></li>
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
    "dialog_import_files": "All Supported Files (*.skey *.csv *.txt *.md);;Oracipher Encrypted File (*.skey);;CSV Files (*.csv);;Text Files (*.txt *.md)",
    "msg_export_success_title": "Export Successful",
    "msg_export_success": "{count} entries have been successfully exported to:\n{path}",
    "msg_export_fail_title": "Export Failed",
    "msg_export_fail": "An error occurred during export: {error}",
    "msg_import_confirm_title": "Confirm Import",
    "msg_import_confirm": "You are about to import entries.\nThis is a smart merge operation. Continue?",
    "msg_import_success_title": "Import Successful",
    "msg_import_success": "Operation complete!\nAdded: {added_count}  Updated: {updated_count}  Skipped: {skipped_count}",
    "msg_import_fail_title": "Import Failed",
    "dialog_input_password_title": "Password Required",
    "dialog_input_password_label": "Please enter the master password for the .skey file you are importing:",
    "warning_unsecure_export_title": "Security Warning",
    "warning_unsecure_export_text": "You are about to export your data as an unencrypted CSV file. This file will be human-readable and contain all your passwords in plain text. For backups, please use the secure .skey format.\n\nDo you understand the risk and wish to continue?",
    "warning_include_totp_title": "Include TOTP Secrets?",
    "warning_include_totp_text": "Do you want to include 2FA/TOTP secret keys in the unencrypted CSV file?\n\nWARNING: This is extremely dangerous! Anyone with access to this file will be able to generate your two-factor codes.\n\nAre you sure you want to continue?",
    "settings_auto_lock_title": "Auto-lock Vault",
    "settings_auto_lock_desc": "Automatically lock the vault after a period of inactivity to keep your data safe.",
    "minutes_suffix": "min",
}