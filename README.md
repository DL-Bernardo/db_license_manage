# Odoo Database License Manager (v17)

O **Database License Manager** é um módulo de segurança avançado para Odoo 17, desenhado para proteger a propriedade intelectual e controlar o período de utilização do software.

Diferente de soluções simples baseadas em datas de texto, este módulo utiliza **Criptografia Assimétrica (RSA) e JWT (JSON Web Tokens)** para garantir que a licença não possa ser falsificada, alterada ou clonada para outras bases de dados.

## 🚀 Funcionalidades Principais

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

---

## 🛠️ Pré-requisitos Técnicos

Este módulo depende de bibliotecas Python de criptografia padrão. Certifique-se de que estão instaladas no ambiente do servidor Odoo:

```bash
pip install pyjwt cryptography
```

---

## ⚙️ Instalação e Configuração (Cliente)

### 1. Instalação
1.  Coloque a pasta `db_license_manager` no diretório de `custom_addons`.
2.  Atualize a lista de aplicações e instale o módulo.
    *   *Nota:* O módulo instalará automaticamente as dependências `web`, `website`, `auth_signup` e `mail` se necessário.

### 2. Configuração Inicial (Obrigatório)
Assim que o módulo for instalado, **nenhum usuário conseguirá logar** (exceto Admin) até que a Chave Pública seja configurada.

1.  Aceda com conta de Administrador.
2.  Vá para **Definições (Settings) > Licenciamento**.
3.  No campo **"Chave Pública RSA"**, cole o conteúdo do seu ficheiro `public_key.pem`.
4.  Salve as definições.

### 3. Inserir a Licença
1.  Ainda em **Definições > Licenciamento**.
2.  No campo **"Token de Licença"**, cole a string fornecida pelo seu fornecedor de software.
3.  O sistema validará imediatamente a assinatura e mostrará:
    *   Estado da Licença (Badge Colorido)
    *   Data de Início (Válido de...)
    *   Data de Fim (...até)

---

## 🔐 Guia do Desenvolvedor (Fornecedor)

### 1. Geração das Chaves RSA
Antes de distribuir o módulo, você deve gerar um par de chaves RSA. Guarde a **Chave Privada** em segurança e nunca a partilhe. A **Chave Pública** será configurada no Odoo do cliente.

No terminal (Linux/Mac/WSL):

```bash
# Gerar Chave Privada
openssl genrsa -out private_key.pem 2048

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