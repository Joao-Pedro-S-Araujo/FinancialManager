import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib # Importado para hashing de senha

# --- Configurações de Estilo ---
COR_PRINCIPAL = "#1e1e2f"
COR_SECUNDARIA = "#2e2e3f"
COR_BOTAO = "#00b894"
COR_TEXTO = "#ffffff"
FONTE = ("Segoe UI", 12)

# --- Variáveis Globais e Configuração do "Banco de Dados" ---
NOME_ARQUIVO = 'dados_usuarios.json'
usuarios = [] # Estrutura de dados unificada

# --- Funções de Lógica e Dados ---

def carregar_dados():
    """Carrega os dados dos usuários do arquivo JSON para a memória."""
    global usuarios
    if not os.path.exists(NOME_ARQUIVO):
        # Se o arquivo não existe, cria um vazio com a estrutura correta
        with open(NOME_ARQUIVO, 'w', encoding='utf-8') as arquivo:
            json.dump({"usuarios": []}, arquivo, indent=4)
        usuarios = []
        return

    with open(NOME_ARQUIVO, 'r', encoding='utf-8') as arquivo:
        try:
            dados = json.load(arquivo)
            # Garantir que a chave 'usuarios' exista
            usuarios = dados.get("usuarios", [])
        except json.JSONDecodeError:
            # Se o arquivo estiver corrompido ou vazio, inicializa com uma lista vazia
            usuarios = []

def salvar_dados():
    """Salva a lista de usuários atual no arquivo JSON."""
    with open(NOME_ARQUIVO, 'w', encoding='utf-8') as arquivo:
        # Salva no formato {"usuarios": [...]} para manter a estrutura
        json.dump({"usuarios": usuarios}, arquivo, indent=4)

def hash_senha(senha):
    """Gera um hash SHA-256 para a senha fornecida."""
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def gerar_novo_id():
    """Gera um novo ID único para o usuário."""
    if not usuarios:
        return 1
    # Encontra o maior ID existente e adiciona 1
    return max(usuario['id'] for usuario in usuarios) + 1

def cadastrar_usuario():
    """Função principal para o processo de cadastro."""
    email = entrada_email.get().strip()
    senha = entrada_senha.get().strip()

    # 1. Validação das entradas
    if not email or not senha:
        messagebox.showerror("Erro de Cadastro", "Por favor, preencha todos os campos.")
        return

    if "@" not in email or "." not in email:
        messagebox.showerror("Erro de Cadastro", "Por favor, insira um email válido.")
        return

    # 2. Verificar se o email já existe
    for usuario in usuarios:
        if usuario['email'] == email:
            messagebox.showwarning("Cadastro Falhou", "Este email já está cadastrado.")
            return

    # 3. Criação do novo usuário
    novo_id = gerar_novo_id()
    senha_hashed = hash_senha(senha)

    novo_usuario = {
        "id": novo_id,
        "email": email,
        "senha_hash": senha_hashed
    }

    # 4. Adicionar e salvar
    usuarios.append(novo_usuario)
    salvar_dados()
    
    # 5. Feedback e limpeza dos campos
    messagebox.showinfo("Sucesso", f"Usuário cadastrado com sucesso! Seu ID é: {novo_id}")
    entrada_email.delete(0, tk.END)
    entrada_senha.delete(0, tk.END)

# --- Inicialização da Aplicação ---
carregar_dados() # Carrega os dados existentes ao iniciar

# --- Interface Gráfica (GUI) ---
janela = tk.Tk()
janela.title("FinancialManager - Cadastro")
janela.geometry("400x500")
janela.configure(bg=COR_PRINCIPAL)
janela.resizable(False, False)

# Título
titulo = tk.Label(janela, text="Crie sua Conta", font=("Segoe UI", 20, "bold"), fg=COR_TEXTO, bg=COR_PRINCIPAL)
titulo.pack(pady=20)

# Frame para centralizar os widgets
frame_central = tk.Frame(janela, bg=COR_PRINCIPAL)
frame_central.pack(pady=20, padx=40, fill="both", expand=True)

# Email para cadastro
label_email = tk.Label(frame_central, text="Email", font=("Segoe UI", 15), fg=COR_TEXTO, bg=COR_PRINCIPAL)
label_email.pack(pady=(10, 5), anchor="w")

# Entrada de email (com nome de variável único)
entrada_email = ttk.Entry(frame_central, font=FONTE, justify="center")
entrada_email.pack(pady=5, fill="x", ipady=5)

# Criar senha
label_senha = tk.Label(frame_central, text="Senha", font=("Segoe UI", 15), fg=COR_TEXTO, bg=COR_PRINCIPAL)
label_senha.pack(pady=(20, 5), anchor="w")

# Entrada senha (com nome de variável único e ocultando caracteres)
entrada_senha = ttk.Entry(frame_central, font=FONTE, justify="center", show="*")
entrada_senha.pack(pady=5, fill="x", ipady=5)

# Botão cadastrar
btn_cadastrar = tk.Button(
    frame_central,
    text="Cadastrar",
    font=("Segoe UI", 14, "bold"),
    bg=COR_BOTAO,
    fg=COR_TEXTO,
    command=cadastrar_usuario, # Conecta o botão à função de cadastro
    relief="flat",
    borderwidth=0,
    activebackground="#00a37e",
    activeforeground=COR_TEXTO
)
btn_cadastrar.pack(pady=40, fill="x", ipady=10)

janela.mainloop()