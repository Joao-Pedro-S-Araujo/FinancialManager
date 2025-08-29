import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from datetime import datetime
import db_manager

# --- Configurações de Estilo ---
COR_PRINCIPAL = "#1e1e2f"
COR_SECUNDARIA = "#2e2e3f"
COR_BOTAO = "#00b894"
COR_TEXTO = "#ffffff"
FONTE = ("Segoe UI", 12)
FONTE_TITULO = ("Segoe UI", 20, "bold")
FONTE_SALDO = ("Segoe UI", 16, "bold")

# --- Variáveis Globais de Estado ---

usuario_logado = None  # Armazenará os dados do usuário logado

# --- Funções de Autenticação e Usuário ---

def hash_senha(senha):
    """Gera um hash SHA-256 para a senha."""
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def cadastrar_usuario():
    """Registra um novo usuário no banco de dados."""
    email = entry_email_cadastro.get().strip()
    senha = entry_senha_cadastro.get().strip()
    
    if not email or not senha:
        messagebox.showerror("Erro", "Preencha todos os campos.")
        return
        
    # Verifica se o usuário já existe no banco
    if db_manager.buscar_usuario_por_email(email):
        messagebox.showwarning("Erro", "Este email já está cadastrado.")
        return

    senha_hashed = hash_senha(senha)
    
    if db_manager.adicionar_usuario(email, senha_hashed):
        messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso! Faça o login.")
        mostrar_frame(frame_login)
    else:
        messagebox.showerror("Erro de Banco de Dados", "Não foi possível realizar o cadastro. Tente novamente mais tarde.")

def fazer_login():
    """Valida as credenciais do usuário consultando o banco de dados."""
    global usuario_logado
    email = entry_email_login.get().strip()
    senha = entry_senha_login.get().strip()

    if not email or not senha:
        messagebox.showerror("Erro de Login", "Preencha todos os campos.")
        return

    senha_hashed = hash_senha(senha)
    
    user = db_manager.buscar_usuario_por_email(email)
    
    if user and user['senha_hash'] == senha_hashed:
        usuario_logado = user
        iniciar_sessao_app()
    else:
        messagebox.showerror("Erro de Login", "Email ou senha incorretos.")

# Iniciar sessão:

def iniciar_sessao_app():
    """Prepara e exibe a tela principal da aplicação para o usuário logado."""
    label_bem_vindo.config(text=f"Bem-vindo(a), {usuario_logado['email']}")
    atualizar_saldo_display()
    mostrar_frame(frame_principal)

def fazer_logout():
    global usuario_logado
    usuario_logado = None

# --- Funções Financeiras  ---

def atualizar_saldo_display():
    """Atualiza o label do saldo consultando o banco de dados."""
    user_id = usuario_logado['id']
    saldo_atual = db_manager.obter_saldo(user_id)
    label_saldo.config(text=f"R$ {saldo_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

def depositar():
    user_id = usuario_logado['id']
    try:
        valor = float(entrada_valor.get().replace(",", "."))
        if valor <= 0:
            messagebox.showerror("Erro", "O valor do depósito deve ser positivo.")
            return
        
        if db_manager.registrar_transacao(user_id, 'deposito', valor):
            atualizar_saldo_display()
            messagebox.showinfo("Sucesso", f"Depósito de R$ {valor:,.2f} realizado.".replace(",", "X").replace(".", ",").replace("X", "."))
            entrada_valor.delete(0, tk.END)
        else:
            messagebox.showerror("Erro de Banco de Dados", "Não foi possível registrar o depósito.")

    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")

def sacar():
    user_id = usuario_logado['id']
    saldo_atual = db_manager.obter_saldo(user_id)
    
    try:
        valor = float(entrada_valor.get().replace(",", "."))
        if valor <= 0:
            messagebox.showerror("Erro", "O valor do saque deve ser positivo.")
        elif valor > saldo_atual:
            messagebox.showwarning("Saldo Insuficiente", "Você não tem saldo suficiente para este saque.")
        else:
            if db_manager.registrar_transacao(user_id, 'saque', valor):
                atualizar_saldo_display()
                messagebox.showinfo("Sucesso", f"Saque de R$ {valor:,.2f} realizado.".replace(",", "X").replace(".", ",").replace("X", "."))
                entrada_valor.delete(0, tk.END)
            else:
                messagebox.showerror("Erro de Banco de Dados", "Não foi possível registrar o saque.")
    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")


def fazer_login():
    """Valida as credenciais do usuário consultando o banco de dados."""
    global usuario_logado
    email = entry_email_login.get().strip()
    senha = entry_senha_login.get().strip()

    if not email or not senha:
        messagebox.showerror("Erro de Login", "Preencha todos os campos.")
        return

    senha_hashed = hash_senha(senha)
    
    user = db_manager.buscar_usuario_por_email(email)
    
    if user and user['senha_hash'] == senha_hashed:
        usuario_logado = user
        iniciar_sessao_app()
    else:
        messagebox.showerror("Erro de Login", "Email ou senha incorretos.")

def iniciar_sessao_app():
    """Prepara e exibe a tela principal da aplicação para o usuário logado."""
    label_bem_vindo.config(text=f"Bem-vindo(a), {usuario_logado['email']}")
    atualizar_saldo_display()
    mostrar_frame(frame_principal)
    messagebox.showerror("Erro de Login", "Email ou senha incorretos.")

def iniciar_sessao_app():
    """Prepara e exibe a tela principal da aplicação para o usuário logado."""
    label_bem_vindo.config(text=f"Bem-vindo(a), {usuario_logado['email']}")
    atualizar_saldo_display()
    mostrar_frame(frame_principal)

def fazer_logout():
    """Encerra a sessão do usuário e retorna para a tela de login."""
    global usuario_logado
    usuario_logado = None
    entry_email_login.delete(0, tk.END)
    entry_senha_login.delete(0, tk.END)
    mostrar_frame(frame_login)

# --- Funções Financeiras ---

def atualizar_saldo_display():
    """Atualiza o label do saldo consultando o banco de dados."""
    user_id = usuario_logado['id']
    saldo_atual = db_manager.obter_saldo(user_id)
    label_saldo.config(text=f"R$ {saldo_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

def depositar():
    user_id = usuario_logado['id']
    try:
        valor = float(entrada_valor.get().replace(",", "."))
        if valor <= 0:
            messagebox.showerror("Erro", "O valor do depósito deve ser positivo.")
            return
        
        if db_manager.registrar_transacao(user_id, 'deposito', valor):
            atualizar_saldo_display()
            messagebox.showinfo("Sucesso", f"Depósito de R$ {valor:,.2f} realizado.".replace(",", "X").replace(".", ",").replace("X", "."))
            entrada_valor.delete(0, tk.END)
        else:
            messagebox.showerror("Erro de Banco de Dados", "Não foi possível registrar o depósito.")

    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")

def sacar():
    user_id = usuario_logado['id']
    saldo_atual = db_manager.obter_saldo(user_id)
    
    try:
        valor = float(entrada_valor.get().replace(",", "."))
        if valor <= 0:
            messagebox.showerror("Erro", "O valor do saque deve ser positivo.")
        elif valor > saldo_atual:
            messagebox.showwarning("Saldo Insuficiente", "Você não tem saldo suficiente para este saque.")
        else:
            if db_manager.registrar_transacao(user_id, 'saque', valor):
                atualizar_saldo_display()
                messagebox.showinfo("Sucesso", f"Saque de R$ {valor:,.2f} realizado.".replace(",", "X").replace(".", ",").replace("X", "."))
                entrada_valor.delete(0, tk.END)
            else:
                messagebox.showerror("Erro de Banco de Dados", "Não foi possível registrar o saque.")
    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")

def mostrar_historico():
    """Busca o histórico e o exibe em uma nova janela com a formatação correta."""
    user_id = usuario_logado['id']
    historico = db_manager.obter_historico(user_id)
    
    if not historico:
        messagebox.showinfo("Histórico", "Nenhuma transação registrada.")
        return
    
    transacoes_str = ""
    for transacao in historico:
        tipo = transacao["tipo"].capitalize()
        valor = transacao["valor"]
        data_completa = transacao["data"]  # Ex: "29/08/2025 16:20:12"
        
        # Divide a string de data/hora no espaço
        partes_data = data_completa.split(" ")
        data_str = partes_data[0]  # "29/08/2025"
        hora_str = partes_data[1]  # "16:20:12"
        
        # Formata o valor para o padrão brasileiro
        valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        linha = f"{tipo}: {valor_formatado} - {data_str} - {hora_str}\n"
        transacoes_str += linha
      
    # Cria uma nova janela para o histórico
    janela_historico = tk.Toplevel(janela)
    janela_historico.title("Histórico de Transações")
    janela_historico.geometry("400x500")
    janela_historico.configure(bg=COR_PRINCIPAL)
    
    texto_historico = tk.Text(janela_historico, bg=COR_SECUNDARIA, fg=COR_TEXTO, font=FONTE, wrap="word", bd=0)
    texto_historico.insert(tk.END, transacoes_str)
    texto_historico.config(state="disabled") # Impede a edição
    texto_historico.pack(expand=True, fill="both", padx=10, pady=10)

# --- Gerenciamento da Interface Gráfica (GUI) ---

def mostrar_frame(frame_para_mostrar):
    """Esconde todos os frames e mostra apenas o selecionado."""
    frame_login.pack_forget()
    frame_cadastro.pack_forget()
    frame_principal.pack_forget()
    frame_para_mostrar.pack(fill="both", expand=True)

# --- Janela Principal ---
janela = tk.Tk()
janela.title("FinancialManager")
janela.geometry("600x600")
janela.configure(bg=COR_PRINCIPAL)
# Icone do sistema
icone = tk.PhotoImage(file="icon_bank.png")
janela.iconphoto(False, icone)

# --- Estilo para os botões TTK ---
style = ttk.Style(janela)
style.theme_use("default")
style.configure("TButton",
                background=COR_BOTAO,
                foreground=COR_TEXTO,
                font=("Segoe UI", 12, "bold"),
                padding=10,
                borderwidth=0)
style.map("TButton",
          background=[('active', '#00a37e')],
          relief=[('pressed', 'sunken')])


# --- Frame de Login ---
frame_login = tk.Frame(janela, bg=COR_PRINCIPAL)
tk.Label(frame_login, text="Login", font=FONTE_TITULO, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=20)
tk.Label(frame_login, text="Email", font=FONTE, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=(10,0))
entry_email_login = ttk.Entry(frame_login, font=FONTE, justify="center", width=40)
entry_email_login.pack(pady=5, ipady=5)
tk.Label(frame_login, text="Senha", font=FONTE, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=(10,0))
entry_senha_login = ttk.Entry(frame_login, font=FONTE, justify="center", show="*", width=40)
entry_senha_login.pack(pady=5, ipady=5)
ttk.Button(frame_login, text="Entrar", command=fazer_login, width=20).pack(pady=20)
ttk.Button(frame_login, text="Não tenho conta", command=lambda: mostrar_frame(frame_cadastro)).pack()

# --- Frame de Cadastro ---
frame_cadastro = tk.Frame(janela, bg=COR_PRINCIPAL)
tk.Label(frame_cadastro, text="Crie sua Conta", font=FONTE_TITULO, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=20)
tk.Label(frame_cadastro, text="Email", font=FONTE, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=(10,0))
entry_email_cadastro = ttk.Entry(frame_cadastro, font=FONTE, justify="center", width=40)
entry_email_cadastro.pack(pady=5, ipady=5)
tk.Label(frame_cadastro, text="Senha", font=FONTE, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=(10,0))
entry_senha_cadastro = ttk.Entry(frame_cadastro, font=FONTE, justify="center", show="*", width=40)
entry_senha_cadastro.pack(pady=5, ipady=5)
ttk.Button(frame_cadastro, text="Cadastrar", command=cadastrar_usuario, width=20).pack(pady=20)
ttk.Button(frame_cadastro, text="Já tenho conta", command=lambda: mostrar_frame(frame_login)).pack()

# --- Frame Principal da Aplicação ---
frame_principal = tk.Frame(janela, bg=COR_PRINCIPAL)
label_bem_vindo = tk.Label(frame_principal, text="", font=FONTE_TITULO, fg=COR_TEXTO, bg=COR_PRINCIPAL)
label_bem_vindo.pack(pady=20)

frame_saldo = tk.Frame(frame_principal, bg=COR_SECUNDARIA, bd=0)
frame_saldo.pack(pady=10, padx=20, fill="x")
tk.Label(frame_saldo, text="Saldo Atual", font=FONTE, fg=COR_TEXTO, bg=COR_SECUNDARIA).pack(pady=5)
label_saldo = tk.Label(frame_saldo, text="R$ 0,00", font=FONTE_SALDO, fg="#00cec9", bg=COR_SECUNDARIA)
label_saldo.pack(pady=5)

entrada_valor = ttk.Entry(frame_principal, font=FONTE, justify="center")
entrada_valor.pack(pady=15, ipadx=5, ipady=5)

frame_botoes = tk.Frame(frame_principal, bg=COR_PRINCIPAL)
frame_botoes.pack(pady=10)
ttk.Button(frame_botoes, text="Depositar", command=depositar).grid(row=0, column=0, padx=10, pady=5)
ttk.Button(frame_botoes, text="Sacar", command=sacar).grid(row=0, column=1, padx=10, pady=5)

ttk.Button(frame_principal, text="Histórico de Transações", command=mostrar_historico).pack(pady=10)
ttk.Button(frame_principal, text="Sair (Logout)", command=fazer_logout).pack(pady=20)

# --- Inicialização da Aplicação ---
db_manager.inicializar_banco() 
mostrar_frame(frame_login) # A aplicação começa na tela de login
janela.mainloop()
