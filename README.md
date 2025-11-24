# Odoo Database License Manager (v17)

O **Database License Manager** é um módulo de segurança para Odoo 17 desenhado para proteger a propriedade intelectual e controlar o período de utilização do software. 

Diferente de soluções simples baseadas em datas de texto simples, este módulo utiliza **Criptografia Assimétrica (RSA) e JWT (JSON Web Tokens)** para garantir que a licença não possa ser falsificada, alterada ou clonada para outras bases de dados.

## 🚀 Funcionalidades Principais.

*   **Bloqueio por Data de Validade:** Impede o login de utilizadores após a data de expiração definida.
*   **Vínculo com UUID (Anti-Cópia):** A licença é gerada especificamente para o UUID da base de dados do cliente. Se a base for restaurada noutro servidor, a licença torna-se inválida automaticamente.
*   **Segurança RSA 2048-bit:** Utiliza uma chave privada (na posse do fornecedor) para assinar licenças e uma chave pública (no módulo) para validação.
*   **Admin Bypass (Fail-Safe):** Administradores (ID 1, ID 2 e Superusers) mantêm acesso ao sistema mesmo com a licença expirada, permitindo a renovação do token via interface.
*   **Período de Graça (Grace Period):** Sistema preparado para emitir avisos visuais (Warnings) 15 dias antes da expiração.

---

## 🛠️ Pré-requisitos Técnicos

Este módulo depende de bibliotecas Python de criptografia padrão. Certifique-se de que estão instaladas no ambiente do servidor Odoo:

**bash
**pip install pyjwt cryptography

⚙️ Instalação e Configuração (Cliente)
Instalação:
Coloque a pasta db_license_manager no diretório de custom_addons.
Atualize a lista de aplicações e instale o módulo.
Inserir a Licença:
Aceda a Definições (Settings) > Licenciamento.
No campo "Token de Licença", cole a string fornecida pelo seu fornecedor de software.
O sistema validará imediatamente a assinatura e mostrará a data de validade.

🔐 Guia do Desenvolvedor (Fornecedor)
1. Geração das Chaves RSA
Antes de distribuir o módulo, você deve gerar um par de chaves RSA. Guarde a Chave Privada em segurança e nunca a partilhe.
No terminal (Linux/Mac):

# Gerar Chave Privada
openssl genrsa -out private_key.pem 2048

# Gerar Chave Pública (Extraída da Privada)
openssl rsa -in private_key.pem -pubout -out public_key.pem


Aqui está um README.md profissional e estruturado, pronto para ser incluído na raiz do teu repositório. Ele cobre a instalação, o funcionamento, a segurança e o guia de uso para o administrador.
code
Markdown
# Odoo Database License Manager (v17)

O **Database License Manager** é um módulo de segurança para Odoo 17 desenhado para proteger a propriedade intelectual e controlar o período de utilização do software. 

Diferente de soluções simples baseadas em datas de texto simples, este módulo utiliza **Criptografia Assimétrica (RSA) e JWT (JSON Web Tokens)** para garantir que a licença não possa ser falsificada, alterada ou clonada para outras bases de dados.

## 🚀 Funcionalidades Principais

*   **Bloqueio por Data de Validade:** Impede o login de utilizadores após a data de expiração definida.
*   **Vínculo com UUID (Anti-Cópia):** A licença é gerada especificamente para o UUID da base de dados do cliente. Se a base for restaurada noutro servidor, a licença torna-se inválida automaticamente.
*   **Segurança RSA 2048-bit:** Utiliza uma chave privada (na posse do fornecedor) para assinar licenças e uma chave pública (no módulo) para validação.
*   **Admin Bypass (Fail-Safe):** Administradores (ID 1, ID 2 e Superusers) mantêm acesso ao sistema mesmo com a licença expirada, permitindo a renovação do token via interface.
*   **Período de Graça (Grace Period):** Sistema preparado para emitir avisos visuais (Warnings) 15 dias antes da expiração.

---

## 🛠️ Pré-requisitos Técnicos

Este módulo depende de bibliotecas Python de criptografia padrão. Certifique-se de que estão instaladas no ambiente do servidor Odoo:

*bash
*pip install pyjwt cryptography

⚙️ Instalação e Configuração (Cliente)
Instalação:
Coloque a pasta db_license_manager no diretório de custom_addons.
Atualize a lista de aplicações e instale o módulo.
Inserir a Licença:
Aceda a Definições (Settings) > Licenciamento.
No campo "Token de Licença", cole a string fornecida pelo seu fornecedor de software.
O sistema validará imediatamente a assinatura e mostrará a data de validade.

🔐 Guia do Desenvolvedor (Fornecedor)
1. Geração das Chaves RSA
Antes de distribuir o módulo, você deve gerar um par de chaves RSA. Guarde a Chave Privada em segurança e nunca a partilhe.
No terminal (Linux/Mac):
code
Bash
# Gerar Chave Privada
openssl genrsa -out private_key.pem 2048

# Gerar Chave Pública (Extraída da Privada)
openssl rsa -in private_key.pem -pubout -out public_key.pem
2. Configurar o Módulo
Abra o ficheiro utils/license_verifier.py no módulo e substitua a variável PUBLIC_KEY pelo conteúdo do seu ficheiro public_key.pem.
3. Gerar uma Licença para um Cliente
Utilize o script Python abaixo (execute localmente na sua máquina) para criar o token que enviará ao cliente. Não inclua este script no módulo do cliente.
Script generate_license.py:

import jwt
import datetime

# COLE A SUA CHAVE PRIVADA AQUI
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
...conteúdo do private_key.pem...
-----END RSA PRIVATE KEY-----"""

def create_token(client_name, db_uuid, days):
    payload = {
        'iss': 'OdooVendor',
        'sub': client_name,
        'uuid': db_uuid,  # UUID obtido em Configurações > Técnico > Parâmetros de Sistema
        'exp': datetime.datetime.now() + datetime.timedelta(days=days),
        'iat': datetime.datetime.now()
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

# Exemplo de uso:
token = create_token("Cliente Exemplo Lda", "uuid-da-base-de-dados-cliente", 365)
print(token)

🛡️ Fluxo de Segurança

Tentativa de Login: O utilizador insere as credenciais.
Verificação de Utilizador: O Odoo valida a senha.
Interceptação: O módulo verifica se o utilizador é Admin.
Se SIM: Acesso permitido.
Se NÃO: O módulo lê o Token de Licença.
Validação do Token:
A assinatura RSA é válida?
A data atual é menor que a data de expiração?
O UUID do token corresponde ao UUID da base de dados atual?
Resultado: Se qualquer verificação falhar, o utilizador é desconectado forçadamente e uma mensagem de erro é exibida.

⚠️ Resolução de Problemas
O cliente restaurou um backup e foi bloqueado:
Ao restaurar um backup numa nova instância, o UUID da base de dados muda (ou deve mudar). Como o token está vinculado ao UUID antigo, o bloqueio é acionado. O cliente deve solicitar uma nova licença fornecendo o novo UUID.
Não consigo entrar para renovar a licença:
Aceda com a conta de Administrador original (geralmente admin ou ID 2). Estas contas têm imunidade ao bloqueio para permitir a manutenção do sistema.

Desenvolvido por: [DIGITALUB - ANGOLA]
Licença: OPL-1 (Digitalub Proprietary License)