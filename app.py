import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from datetime import datetime
import db_manager
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkcalendar import DateEntry

# =================================================================
# 1. CONFIGURAÇÕES DE ESTILO E VARIÁVEIS GLOBAIS
# =================================================================

COR_PRINCIPAL = "#1e1e2f"
COR_SECUNDARIA = "#2e2e3f"
COR_BOTAO = "#00b894"
COR_TEXTO = "#ffffff"
FONTE = ("Segoe UI", 12)
FONTE_TITULO = ("Segoe UI", 20, "bold")
FONTE_SALDO = ("Segoe UI", 16, "bold")

usuario_logado = None

# =================================================================
# 2. DEFINIÇÃO DE TODAS AS FUNÇÕES
# =================================================================

# --- Funções de Autenticação e Sessão ---

def hash_senha(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def cadastrar_usuario():
    email = entry_email_cadastro.get().strip()
    senha = entry_senha_cadastro.get().strip()
    if not email or not senha:
        messagebox.showerror("Erro", "Preencha todos os campos.")
        return
    if db_manager.buscar_usuario_por_email(email):
        messagebox.showwarning("Erro", "Este email já está cadastrado.")
        return
    senha_hashed = hash_senha(senha)
    if db_manager.adicionar_usuario(email, senha_hashed):
        messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso! Faça o login.")
        mostrar_frame(frame_login)
    else:
        messagebox.showerror("Erro de Banco de Dados", "Não foi possível realizar o cadastro.")

def fazer_login():
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
    label_bem_vindo.config(text=f"Bem-vindo(a), {usuario_logado['email']}")
    preencher_dashboard()
    mostrar_frame(frame_principal)

def fazer_logout():
    global usuario_logado
    usuario_logado = None
    entry_email_login.delete(0, tk.END)
    entry_senha_login.delete(0, tk.END)
    mostrar_frame(frame_login)

# --- Funções das Janelas da Aplicação ---

def abrir_janela_transacao():
    janela_trans = tk.Toplevel(janela)
    janela_trans.title("Registrar Nova Transação")
    janela_trans.geometry("450x400")
    janela_trans.configure(bg=COR_PRINCIPAL)
    janela_trans.transient(janela)
    janela_trans.grab_set()

    tk.Label(janela_trans, text="Valor (R$)", font=FONTE, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=(20, 5))
    entrada_valor_trans = ttk.Entry(janela_trans, font=FONTE, justify="center")
    entrada_valor_trans.pack(pady=5, ipady=5)

    tk.Label(janela_trans, text="Categoria (para saques)", font=FONTE, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=(15, 5))
    categorias = ["Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Educação", "Compras", "Outros"]
    combo_categorias_trans = ttk.Combobox(janela_trans, values=categorias, font=FONTE, justify="center", state="readonly")
    combo_categorias_trans.pack(pady=5, ipady=3)

    def executar_deposito():
        try:
            valor = float(entrada_valor_trans.get().replace(",", "."))
            if valor <= 0:
                messagebox.showerror("Erro", "O valor deve ser positivo.", parent=janela_trans)
                return
            if db_manager.registrar_transacao(usuario_logado['id'], 'deposito', valor):
                messagebox.showinfo("Sucesso", "Depósito realizado!", parent=janela_trans)
                preencher_dashboard()
                janela_trans.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.", parent=janela_trans)

    def executar_saque():
        categoria = combo_categorias_trans.get()
        if not categoria:
            messagebox.showwarning("Atenção", "Selecione uma categoria.", parent=janela_trans)
            return
        try:
            valor = float(entrada_valor_trans.get().replace(",", "."))
            if valor <= 0:
                messagebox.showerror("Erro", "O valor deve ser positivo.", parent=janela_trans)
                return
            if db_manager.registrar_transacao(usuario_logado['id'], 'saque', valor, categoria):
                messagebox.showinfo("Sucesso", "Saque realizado!", parent=janela_trans)
                preencher_dashboard()
                janela_trans.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.", parent=janela_trans)

    frame_botoes_trans = tk.Frame(janela_trans, bg=COR_PRINCIPAL)
    frame_botoes_trans.pack(pady=30)
    ttk.Button(frame_botoes_trans, text="Depositar", command=executar_deposito).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes_trans, text="Sacar", command=executar_saque).grid(row=0, column=1, padx=10)

def abrir_janela_transferencia():
    janela_transf = tk.Toplevel(janela)
    janela_transf.title("Transferir Dinheiro")
    janela_transf.geometry("400x300")
    janela_transf.configure(bg=COR_PRINCIPAL)
    janela_transf.resizable(False, False)
    janela_transf.transient(janela)
    janela_transf.grab_set()

    tk.Label(janela_transf, text="Email do Destinatário", font=FONTE, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=(20, 5))
    entry_email = ttk.Entry(janela_transf, font=FONTE, width=30, justify="center")
    entry_email.pack(ipady=5)

    tk.Label(janela_transf, text="Valor a Transferir (R$)", font=FONTE, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=(20, 5))
    entry_valor = ttk.Entry(janela_transf, font=FONTE, width=30, justify="center")
    entry_valor.pack(ipady=5)
    
    def executar_transferencia():
        email_destinatario = entry_email.get().strip()
        try:
            valor = float(entry_valor.get().strip().replace(",", "."))
            if not email_destinatario or valor <= 0:
                messagebox.showwarning("Dados Inválidos", "Preencha o email e um valor positivo.", parent=janela_transf)
                return
            if messagebox.askyesno("Confirmar", f"Deseja transferir R$ {valor:,.2f} para {email_destinatario}?", parent=janela_transf):
                resultado = db_manager.registrar_transferencia(usuario_logado['id'], email_destinatario, valor)
                if resultado['sucesso']:
                    messagebox.showinfo("Sucesso", resultado['mensagem'], parent=janela_transf)
                    preencher_dashboard()
                    janela_transf.destroy()
                else:
                    messagebox.showerror("Erro", resultado['mensagem'], parent=janela_transf)
        except ValueError:
            messagebox.showerror("Erro de Valor", "Por favor, insira um valor numérico válido.", parent=janela_transf)

    ttk.Button(janela_transf, text="Confirmar Transferência", command=executar_transferencia).pack(pady=30)

def abrir_janela_edicao(transacao_id, callback_atualizacao):
    transacao = db_manager.obter_transacao_por_id(transacao_id)
    if not transacao:
        messagebox.showerror("Erro", "Não foi possível encontrar a transação.")
        return

    janela_edit = tk.Toplevel(janela)
    janela_edit.title("Editar Transação")
    janela_edit.geometry("450x300")
    janela_edit.configure(bg=COR_PRINCIPAL)
    janela_edit.transient(janela)
    janela_edit.grab_set()

    tk.Label(janela_edit, text="Valor (R$)", font=FONTE, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=(20, 5))
    entry_valor_edit = ttk.Entry(janela_edit, font=FONTE, justify="center")
    entry_valor_edit.pack(pady=5, ipady=5)
    entry_valor_edit.insert(0, f"{transacao['valor']:.2f}".replace(".", ","))

    tk.Label(janela_edit, text="Categoria", font=FONTE, fg=COR_TEXTO, bg=COR_PRINCIPAL).pack(pady=(15, 5))
    categorias = ["Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Educação", "Compras", "Outros"]
    combo_categorias_edit = ttk.Combobox(janela_edit, values=categorias, font=FONTE, justify="center", state="readonly")
    combo_categorias_edit.pack(pady=5, ipady=3)
    if transacao['categoria'] in categorias:
        combo_categorias_edit.set(transacao['categoria'])

    def salvar_edicao():
        try:
            novo_valor = float(entry_valor_edit.get().replace(",", "."))
            nova_categoria = combo_categorias_edit.get()
            if novo_valor <= 0 or not nova_categoria:
                messagebox.showwarning("Dados Inválidos", "Preencha todos os campos com valores válidos.", parent=janela_edit)
                return

            resultado = db_manager.editar_transacao(transacao_id, usuario_logado['id'], novo_valor, nova_categoria)
            if resultado['sucesso']:
                messagebox.showinfo("Sucesso", "Transação atualizada com sucesso.", parent=janela_edit)
                preencher_dashboard()
                callback_atualizacao()
                janela_edit.destroy()
            else:
                messagebox.showerror("Erro", "Não foi possível atualizar a transação.", parent=janela_edit)
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.", parent=janela_edit)

    ttk.Button(janela_edit, text="Salvar Alterações", command=salvar_edicao).pack(pady=30)

def mostrar_historico():
    janela_historico = tk.Toplevel(janela)
    janela_historico.title("Histórico de Transações")
    janela_historico.geometry("800x600")
    janela_historico.configure(bg=COR_PRINCIPAL)
    janela_historico.transient(janela)
    janela_historico.grab_set()

    frame_filtros = tk.Frame(janela_historico, bg=COR_PRINCIPAL)
    frame_filtros.pack(pady=10, padx=20, fill='x')

    tk.Label(frame_filtros, text="De:", bg=COR_PRINCIPAL, fg=COR_TEXTO, font=FONTE).pack(side='left', padx=(0, 5))
    cal_inicio = DateEntry(frame_filtros, width=12, background=COR_BOTAO, date_pattern='dd/mm/yyyy', foreground='white', borderwidth=2, font=FONTE)
    cal_inicio.pack(side='left')
    cal_inicio.set_date(None); cal_inicio.delete(0, "end")

    tk.Label(frame_filtros, text="Até:", bg=COR_PRINCIPAL, fg=COR_TEXTO, font=FONTE).pack(side='left', padx=(20, 5))
    cal_fim = DateEntry(frame_filtros, width=12, background=COR_BOTAO, date_pattern='dd/mm/yyyy', foreground='white', borderwidth=2, font=FONTE)
    cal_fim.pack(side='left')
    cal_fim.set_date(None); cal_fim.delete(0, "end")

    style_tree = ttk.Style()
    style_tree.configure("Treeview", background=COR_SECUNDARIA, foreground=COR_TEXTO, rowheight=25, fieldbackground=COR_SECUNDARIA, font=FONTE)
    style_tree.map('Treeview', background=[('selected', COR_BOTAO)])
    style_tree.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
    
    frame_tabela = tk.Frame(janela_historico)
    frame_tabela.pack(expand=True, fill='both', padx=20, pady=10)

    colunas = ('data', 'hora', 'tipo', 'categoria', 'valor')
    tree = ttk.Treeview(frame_tabela, columns=colunas, show='headings', style="Treeview")
    
    tree.heading('data', text='Data'); tree.heading('hora', text='Hora'); tree.heading('tipo', text='Tipo'); tree.heading('categoria', text='Categoria'); tree.heading('valor', text='Valor')
    tree.column('data', anchor=tk.CENTER, width=100); tree.column('hora', anchor=tk.CENTER, width=100); tree.column('tipo', anchor=tk.CENTER, width=100); tree.column('categoria', anchor=tk.CENTER, width=120); tree.column('valor', anchor=tk.E, width=150)
    tree.pack(side='left', expand=True, fill='both')
    
    scrollbar = ttk.Scrollbar(frame_tabela, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

    def atualizar_historico():
        for i in tree.get_children(): tree.delete(i)
        historico = db_manager.obter_historico(usuario_logado['id'], cal_inicio.get_date(), cal_fim.get_date())
        if not historico:
            tree.insert('', tk.END, values=("", "Sem resultados", "", "", ""))
            return
        for transacao in historico:
            partes_data = transacao["data"].split(" ")
            valor_formatado = f"R$ {transacao['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tag_cor = 'deposito' if transacao["tipo"] == 'deposito' else 'saque'
            tree.insert('', tk.END, text=transacao['id'], values=(partes_data[0], partes_data[1], transacao["tipo"].capitalize(), transacao.get("categoria") or "", valor_formatado), tags=(tag_cor,))

    tree.tag_configure('deposito', foreground='#2ecc71'); tree.tag_configure('saque', foreground='#e74c3c')
    
    def limpar_filtros():
        cal_inicio.set_date(None); cal_inicio.delete(0, "end")
        cal_fim.set_date(None); cal_fim.delete(0, "end")
        atualizar_historico()

    menu_contexto = tk.Menu(janela_historico, tearoff=0)
    def mostrar_menu(event):
        item_selecionado = tree.identify_row(event.y)
        if item_selecionado:
            tree.selection_set(item_selecionado)
            menu_contexto.tk_popup(event.x_root, event.y_root)

    def acao_excluir():
        if not tree.selection(): return
        item_selecionado = tree.selection()[0]
        transacao_id = tree.item(item_selecionado, 'text')
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir esta transação?", parent=janela_historico):
            if db_manager.excluir_transacao(transacao_id, usuario_logado['id']):
                messagebox.showinfo("Sucesso", "Transação excluída.", parent=janela_historico)
                atualizar_historico()
                preencher_dashboard()
            else:
                messagebox.showerror("Erro", "Não foi possível excluir a transação.", parent=janela_historico)

    def acao_editar():
        if not tree.selection(): return
        item_selecionado = tree.selection()[0]
        transacao_id = tree.item(item_selecionado, 'text')
        abrir_janela_edicao(transacao_id, atualizar_historico)

    menu_contexto.add_command(label="✏️ Editar Transação", command=acao_editar)
    menu_contexto.add_command(label="❌ Excluir Transação", command=acao_excluir)
    tree.bind("<Button-3>", mostrar_menu)
        
    ttk.Button(frame_filtros, text="Filtrar", command=atualizar_historico).pack(side='left', padx=(20, 5))
    ttk.Button(frame_filtros, text="Limpar Filtro", command=limpar_filtros).pack(side='left', padx=5)
    atualizar_historico()

def abrir_janela_relatorio():
    """Abre uma nova janela que exibe um gráfico de barras dos gastos por categoria com filtros de data."""
    janela_rel = tk.Toplevel(janela)
    janela_rel.title("Relatório de Despesas por Categoria")
    janela_rel.geometry("900x700") # Aumentei a altura para os filtros
    janela_rel.configure(bg=COR_PRINCIPAL)
    janela_rel.transient(janela)
    janela_rel.grab_set()

    # --- Frame para os Filtros ---
    frame_filtros = tk.Frame(janela_rel, bg=COR_PRINCIPAL)
    frame_filtros.pack(pady=10, padx=20, fill='x')

    tk.Label(frame_filtros, text="De:", bg=COR_PRINCIPAL, fg=COR_TEXTO, font=FONTE).pack(side='left', padx=(0, 5))
    cal_inicio = DateEntry(frame_filtros, width=12, background=COR_BOTAO, date_pattern='dd/mm/yyyy', foreground='white', borderwidth=2, font=FONTE)
    cal_inicio.pack(side='left')
    cal_inicio.set_date(None); cal_inicio.delete(0, "end")

    tk.Label(frame_filtros, text="Até:", bg=COR_PRINCIPAL, fg=COR_TEXTO, font=FONTE).pack(side='left', padx=(20, 5))
    cal_fim = DateEntry(frame_filtros, width=12, background=COR_BOTAO, date_pattern='dd/mm/yyyy', foreground='white', borderwidth=2, font=FONTE)
    cal_fim.pack(side='left')
    cal_fim.set_date(None); cal_fim.delete(0, "end")

    # --- Frame para o Gráfico ---
    frame_grafico = tk.Frame(janela_rel, bg=COR_PRINCIPAL)
    frame_grafico.pack(expand=True, fill='both', padx=20, pady=10)

    fig = Figure(figsize=(8, 6), dpi=100, facecolor=COR_PRINCIPAL)
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # --- Função para Atualizar o Gráfico ---
    def atualizar_grafico():
        data_inicio_val = cal_inicio.get_date()
        data_fim_val = cal_fim.get_date()
        
        dados_categorias = db_manager.obter_gastos_por_categoria(usuario_logado['id'], data_inicio_val, data_fim_val)
        
        fig.clear() # Limpa o gráfico anterior
        ax = fig.add_subplot(111)
        ax.set_facecolor(COR_SECUNDARIA)

        if not dados_categorias:
            ax.text(0.5, 0.5, "Sem dados para o período selecionado.", color=COR_TEXTO, ha='center', va='center', fontsize=14)
            ax.tick_params(axis='x', colors=COR_SECUNDARIA)
            ax.tick_params(axis='y', colors=COR_SECUNDARIA)
        else:
            labels = [item['categoria'] for item in dados_categorias]
            sizes = [item['total'] for item in dados_categorias]
            labels.reverse(); sizes.reverse()

            ax.tick_params(axis='x', colors=COR_TEXTO); ax.tick_params(axis='y', colors=COR_TEXTO)
            ax.spines['bottom'].set_color(COR_TEXTO); ax.spines['top'].set_color(COR_SECUNDARIA)
            ax.spines['right'].set_color(COR_SECUNDARIA); ax.spines['left'].set_color(COR_TEXTO)
            
            bars = ax.barh(labels, sizes, color=COR_BOTAO, height=0.6)
            for bar in bars:
                width = bar.get_width()
                label_text = f" R$ {width:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                ax.text(width, bar.get_y() + bar.get_height()/2.0, label_text, va='center', ha='left', color=COR_TEXTO, fontweight='bold')
            
            ax.set_xlabel('Valor Gasto (R$)', color=COR_TEXTO, fontsize=12)
            ax.grid(axis='x', color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

        ax.set_title('Gastos Totais por Categoria', color=COR_TEXTO, fontsize=16, pad=20)
        fig.tight_layout()
        canvas.draw()

    def limpar_filtros():
        cal_inicio.set_date(None); cal_inicio.delete(0, "end")
        cal_fim.set_date(None); cal_fim.delete(0, "end")
        atualizar_grafico()

    ttk.Button(frame_filtros, text="Filtrar", command=atualizar_grafico).pack(side='left', padx=(20, 5))
    ttk.Button(frame_filtros, text="Limpar Filtro", command=limpar_filtros).pack(side='left', padx=5)

    # Carrega o gráfico com todos os dados na primeira vez
    atualizar_grafico()
    
def preencher_dashboard():
    user_id = usuario_logado['id']
    for widget in frame_principal.winfo_children():
        if widget != label_bem_vindo: widget.destroy()

    resumo = db_manager.obter_resumo_mensal(user_id)
    frame_resumo = tk.Frame(frame_principal, bg=COR_SECUNDARIA); frame_resumo.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
    tk.Label(frame_resumo, text="Resumo do Mês", font=FONTE_SALDO, fg=COR_TEXTO, bg=COR_SECUNDARIA).pack(pady=(10,5))
    entradas_str = f"R$ {resumo['entradas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    tk.Label(frame_resumo, text=f"Entradas: {entradas_str}", font=FONTE, fg="#2ecc71", bg=COR_SECUNDARIA).pack(pady=2)
    saidas_str = f"R$ {resumo['saidas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    tk.Label(frame_resumo, text=f"Saídas: {saidas_str}", font=FONTE, fg="#e74c3c", bg=COR_SECUNDARIA).pack(pady=(2,10))

    saldo_atual = db_manager.obter_saldo(user_id)
    frame_saldo = tk.Frame(frame_principal, bg=COR_SECUNDARIA); frame_saldo.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
    tk.Label(frame_saldo, text="Saldo Atual", font=FONTE_SALDO, fg=COR_TEXTO, bg=COR_SECUNDARIA).pack(pady=(10,5))
    saldo_str = f"R$ {saldo_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    tk.Label(frame_saldo, text=saldo_str, font=FONTE_SALDO, fg="#00cec9", bg=COR_SECUNDARIA).pack(pady=(2,10))

    top_categorias = db_manager.obter_top_categorias(user_id)
    frame_grafico = tk.Frame(frame_principal, bg=COR_SECUNDARIA); frame_grafico.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
    tk.Label(frame_grafico, text="Top Despesas do Mês", font=FONTE_SALDO, fg=COR_TEXTO, bg=COR_SECUNDARIA).pack(pady=10)
    if top_categorias:
        fig = Figure(figsize=(5, 3), dpi=80, facecolor=COR_SECUNDARIA); ax = fig.add_subplot(111); ax.set_facecolor(COR_SECUNDARIA)
        labels = [item['categoria'] for item in top_categorias]; sizes = [item['total'] for item in top_categorias]
        labels.reverse(); sizes.reverse()
        ax.barh(labels, sizes, color=COR_BOTAO, height=0.5)
        ax.tick_params(axis='x', colors=COR_TEXTO); ax.tick_params(axis='y', colors=COR_TEXTO)
        ax.spines['bottom'].set_color(COR_TEXTO); ax.spines['left'].set_color(COR_TEXTO); ax.spines['top'].set_color(COR_SECUNDARIA); ax.spines['right'].set_color(COR_SECUNDARIA)
        fig.tight_layout(pad=0.5)
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico); canvas.draw(); canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1, padx=10, pady=5)
    else:
        tk.Label(frame_grafico, text="Nenhuma despesa no mês.", font=FONTE, fg=COR_TEXTO, bg=COR_SECUNDARIA).pack(expand=True)

    ultimas_transacoes = db_manager.obter_ultimas_transacoes(user_id)
    frame_ultimas = tk.Frame(frame_principal, bg=COR_SECUNDARIA); frame_ultimas.grid(row=2, column=1, padx=20, pady=10, sticky="nsew")
    tk.Label(frame_ultimas, text="Últimas Transações", font=FONTE_SALDO, fg=COR_TEXTO, bg=COR_SECUNDARIA).pack(pady=10)
    style_tree = ttk.Style(); style_tree.configure("Dashboard.Treeview", background=COR_SECUNDARIA, foreground=COR_TEXTO, rowheight=25, fieldbackground=COR_SECUNDARIA, font=FONTE)
    style_tree.map('Dashboard.Treeview', background=[('selected', COR_BOTAO)]); style_tree.configure("Dashboard.Treeview.Heading", font=("Segoe UI", 10, "bold"))
    tree = ttk.Treeview(frame_ultimas, columns=('data', 'tipo', 'valor'), show='headings', style="Dashboard.Treeview", height=5)
    tree.heading('data', text='Data'); tree.heading('tipo', text='Tipo'); tree.heading('valor', text='Valor')
    tree.column('data', width=100, anchor='center'); tree.column('tipo', width=100, anchor='center'); tree.column('valor', width=120, anchor='e')
    for t in ultimas_transacoes:
        valor_f = f"R$ {t['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        tag = 'deposito' if t['tipo'] == 'deposito' else 'saque'
        tree.insert('', 'end', values=(t['data'], t['tipo'].capitalize(), valor_f), tags=(tag,))
    tree.tag_configure('deposito', foreground='#2ecc71'); tree.tag_configure('saque', foreground='#e74c3c')
    tree.pack(fill='x', expand=True, padx=10, pady=5)

    frame_acoes = tk.Frame(frame_principal, bg=COR_PRINCIPAL); frame_acoes.grid(row=3, column=0, columnspan=2, pady=20)
    ttk.Button(frame_acoes, text="Nova Transação", command=abrir_janela_transacao).pack(side='left', padx=10)
    ttk.Button(frame_acoes, text="Transferir", command=abrir_janela_transferencia).pack(side='left', padx=10)
    ttk.Button(frame_acoes, text="Histórico Completo", command=mostrar_historico).pack(side='left', padx=10)
    ttk.Button(frame_acoes, text="Relatórios", command=abrir_janela_relatorio).pack(side='left', padx=10)
    ttk.Button(frame_acoes, text="Sair", command=fazer_logout).pack(side='left', padx=10)

def mostrar_frame(frame_para_mostrar):
    frame_login.pack_forget()
    frame_cadastro.pack_forget()
    frame_principal.pack_forget()
    frame_para_mostrar.pack(fill="both", expand=True)

# =================================================================
# 3. CRIAÇÃO DA INTERFACE GRÁFICA (JANELA E FRAMES)
# =================================================================

janela = tk.Tk()
janela.title("FinancialManager")
janela.geometry("1000x700")
janela.configure(bg=COR_PRINCIPAL)
# janela.iconphoto(False, tk.PhotoImage(file="icon_bank.png"))

style = ttk.Style(janela)
style.theme_use("default")
style.configure("TButton", background=COR_BOTAO, foreground=COR_TEXTO, font=("Segoe UI", 12, "bold"), padding=10, borderwidth=0)
style.map("TButton", background=[('active', '#00a37e')], relief=[('pressed', 'sunken')])

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

frame_principal = tk.Frame(janela, bg=COR_PRINCIPAL)
frame_principal.grid_columnconfigure(0, weight=1)
frame_principal.grid_columnconfigure(1, weight=1)
frame_principal.grid_rowconfigure(2, weight=1)

label_bem_vindo = tk.Label(frame_principal, text="", font=FONTE_TITULO, fg=COR_TEXTO, bg=COR_PRINCIPAL, anchor="w")
label_bem_vindo.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

# =================================================================
# 4. INICIALIZAÇÃO DA APLICAÇÃO
# =================================================================
db_manager.inicializar_banco() 
mostrar_frame(frame_login)
janela.mainloop()