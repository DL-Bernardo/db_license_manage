# Odoo Database License Manager (v17)

The **Database License Manager** is an advanced security module for Odoo 17, designed to protect intellectual property and control the software's usage period.

Unlike simple solutions based on text dates, this module uses **Asymmetric Cryptography (RSA) and JWT (JSON Web Tokens)** to ensure that the license cannot be forged, altered, or cloned for other databases.

## 🚀 Key Features

### 🔒 Security and Control
*   **Expiration Date Lock:** Prevents users from logging in after the defined expiration date.
*   **UUID Binding (Anti-Copy):** The license is generated specifically for the client's database UUID. If the database is restored on another server, the license automatically becomes invalid.
*   **RSA 2048-bit Security:** Uses a private key (held by the provider) to sign licenses and a public key (configured in the module) for validation.
*   **Admin Bypass (Fail-Safe):** Administrators (ID 1, ID 2, and Superusers) maintain access to the system even with an expired license, allowing token renewal via the interface.

### ⚠️ Warning and Notification System (New)
*   **Login Warning (Grace Period):** 5 days before expiration, users see a warning banner on the login screen.
    *   Login is **not blocked** during this period.
    *   A **"Continue to System"** button allows normal access.
    *   "Premium" look with gradients (Orange for warning, Red for critical).
*   **Persistent Notification (Systray):** An alert icon at the top of the screen (backend) displays a countdown of the remaining days.
*   **Automatic Emails:** The system sends automatic emails to administrators when the license is about to expire.
    *   **Schedule:** 15, 7, 5, 3, 1, and 0 days before expiration.
    *   **Template:** Formatted HTML email with alert colors.

### ⚙️ Management Interface
*   **Dynamic Configuration:** The public key and token are configured directly in *Settings > Licensing*.
*   **Visual Status:** Colored badges (Valid, Warning, Expired) for easy identification of the license status.
*   **Real-time Validation:** When pasting the token, the system immediately displays the validity dates.

---

## 🛠️ Technical Prerequisites

This module depends on standard Python cryptography libraries. Make sure they are installed in the Odoo server environment:

```bash
pip install pyjwt cryptography
```

---

## ⚙️ Installation and Configuration (Client)

### 1. Installation
1.  Place the `db_license_manager` folder in the `custom_addons` directory.
2.  Update the applications list and install the module.
    *   *Note:* The module will automatically install the `web`, `website`, `auth_signup`, and `mail` dependencies if necessary.

### 2. Initial Configuration (Required)
As soon as the module is installed, **no user will be able to log in** (except Admin) until the Public Key is configured.

1.  Log in with an Administrator account.
2.  Go to **Settings > Licensing**.
3.  In the **"RSA Public Key"** field, paste the content of your `public_key.pem` file.
4.  Save the settings.

### 3. Insert the License
1.  Still in **Settings > Licensing**.
2.  In the **"License Token"** field, paste the string provided by your software provider.
3.  The system will immediately validate the signature and show:
    *   License Status (Colored Badge)
    *   Start Date (Valid from...)
    *   End Date (...to)

---

## 🔐 Developer Guide (Provider)

### 1. Generating RSA Keys
Before distributing the module, you must generate an RSA key pair. Keep the **Private Key** safe and never share it. The **Public Key** will be configured in the client's Odoo.

In the terminal (Linux/Mac/WSL):

```bash
# Generate Private Key
openssl genrsa -out private_key.pem 2048

# Generate Public Key (Extracted from Private)
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

### 2. Generate a License for a Client
Use the Python script below (run it locally on your machine) to create the token you will send to the client. **Do not include this script in the client's module.**

**`generate_license.py` script:**

```python
import jwt
import datetime

# PASTE YOUR PRIVATE KEY HERE
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
...content of private_key.pem...
-----END RSA PRIVATE KEY-----"""

def create_token(client_name, db_uuid, days):
    now = datetime.datetime.now()
    payload = {
        'iss': 'OdooVendor',
        'sub': client_name,
        'uuid': db_uuid,  # UUID obtained in Settings > Technical > System Parameters
        'exp': now + datetime.timedelta(days=days), # Expiration Date
        'iat': now # Issue Date (Start)
    }
    # Optional: Add 'verify_iat': False in the decode if there are timezone issues
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

# Example of use:
# 1. Ask the client for their database UUID.
# 2. Generate the token:
token = create_token("Example Client Ltd", "client-database-uuid", 365)
print(token)
```

### 3. Sending to the Client
Send the client:
1.  The `db_license_manage` module.
2.  The content of the `public_key.pem` file (only once, on installation).
3.  The generated `token` (whenever the license is renewed).

---

## 🛡️ Security Flow

1.  **Login Attempt:** The user enters their credentials.
2.  **User Verification:** Odoo validates the password.
3.  **Interception:** The module checks if the user is an Admin.
    *   **If YES:** Access granted.
    *   **If NO:** The module reads the License Token and the Public Key from the system.
4.  **Token Validation:**
    *   Is the RSA signature valid?
    *   Does the UUID match?
    *   **WARNING Status (<= 5 days):** Displays a warning on the login screen, but allows continuing.
    *   **EXPIRED/INVALID Status:** Blocks login and displays an error.
5.  **Notifications:**
    *   Daily cron job checks the validity and sends emails to the `base.group_system` group.

---

## ⚠️ Troubleshooting

*   **The client restored a backup and was blocked:**
    When restoring a backup on a new instance, the database UUID changes. The client must request a new license by providing the new UUID.

*   **I can't log in to renew the license:**
    Log in with the original Administrator account (usually `admin` or ID 2). These accounts are immune to the block.

*   **Error "Uncaught Promise > license_token field is undefined":**
    Make sure to restart the Odoo server after updating the module. This error occurs when there is a desynchronization between the Python model and the JS View.

*   **Emails are not arriving:**
    Check if the outgoing mail server (SMTP) is configured in *Settings > Technical > Email Servers*. Also, check if the "License Manager: Check Expiration" Scheduled Action is active.

---

**Developed by:** [DIGITALUB - ANGOLA]
**License:** OPL-1 (Digitalub Proprietary License)
