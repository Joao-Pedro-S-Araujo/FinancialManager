import tkinter as tk
from tkinter import ttk, messagebox

# Cores e estilo
COR_PRINCIPAL = "#1e1e2f"
COR_SECUNDARIA = "#2e2e3f"
COR_BOTAO = "#00b894"
COR_TEXTO = "#ffffff"
FONTE = ("Segoe UI", 12)

saldo = 0

# Funções
def mostrar_saldo():
    messagebox.showinfo("Saldo", f"Seu saldo atual é: R${saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

def depositar():
    global saldo
    try:
        valor = float(entrada_valor.get())
        if valor < 0:
            messagebox.showerror("Erro", "Valor inválido para depósito.")
        else:
            saldo += valor
            atualizar_saldo()
            messagebox.showinfo("Depósito", f"Depósito de R$ {valor:.2f} realizado com sucesso!")
            entrada_valor.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")

def sacar():
    global saldo
    try:
        valor = float(entrada_valor.get())
        if valor < 0:
            messagebox.showerror("Erro", "Valor inválido para saque.")
        elif valor > saldo:
            messagebox.showwarning("Saldo insuficiente", "Você não tem saldo suficiente.")
        else:
            saldo -= valor
            atualizar_saldo()
            messagebox.showinfo("Saque", f"Saque de R$ {valor:.2f} realizado com sucesso!")
            entrada_valor.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")

def atualizar_saldo():
    label_saldo.config(text=f"R$ {saldo:.2f}")

# Janela principal
janela = tk.Tk()
janela.title("Finança fácil")
janela.geometry("400x400")
janela.configure(bg=COR_PRINCIPAL)

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

label_saldo = tk.Label(frame_saldo, text=f"R$ {saldo:.2f}", font=("Segoe UI", 16, "bold"), fg="#00cec9", bg=COR_SECUNDARIA)
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

btn_saldo = ttk.Button(janela, text="Mostrar Saldo", command=mostrar_saldo)
btn_saldo.pack(pady=10)

btn_sair = ttk.Button(janela, text="Sair", command=janela.destroy)
btn_sair.pack(pady=5)

janela.mainloop()
