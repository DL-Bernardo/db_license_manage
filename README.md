# Odoo Database License Manager (v17)

O **Database License Manager** é um módulo de segurança para Odoo 17 desenhado para proteger a propriedade intelectual e controlar o período de utilização do software.

Diferente de soluções simples baseadas em datas de texto simples, este módulo utiliza **Criptografia Assimétrica (RSA) e JWT (JSON Web Tokens)** para garantir que a licença não possa ser falsificada, alterada ou clonada para outras bases de dados.

## 🚀 Funcionalidades Principais

*   **Bloqueio por Data de Validade:** Impede o login de utilizadores após a data de expiração definida.
*   **Vínculo com UUID (Anti-Cópia):** A licença é gerada especificamente para o UUID da base de dados do cliente. Se a base for restaurada noutro servidor, a licença torna-se inválida automaticamente.
*   **Segurança RSA 2048-bit:** Utiliza uma chave privada (na posse do fornecedor) para assinar licenças e uma chave pública (configurada no módulo) para validação.
*   **Configuração Dinâmica:** A chave pública é configurada diretamente na interface do Odoo, sem necessidade de alterar código.
*   **Visualização Completa:** Exibe a data de início (emissão) e fim (validade) da licença.
*   **Admin Bypass (Fail-Safe):** Administradores (ID 1, ID 2 e Superusers) mantêm acesso ao sistema mesmo com a licença expirada, permitindo a renovação do token via interface.
*   **Período de Graça (Grace Period):** Sistema preparado para emitir avisos visuais (Warnings) 15 dias antes da expiração.

---

## 🛠️ Pré-requisitos Técnicos

Este módulo depende de bibliotecas Python de criptografia padrão. Certifique-se de que estão instaladas no ambiente do servidor Odoo:

```bash
pip install pyjwt cryptography
```

## ⚙️ Instalação e Configuração (Cliente)

### 1. Instalação
1.  Coloque a pasta `db_license_manager` no diretório de `custom_addons`.
2.  Atualize a lista de aplicações e instale o módulo.

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
    *   Estado da Licença (Válido/Inválido/Expirado)
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
    *   A assinatura RSA é válida com a chave pública configurada?
    *   A data atual é menor que a data de expiração?
    *   O UUID do token corresponde ao UUID da base de dados atual?
5.  **Resultado:** Se qualquer verificação falhar, o utilizador é desconectado forçadamente e uma mensagem de erro é exibida.

---

## ⚠️ Resolução de Problemas

*   **O cliente restaurou um backup e foi bloqueado:**
    Ao restaurar um backup numa nova instância, o UUID da base de dados muda. O cliente deve solicitar uma nova licença fornecendo o novo UUID.

*   **Não consigo entrar para renovar a licença:**
    Aceda com a conta de Administrador original (geralmente `admin` ou ID 2). Estas contas têm imunidade ao bloqueio para permitir a manutenção do sistema.

*   **Erro "Chave Pública não configurada":**
    O administrador deve logar e configurar a chave pública em *Definições > Licenciamento*.

---

**Desenvolvido por:** [DIGITALUB - ANGOLA]
**Licença:** OPL-1 (Digitalub Proprietary License)