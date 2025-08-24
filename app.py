import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
from datetime import datetime

# --- Configurações de Estilo ---
COR_PRINCIPAL = "#1e1e2f"
COR_SECUNDARIA = "#2e2e3f"
COR_BOTAO = "#00b894"
COR_TEXTO = "#ffffff"
FONTE = ("Segoe UI", 12)
FONTE_TITULO = ("Segoe UI", 20, "bold")
FONTE_SALDO = ("Segoe UI", 16, "bold")

# --- Nomes dos Arquivos de "Banco de Dados" ---
ARQUIVO_USUARIOS = 'dados_usuarios.json'
ARQUIVO_FINANCEIRO = 'dados_financeiros.json'

# --- Variáveis Globais de Estado ---
usuarios = []
dados_financeiros = {} # Dicionário para armazenar dados por ID de usuário
usuario_logado = None  # Armazenará os dados do usuário logado

# --- Funções de Gerenciamento de Dados ---

def carregar_dados_iniciais():
    """Carrega ambos os arquivos JSON para a memória ao iniciar."""
    global usuarios, dados_financeiros
    
    # Carregar usuários
    if not os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as f:
            json.dump({"usuarios": []}, f)
    with open(ARQUIVO_USUARIOS, 'r', encoding='utf-8') as f:
        try:
            usuarios = json.load(f).get("usuarios", [])
        except json.JSONDecodeError:
            usuarios = []

    # Carregar dados financeiros
    if not os.path.exists(ARQUIVO_FINANCEIRO):
        with open(ARQUIVO_FINANCEIRO, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    with open(ARQUIVO_FINANCEIRO, 'r', encoding='utf-8') as f:
        try:
            dados_financeiros = json.load(f)
        except json.JSONDecodeError:
            dados_financeiros = {}

def salvar_usuarios():
    """Salva a lista de usuários no arquivo JSON."""
    with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as f:
        json.dump({"usuarios": usuarios}, f, indent=4)

def salvar_dados_financeiros():
    """Salva todos os dados financeiros no arquivo JSON."""
    with open(ARQUIVO_FINANCEIRO, 'w', encoding='utf-8') as f:
        json.dump(dados_financeiros, f, indent=4)

# --- Funções de Autenticação e Usuário ---

def hash_senha(senha):
    """Gera um hash SHA-256 para a senha."""
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def cadastrar_usuario():
    """Registra um novo usuário e cria seus dados financeiros iniciais."""
    email = entry_email_cadastro.get().strip()
    senha = entry_senha_cadastro.get().strip()
    
    if not email or not senha:
        messagebox.showerror("Erro", "Preencha todos os campos.")
        return
    if any(u['email'] == email for u in usuarios):
        messagebox.showwarning("Erro", "Este email já está cadastrado.")
        return

    novo_id = (max(u['id'] for u in usuarios) + 1) if usuarios else 1
    novo_usuario = {
        "id": novo_id,
        "email": email,
        "senha_hash": hash_senha(senha)
    }
    usuarios.append(novo_usuario)
    salvar_usuarios()

    # Cria o registro financeiro inicial para o novo usuário
    dados_financeiros[str(novo_id)] = {"saldo": 0, "historico": []}
    salvar_dados_financeiros()

    messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso! Faça o login.")
    mostrar_frame(frame_login)

def fazer_login():
    """Valida as credenciais do usuário e inicia a sessão."""
    global usuario_logado
    email = entry_email_login.get().strip()
    senha = entry_senha_login.get().strip()

    if not email or not senha:
        messagebox.showerror("Erro de Login", "Preencha todos os campos.")
        return

    senha_hashed = hash_senha(senha)
    
    for user in usuarios:
        if user['email'] == email and user['senha_hash'] == senha_hashed:
            usuario_logado = user
            iniciar_sessao_app()
            return
    
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

# --- Funções Financeiras (Agora específicas para o usuário logado) ---

def atualizar_saldo_display():
    """Atualiza o label do saldo na tela principal."""
    user_id_str = str(usuario_logado['id'])
    saldo_atual = dados_financeiros.get(user_id_str, {}).get('saldo', 0)
    label_saldo.config(text=f"R$ {saldo_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

def depositar():
    user_id_str = str(usuario_logado['id'])
    try:
        valor = float(entrada_valor.get().replace(",", "."))
        if valor <= 0:
            messagebox.showerror("Erro", "O valor do depósito deve ser positivo.")
            return
        
        dados_financeiros[user_id_str]['saldo'] += valor
        transacao = {"tipo": "depósito", "valor": valor, "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        dados_financeiros[user_id_str]['historico'].append(transacao)
        
        salvar_dados_financeiros()
        atualizar_saldo_display()
        messagebox.showinfo("Sucesso", f"Depósito de R$ {valor:,.2f} realizado.".replace(",", "X").replace(".", ",").replace("X", "."))
        entrada_valor.delete(0, tk.END)

    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")

def sacar():
    user_id_str = str(usuario_logado['id'])
    saldo_atual = dados_financeiros[user_id_str]['saldo']
    try:
        valor = float(entrada_valor.get().replace(",", "."))
        if valor <= 0:
            messagebox.showerror("Erro", "O valor do saque deve ser positivo.")
        elif valor > saldo_atual:
            messagebox.showwarning("Saldo Insuficiente", "Você não tem saldo suficiente para este saque.")
        else:
            dados_financeiros[user_id_str]['saldo'] -= valor
            transacao = {"tipo": "saque", "valor": valor, "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
            dados_financeiros[user_id_str]['historico'].append(transacao)

            salvar_dados_financeiros()
            atualizar_saldo_display()
            messagebox.showinfo("Sucesso", f"Saque de R$ {valor:,.2f} realizado.".replace(",", "X").replace(".", ",").replace("X", "."))
            entrada_valor.delete(0, tk.END)

    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")

def mostrar_historico():
    user_id_str = str(usuario_logado['id'])
    historico = dados_financeiros[user_id_str]['historico']
    if not historico:
        messagebox.showinfo("Histórico", "Nenhuma transação registrada.")
        return
    
    transacoes_str = ""
    for transacao in reversed(historico): # Mostra as mais recentes primeiro
        tipo = transacao.get("tipo", "N/A").capitalize()
        valor = transacao.get("valor", 0)
        data = transacao.get("data", "N/A")
        transacoes_str += f"{data} - {tipo}: R$ {valor:,.2f}\n".replace(",", "X").replace(".", ",").replace("X", ".")
    
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
carregar_dados_iniciais()
mostrar_frame(frame_login) # A aplicação começa na tela de login
janela.mainloop()
