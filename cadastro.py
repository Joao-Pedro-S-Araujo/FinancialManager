import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Cores e estilo
COR_PRINCIPAL = "#1e1e2f"
COR_SECUNDARIA = "#2e2e3f"
COR_BOTAO = "#00b894"
COR_TEXTO = "#ffffff"
FONTE = ("Segoe UI", 12)

# --- Variáveis globais ---
NOME_ARQUIVO = 'dados_login.json'
dados_login = []
dados_senha = []

# Criar o arquivo .json
def carregar_dados():
    global dados_login
    if os.path.exists(NOME_ARQUIVO):
        with open(NOME_ARQUIVO, 'r', encoding='utf-8') as arquivo:
            try:
                dados = json.load(arquivo)
                
            except json.JSONDecodeError:
                # O arquivo está vazio ou corrompido, inicia com valores padrão
                dados_login = []
    # Se o arquivo não existe, as variáveis já estão com os valores iniciais (0 e [])

def salvar_dados():
    dados = {
        'login': dados_login,
        'senha': dados_senha,
    }
    with open(NOME_ARQUIVO, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, indent=4)

