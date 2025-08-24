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
NOME_ARQUIVO = 'historico.json'
saldo = 0
historico_transacoes = []

# --- Funções de persistência ---
def carregar_dados():
    global saldo, historico_transacoes
    if os.path.exists(NOME_ARQUIVO):
        with open(NOME_ARQUIVO, 'r', encoding='utf-8') as arquivo:
            try:
                dados = json.load(arquivo)
                saldo = dados.get('saldo', 0)
                historico_transacoes = dados.get('historico', [])
            except json.JSONDecodeError:
                # O arquivo está vazio ou corrompido, inicia com valores padrão
                saldo = 0
                historico_transacoes = []
    # Se o arquivo não existe, as variáveis já estão com os valores iniciais (0 e [])

def salvar_dados():
    dados = {
        'saldo': saldo,
        'historico': historico_transacoes
    }
    with open(NOME_ARQUIVO, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, indent=4)

# --- Funções para a interface (com alterações) ---

def mostrar_saldo():
    messagebox.showinfo("Saldo", f"Seu saldo atual é: R${saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

def depositar():
    global saldo
    try:
        valor = float(entrada_valor.get().replace(",", ".")) # Aceita vírgula como separador
        if valor <= 0:
            messagebox.showerror("Erro", "Valor inválido para depósito. O valor deve ser positivo.")
        else:
            saldo += valor
            transacao = {
                "tipo": "depósito",
                "valor": valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            historico_transacoes.append(transacao)
            salvar_dados() # Salva após a transação
            atualizar_saldo()
            messagebox.showinfo("Depósito", f"Depósito de R$ {valor:,.2f} realizado com sucesso!".replace(",", "X").replace(".", ",").replace("X", "."))
            entrada_valor.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")

def sacar():
    global saldo
    try:
        valor = float(entrada_valor.get().replace(",", "."))
        if valor <= 0:
            messagebox.showerror("Erro", "Valor inválido para saque. O valor deve ser positivo.")
        elif valor > saldo:
            messagebox.showwarning("Saldo insuficiente", "Você não tem saldo suficiente.")
        else:
            saldo -= valor
            transacao = {
                "tipo": "saque",
                "valor": valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            historico_transacoes.append(transacao)
            salvar_dados() # Salva após a transação
            atualizar_saldo()
            messagebox.showinfo("Saque", f"Saque de R$ {valor:,.2f} realizado com sucesso!".replace(",", "X").replace(".", ",").replace("X", "."))
            entrada_valor.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")

def atualizar_saldo():
    # Atualiza a exibição do saldo
    label_saldo.config(text=f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

def mostrar_historico():
    if not historico_transacoes:
        messagebox.showinfo("Histórico", "Nenhuma transação registrada.")
    else:
        # Formata o histórico de forma mais clara
        transacoes_str = ""
        for transacao in historico_transacoes:
            tipo = transacao.get("tipo", "Desconhecido").capitalize()
            valor = transacao.get("valor", 0)
            data = transacao.get("data", "Sem data")
            transacoes_str += f"{tipo}: R$ {valor:,.2f} em {data}\n".replace(",", "X").replace(".", ",").replace("X", ".")
        messagebox.showinfo("Histórico de Transações", transacoes_str)

# --- Janela principal (com chamadas das funções de persistência) ---
janela = tk.Tk()
janela.title("FinancialManager")
janela.geometry("560x510")
janela.configure(bg=COR_PRINCIPAL)

# Carrega os dados salvos antes de inicializar a interface
carregar_dados()

# Estilo
style = ttk.Style()
style.theme_use("default")
style.configure("TButton",
                background=COR_BOTAO,
                foreground="white",
                font=FONTE,
                padding=10)
style.map("TButton",
          background=[('active', '#019875')])

# Título
titulo = tk.Label(janela, text="Bem vindo(a)", font=("Segoe UI", 20, "bold"), fg=COR_TEXTO, bg=COR_PRINCIPAL)
titulo.pack(pady=20)

# Saldo
frame_saldo = tk.Frame(janela, bg=COR_SECUNDARIA, bd=0, relief="groove")
frame_saldo.pack(pady=10, padx=20, fill="x")

label_saldo_titulo = tk.Label(frame_saldo, text="Saldo Atual", font=FONTE, fg=COR_TEXTO, bg=COR_SECUNDARIA)
label_saldo_titulo.pack(pady=5)

label_saldo = tk.Label(frame_saldo, text=f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), font=("Segoe UI", 16, "bold"), fg="#00cec9", bg=COR_SECUNDARIA)
label_saldo.pack(pady=5)

# Entrada de valor
entrada_valor = ttk.Entry(janela, font=FONTE, justify="center")
entrada_valor.pack(pady=15, ipadx=5, ipady=5)

# Botões
frame_botoes = tk.Frame(janela, bg=COR_PRINCIPAL)
frame_botoes.pack(pady=10)

btn_depositar = ttk.Button(frame_botoes, text="Depositar", command=depositar)
btn_depositar.grid(row=0, column=0, padx=10, pady=5)

btn_sacar = ttk.Button(frame_botoes, text="Sacar", command=sacar)
btn_sacar.grid(row=0, column=1, padx=10, pady=5)

btn_saldo = ttk.Button(frame_botoes, text="Mostrar Saldo", command=mostrar_saldo)
btn_saldo.grid(row=0, column=2, padx=10, pady=5)

btn_historico = ttk.Button(janela, text="Histórico de Transações", command=mostrar_historico)
btn_historico.pack(pady=10)

btn_sair = ttk.Button(janela, text="Sair", command=janela.destroy)
btn_sair.pack(pady=5)

icone = tk.PhotoImage(file='icon_bank.png')
janela.iconphoto(True, icone)

janela.mainloop()