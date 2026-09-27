# Database License & Anti-Copy Protection Manager

**Vendor:** DIGITALUB ANGOLA  
**Support:** `suporte@digitalub.ao`  
**License:** OPL-1 (Commercial)  
**Supported Odoo Versions:** 17.0, 18.0, 19.0 (Community & Enterprise)

---

## 📌 Overview

The **Database License & Anti-Copy Protection Manager** provides enterprise-grade cryptographic software licensing and anti-piracy protection for proprietary Odoo modules, client customizations, and recurring SaaS contracts.

### Key Capabilities:
- **RSA-2048 Asymmetric Signatures:** Tamper-proof token validation using industry-standard RS256 cryptography with zero external server dependencies (100% offline verification).
- **UUID Anti-Copy Protection:** Cryptographically binds each license to the target database UUID. Restoring or cloning the database onto another server invalidates the license immediately.
- **Session Control:** Force automatic user session termination when the browser is closed.
- **Automated Email Alerts:** Proactive warning emails sent to company administrators and support at milestones: 30, 15, 7, 5, 3, 2, 1, and 0 days prior to expiration.
- **Pre-Login & Systray Monitoring:** Live 3-state shield widget in the Systray and pre-login banner and status badge on the authentication screen.
- **Real-Time Lockout:** Blocks non-admin access upon license expiration or tampering, while granting administrators persistent bypass to renew licenses.
- **Multi-Language (i18n):** Native support for English, French, Portuguese (PT & BR), and Spanish.

---

## 🔐 Cryptographic Architecture

1. **Private Key (`private_key.pem`):** Kept strictly confidential by the software vendor (Digitalub). Used only to sign new license tokens. Never shared or installed on client servers.
2. **Public Key (`public_key.pem`):** Configured in the client's Odoo Settings (`Settings > Licensing`). Used by the module to verify that tokens were issued by Digitalub.
3. **License Token (JWT):** A signed string containing the client name, database UUID, and expiration timestamp.

---

## 🚀 How to Generate License Tokens

### Step 1: Initialize Local License Tools (One-Time Setup)

Inside the repository root or module folder, run the setup script to initialize your local RSA keys and generator tool in `~/license_tools`:

```bash
python3 tools/setup_license_tools.py
```

This creates:
- `~/license_tools/private_key.pem` (Permissions: 600)
- `~/license_tools/public_key.pem`
- `~/license_tools/generate_license.py`

---

### Step 2: Obtain the Client Database UUID

Ask the client for their database UUID, or locate it in their Odoo instance:
- **Via UI:** In Developer Mode, go to **Settings > Technical > Parameters > System Parameters** and look for `database.uuid`.
- **Via Pre-Login / Settings:** The license configuration screen in **Settings > Licensing** displays the status and UUID.

---

### Step 3: Generate the License Token

#### Option A: Command Line Generator
```bash
python3 ~/license_tools/generate_license.py --client "CLIENT NAME" --uuid "DATABASE_UUID" --days 365
```

**Example:**
```bash
python3 ~/license_tools/generate_license.py --client "KING PEDZIO" --uuid "d22df021-ba05-11f1-81a4-00155d4b9e22" --days 365
```

#### Option B: Interactive Mode
```bash
python3 ~/license_tools/generate_license.py
```
You will be prompted to enter the Client Name, Database UUID, and Validity in days.

#### Option C: One-Click Copy to Windows Clipboard (WSL2)
To copy the clean token directly to your Windows clipboard with zero spaces, run:
```bash
python3 -c "import sys; sys.path.append('/home/bvieira/license_tools'); from generate_license import create_token; t, _, _ = create_token('CLIENT NAME', 'DATABASE_UUID', 365); print(t.strip(), end='')" | clip.exe
```
Then simply press `Ctrl + V` in the browser.

---

## 🛠️ How to Activate the License in Odoo

1. Log in to the client Odoo instance as **Administrator** (`admin`).
2. Navigate to **Settings > Licensing** (Definições > Licenciamento).
3. Ensure the **RSA Public Key** field contains the official Digitalub public key.
4. Paste the generated **License Token** into the **License Key / Token** field.
5. Click **Save**.
6. The license status badge will immediately turn green (**Valid**) showing the expiration date.

> **Note:** The module automatically sanitizes token input by stripping extra spaces, newlines, or carriage returns caused by copying from email or chat clients.

---

## 💡 Running Odoo in Background (Preventing Server Shutdowns)

When testing Odoo in the terminal, running `python3 odoo-bin ...` executes in the **foreground**. If you press `Ctrl + C` or close the terminal window, the Odoo server will stop.

To keep Odoo running continuously in the background on your development machine:

### Using `nohup`:
```bash
nohup python3 odoo19/odoo-bin --addons-path=odoo19/addons,custom_repo -d odoo19_teste --http-port=8070 > odoo19.log 2>&1 &
```

### Or using `tmux` / `screen`:
```bash
tmux new -s odoo19
python3 odoo19/odoo-bin --addons-path=odoo19/addons,custom_repo -d odoo19_teste --http-port=8070
# Press Ctrl+B then D to detach and leave it running
```

---

## 📁 Module File Structure

```text
db_license_manage/
├── __init__.py
├── __manifest__.py
├── README.md
├── controllers/
│   ├── __init__.py
│   ├── main.py              # Login interceptor & /license/expired handler
│   └── systray.py           # Owl 2 JSON-RPC systray status endpoint
├── data/
│   ├── ir_cron_data.xml     # Daily automated expiration check cron
│   └── mail_template_data.xml# License expiration warning email template
├── i18n/
│   ├── db_license_manage.pot# Master translation template
│   ├── en.po                # English
│   ├── fr.po                # French
│   ├── pt.po                # Portuguese (Portugal)
│   ├── pt_BR.po             # Portuguese (Brazil)
│   └── es.po                # Spanish
├── models/
│   ├── __init__.py
│   ├── ir_http.py           # Real-time non-admin session enforcement
│   ├── license_notification.py# Automated email dispatch logic
│   └── res_config.py        # Settings view & session cookie configuration
├── static/
│   ├── description/         # Store banner, screenshots & index.html
│   └── src/
│       ├── css/login.css
│       ├── js/systray_license.js
│       └── xml/systray_license.xml
├── tools/
│   └── setup_license_tools.py# RSA key initialization & generator setup
└── utils/
    ├── __init__.py
    └── license_verifier.py  # RS256 token verification & UUID validation
```
