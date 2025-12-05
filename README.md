# Odoo Database License Manager (v17)

<<<<<<< HEAD
The **Database License Manager** is an advanced security module for Odoo 17, designed to protect intellectual property and control the software's usage period.

Unlike simple solutions based on text dates, this module uses **Asymmetric Cryptography (RSA) and JWT (JSON Web Tokens)** to ensure that the license cannot be forged, altered, or cloned for other databases.
=======
O **Database License Manager** é um módulo de segurança avançado para Odoo 17, desenhado para proteger a propriedade intelectual e controlar o período de utilização do software.

Diferente de soluções simples baseadas em datas de texto, este módulo utiliza **Criptografia Assimétrica (RSA) e JWT (JSON Web Tokens)** para garantir que a licença não possa ser falsificada, alterada ou clonada para outras bases de dados.
>>>>>>> e3d7358826008ff0f97c0789d2aac03e9fadd3f4

## 🚀 Key Features

<<<<<<< HEAD
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
=======
### 🔒 Segurança e Controle
*   **Bloqueio por Data de Validade:** Impede o login de utilizadores após a data de expiração definida.
*   **Vínculo com UUID (Anti-Cópia):** A licença é gerada especificamente para o UUID da base de dados do cliente. Se a base for restaurada noutro servidor, a licença torna-se inválida automaticamente.
*   **Segurança RSA 2048-bit:** Utiliza uma chave privada (na posse do fornecedor) para assinar licenças e uma chave pública (configurada no módulo) para validação.
*   **Admin Bypass (Fail-Safe):** Administradores (ID 1, ID 2 e Superusers) mantêm acesso ao sistema mesmo com a licença expirada, permitindo a renovação do token via interface.

### ⚠️ Sistema de Avisos e Notificações (Novo)
*   **Aviso de Login (Grace Period):** 5 dias antes da expiração, os utilizadores veem um banner de aviso na tela de login.
    *   O login **não é bloqueado** durante este período.
    *   Um botão **"Continuar para o Sistema"** permite o acesso normal.
    *   Visual "Premium" com gradientes (Laranja para aviso, Vermelho para crítico).
*   **Notificação Persistente (Systray):** Um ícone de alerta no topo da tela (backend) exibe a contagem regressiva de dias restantes.
*   **E-mails Automáticos:** O sistema envia e-mails automáticos para os administradores quando a licença está prestes a expirar.
    *   **Cronograma:** 15, 7, 5, 3, 1 e 0 dias antes da expiração.
    *   **Template:** E-mail HTML formatado com cores de alerta.

### ⚙️ Interface de Gestão
*   **Configuração Dinâmica:** A chave pública e o token são configurados diretamente em *Definições > Licenciamento*.
*   **Status Visual:** Badges coloridos (Válido, Aviso, Expirado) para fácil identificação do estado da licença.
*   **Validação em Tempo Real:** Ao colar o token, o sistema exibe imediatamente as datas de validade.
>>>>>>> e3d7358826008ff0f97c0789d2aac03e9fadd3f4

---

## 🛠️ Technical Prerequisites

This module depends on standard Python cryptography libraries. Make sure they are installed in the Odoo server environment:

```bash
pip install pyjwt cryptography
```

---
<<<<<<< HEAD

## ⚙️ Installation and Configuration (Client)
=======

## ⚙️ Instalação e Configuração (Cliente)

### 1. Instalação
1.  Coloque a pasta `db_license_manager` no diretório de `custom_addons`.
2.  Atualize a lista de aplicações e instale o módulo.
    *   *Nota:* O módulo instalará automaticamente as dependências `web`, `website`, `auth_signup` e `mail` se necessário.
>>>>>>> e3d7358826008ff0f97c0789d2aac03e9fadd3f4

### 1. Installation
1.  Place the `db_license_manager` folder in the `custom_addons` directory.
2.  Update the applications list and install the module.
    *   *Note:* The module will automatically install the `web`, `website`, `auth_signup`, and `mail` dependencies if necessary.

### 2. Initial Configuration (Required)
As soon as the module is installed, **no user will be able to log in** (except Admin) until the Public Key is configured.

<<<<<<< HEAD
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
=======
### 3. Inserir a Licença
1.  Ainda em **Definições > Licenciamento**.
2.  No campo **"Token de Licença"**, cole a string fornecida pelo seu fornecedor de software.
3.  O sistema validará imediatamente a assinatura e mostrará:
    *   Estado da Licença (Badge Colorido)
    *   Data de Início (Válido de...)
    *   Data de Fim (...até)
>>>>>>> e3d7358826008ff0f97c0789d2aac03e9fadd3f4

---

## ⚠️ Troubleshooting

*   **The client restored a backup and was blocked:**
    When restoring a backup on a new instance, the database UUID changes. The client must request a new license by providing the new UUID.

*   **I can't log in to renew the license:**
    Log in with the original Administrator account (usually `admin` or ID 2). These accounts are immune to the block.

*   **Error "Uncaught Promise > license_token field is undefined":**
    Make sure to restart the Odoo server after updating the module. This error occurs when there is a desynchronization between the Python model and the JS View.

<<<<<<< HEAD
*   **Emails are not arriving:**
    Check if the outgoing mail server (SMTP) is configured in *Settings > Technical > Email Servers*. Also, check if the "License Manager: Check Expiration" Scheduled Action is active.

---

**Developed by:** [DIGITALUB - ANGOLA]
**License:** OPL-1 (Digitalub Proprietary License)
=======
# Gerar Chave Pública (Extraída da Privada)
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

### 2. Gerar uma Licença para um Cliente
Utilize o script Python abaixo (execute localmente na sua máquina) para criar o token que enviará ao cliente. **Não inclua este script no módulo do cliente.**

**Script `generate_license.py`:**

```python
import jwt
import datetime

# COLE A SUA CHAVE PRIVADA AQUI
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
...conteúdo do private_key.pem...
-----END RSA PRIVATE KEY-----"""

def create_token(client_name, db_uuid, days):
    now = datetime.datetime.now()
    payload = {
        'iss': 'OdooVendor',
        'sub': client_name,
        'uuid': db_uuid,  # UUID obtido em Configurações > Técnico > Parâmetros de Sistema
        'exp': now + datetime.timedelta(days=days), # Data de Expiração
        'iat': now # Data de Emissão (Início)
    }
    # Opcional: Adicionar 'verify_iat': False no decode se houver problemas de fuso horário
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

# Exemplo de uso:
# 1. Peça ao cliente o UUID da base de dados dele.
# 2. Gere o token:
token = create_token("Cliente Exemplo Lda", "uuid-da-base-de-dados-cliente", 365)
print(token)
```

### 3. Envio ao Cliente
Envie ao cliente:
1.  O módulo `db_license_manage`.
2.  O conteúdo do ficheiro `public_key.pem` (apenas uma vez, na instalação).
3.  O `token` gerado (sempre que renovar a licença).

---

## 🛡️ Fluxo de Segurança

1.  **Tentativa de Login:** O utilizador insere as credenciais.
2.  **Verificação de Utilizador:** O Odoo valida a senha.
3.  **Interceptação:** O módulo verifica se o utilizador é Admin.
    *   **Se SIM:** Acesso permitido.
    *   **Se NÃO:** O módulo lê o Token de Licença e a Chave Pública do sistema.
4.  **Validação do Token:**
    *   A assinatura RSA é válida?
    *   O UUID corresponde?
    *   **Status WARNING (<= 5 dias):** Exibe aviso na tela de login, mas permite continuar.
    *   **Status EXPIRED/INVALID:** Bloqueia o login e exibe erro.
5.  **Notificações:**
    *   Cron job diário verifica a validade e envia e-mails para o grupo `base.group_system`.

---

## ⚠️ Resolução de Problemas

*   **O cliente restaurou um backup e foi bloqueado:**
    Ao restaurar um backup numa nova instância, o UUID da base de dados muda. O cliente deve solicitar uma nova licença fornecendo o novo UUID.

*   **Não consigo entrar para renovar a licença:**
    Aceda com a conta de Administrador original (geralmente `admin` ou ID 2). Estas contas têm imunidade ao bloqueio.

*   **Erro "Uncaught Promise > license_token field is undefined":**
    Certifique-se de reiniciar o servidor Odoo após atualizar o módulo. Este erro ocorre quando há dessincronização entre o modelo Python e a View JS.

*   **E-mails não chegam:**
    Verifique se o servidor de saída (SMTP) está configurado em *Definições > Técnico > Servidores de E-mail*. Verifique também se a Ação Agendada "License Manager: Check Expiration" está ativa.

---

**Desenvolvido por:** [DIGITALUB - ANGOLA]
**Licença:** OPL-1 (Digitalub Proprietary License)
>>>>>>> e3d7358826008ff0f97c0789d2aac03e9fadd3f4
