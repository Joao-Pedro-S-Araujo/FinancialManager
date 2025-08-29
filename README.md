# Financial Manager

Este é um gerenciador financeiro simples desenvolvido em Python com a interface gráfica Tkinter e banco de dados MySQL.

## Funcionalidades

- Cadastro e Login de usuários
- Depósito e Saque de valores
- Visualização de histórico de transações

## Pré-requisitos

- Python 3.x
- MySQL Server

## Instalação e Configuração

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/Joao-Pedro-S-Araujo/FinancialManager.git
    cd seu-repositorio
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o banco de dados:**
    - Crie um banco de dados no MySQL chamado `financialmanager`.
    - Copie o arquivo `.env.example` para um novo arquivo chamado `.env`:
      ```bash
      cp .env.example .env
      ```
    - Abra o arquivo `.env` e preencha com as suas credenciais do MySQL.

5.  **Execute a aplicação:**
    ```bash
    python app.py
    ```
