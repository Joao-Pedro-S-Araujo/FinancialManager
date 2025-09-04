# FinancialManager v1.0

![Status do Projeto](https://img.shields.io/badge/status-concluído-brightgreen)
![Linguagem](https://img.shields.io/badge/python-3.11-blue)
![Interface](https://img.shields.io/badge/gui-tkinter-orange)
![Base de Dados](https://img.shields.io/badge/database-sqlite-purple)

FinancialManager é uma aplicação de desktop completa para gestão financeira pessoal, desenvolvida do zero em Python com a interface gráfica Tkinter. O sistema permite aos utilizadores controlar as suas finanças de forma segura e intuitiva, desde o registo de transações até à análise de gastos com orçamentos mensais.

## 📷 Demonstração

<img width="1227" height="897" alt="image" src="https://github.com/user-attachments/assets/9afb6064-e478-45b8-b656-8c6bc7b2eeb3" />


*Uma demonstração visual do Dashboard principal, mostrando o resumo mensal, o saldo e as últimas transações.*

---

## ✨ Funcionalidades Principais

-   **🔐 Autenticação Segura:** Sistema completo de login e registo com hashing de senhas (SHA-256) para garantir a segurança das credenciais.
-   **📊 Dashboard Dinâmico:** Uma tela principal que oferece um resumo instantâneo da saúde financeira do utilizador, incluindo saldo, entradas/saídas do mês, e progresso dos orçamentos.
-   **💸 Gestão de Transações:** Registo de depósitos e saques com um sistema de categorização personalizável.
-   **🔁 Transferências entre Contas:** Funcionalidade para transferir valores entre utilizadores registados no sistema.
-   **✏️ Controle Total:** Capacidade de editar e excluir transações diretamente do histórico, com ajuste automático e seguro do saldo (utilizando transações atómicas).
-   **📈 Relatórios e Análise:**
    -   Histórico de transações completo com filtros por intervalo de datas.
    -   Relatórios visuais com gráficos de barras (gerados com Matplotlib) para uma análise clara das despesas por categoria, também com suporte a filtros de data.

---

## 🛠️ Stack de Tecnologias

-   **Linguagem Principal:** Python 3
-   **Interface Gráfica (GUI):** Tkinter (com `ttk` para widgets modernos)
-   **Base de Dados:** SQLite 3 (para a versão distribuível e portátil)
-   **Visualização de Dados:** Matplotlib
-   **Componentes de UI Adicionais:** tkcalendar
-   **Empacotamento:** PyInstaller

---

## 🚀 Como Executar o Projeto

Existem duas maneiras de executar a aplicação:

### 1. A Partir do Executável (Recomendado para Utilizadores)
A forma mais fácil de testar a aplicação.

1.  Vá à secção de [**Releases**](https://github.com/seu-utilizador/seu-repositorio/releases) deste repositório.
2.  Descarregue o ficheiro `FinancialManager_v1.0.zip`.
3.  Extraia o conteúdo e execute o ficheiro `app.exe`.

*(Nota: Lembre-se de substituir `seu-utilizador/seu-repositorio` pelo seu link real do GitHub)*

### 2. A Partir do Código-Fonte (Para Desenvolvedores)

**Pré-requisitos:**
-   Python 3.8+

**Passos:**

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/seu-utilizador/seu-repositorio.git](https://github.com/seu-utilizador/seu-repositorio.git)
    cd seu-repositorio
    ```
2.  Crie e ative um ambiente virtual:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Execute a aplicação:
    ```bash
    python app.py
    ```

---

## 📜 Licença

Este projeto está licenciado sob a Licença MIT. Veja o ficheiro [LICENSE](LICENSE) para mais detalhes.
