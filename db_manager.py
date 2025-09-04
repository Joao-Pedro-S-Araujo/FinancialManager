import sqlite3
import os
from datetime import datetime

# --- Configurações da Base de Dados ---
# O nome do ficheiro da base de dados. Ficará na mesma pasta do projeto.
DB_FILE = "financial_manager.db"

def criar_conexao():
    """Cria e retorna uma conexão com a base de dados SQLite."""
    try:
        conn = sqlite3.connect(DB_FILE)
        # Permite que os resultados venham como dicionários (muito útil)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao SQLite: {e}")
        return None

# =================================================================
# 1. FUNÇÕES DE GESTÃO DA BASE DE DADOS
# =================================================================

def inicializar_banco():
    """Cria todas as tabelas necessárias se elas não existirem."""
    conn = criar_conexao()
    if conn is None: return
    
    cursor = conn.cursor()
    try:
        # Habilita o suporte a chaves estrangeiras (importante para o ON DELETE CASCADE)
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                saldo REAL NOT NULL DEFAULT 0.00,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('deposito', 'saque')),
                valor REAL NOT NULL,
                categoria TEXT,
                data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orcamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                valor REAL NOT NULL,
                mes INTEGER NOT NULL,
                ano INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                UNIQUE (usuario_id, categoria, mes, ano)
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        conn.close()

# ... (O resto das funções será adaptado para a sintaxe do SQLite, usando '?' em vez de '%s')

# =================================================================
# 2. FUNÇÕES DE UTILIZADOR
# =================================================================

def adicionar_usuario(email, senha_hash):
    conn = criar_conexao()
    if conn is None: return False
    try:
        query = "INSERT INTO usuarios (email, senha_hash) VALUES (?, ?)"
        conn.execute(query, (email, senha_hash))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao adicionar utilizador: {e}")
        return False
    finally:
        if conn: conn.close()

def buscar_usuario_por_email(email):
    conn = criar_conexao()
    if conn is None: return None
    try:
        query = "SELECT * FROM usuarios WHERE email = ?"
        cursor = conn.execute(query, (email,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao buscar utilizador: {e}")
        return None
    finally:
        if conn: conn.close()

# ... (Restantes funções adaptadas)
def registrar_transacao(usuario_id, tipo, valor, categoria=None):
    conn = criar_conexao()
    if conn is None: return False
    try:
        conn.execute("BEGIN TRANSACTION")
        query_transacao = "INSERT INTO transacoes (usuario_id, tipo, valor, categoria) VALUES (?, ?, ?, ?)"
        conn.execute(query_transacao, (usuario_id, tipo, valor, categoria))
        sinal = "+" if tipo == 'deposito' else "-"
        query_saldo = f"UPDATE usuarios SET saldo = saldo {sinal} ? WHERE id = ?"
        conn.execute(query_saldo, (valor, usuario_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao registar transação: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def registrar_transferencia(id_remetente, email_destinatario, valor):
    conn = criar_conexao()
    if conn is None: return {'sucesso': False, 'mensagem': 'Não foi possível ligar à base de dados.'}
    try:
        conn.execute("BEGIN TRANSACTION")
        
        cursor_remetente = conn.execute("SELECT saldo FROM usuarios WHERE id = ?", (id_remetente,))
        saldo_remetente = cursor_remetente.fetchone()['saldo']
        if saldo_remetente < valor:
            conn.rollback()
            return {'sucesso': False, 'mensagem': 'Saldo insuficiente.'}

        cursor_dest = conn.execute("SELECT id FROM usuarios WHERE email = ?", (email_destinatario,))
        destinatario = cursor_dest.fetchone()
        if not destinatario:
            conn.rollback()
            return {'sucesso': False, 'mensagem': 'Email do destinatário não encontrado.'}
        id_destinatario = destinatario['id']
        
        if id_remetente == id_destinatario:
            conn.rollback()
            return {'sucesso': False, 'mensagem': 'Não pode transferir para si mesmo.'}

        conn.execute("UPDATE usuarios SET saldo = saldo - ? WHERE id = ?", (valor, id_remetente))
        conn.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (valor, id_destinatario))
        conn.execute("INSERT INTO transacoes (usuario_id, tipo, valor, categoria) VALUES (?, 'saque', ?, 'Transferência Enviada')", (id_remetente, valor))
        conn.execute("INSERT INTO transacoes (usuario_id, tipo, valor, categoria) VALUES (?, 'deposito', ?, 'Transferência Recebida')", (id_destinatario, valor))
        
        conn.commit()
        return {'sucesso': True, 'mensagem': 'Transferência realizada com sucesso!'}
    except sqlite3.Error as e:
        print(f"Erro na transferência: {e}")
        conn.rollback()
        return {'sucesso': False, 'mensagem': 'Ocorreu um erro interno. Tente novamente.'}
    finally:
        if conn: conn.close()

# ... (Restantes funções adaptadas para SQLite)

def obter_saldo(usuario_id):
    conn = criar_conexao()
    if conn is None: return 0.0
    try:
        cursor = conn.execute("SELECT saldo FROM usuarios WHERE id = ?", (usuario_id,))
        resultado = cursor.fetchone()
        return resultado['saldo'] if resultado else 0.0
    except sqlite3.Error as e:
        print(f"Erro ao obter saldo: {e}")
        return 0.0
    finally:
        if conn: conn.close()

def obter_historico(usuario_id, data_inicio=None, data_fim=None):
    conn = criar_conexao()
    if conn is None: return []
    try:
        query_base = "SELECT id, tipo, valor, categoria, data_transacao FROM transacoes WHERE usuario_id = ?"
        params = [usuario_id]
        if data_inicio:
            query_base += " AND DATE(data_transacao) >= ?"
            params.append(data_inicio)
        if data_fim:
            query_base += " AND DATE(data_transacao) <= ?"
            params.append(data_fim)
        query_base += " ORDER BY data_transacao DESC"
        
        cursor = conn.execute(query_base, tuple(params))
        historico_bruto = cursor.fetchall()

        historico_formatado = []
        for transacao_row in historico_bruto:
            transacao_dict = dict(transacao_row)
            # SQLite devolve strings de data, precisamos de converter para objeto datetime
            dt_obj = datetime.strptime(transacao_dict['data_transacao'], '%Y-%m-%d %H:%M:%S')
            transacao_dict['data'] = dt_obj.strftime('%d/%m/%Y %H:%M:%S')
            del transacao_dict['data_transacao']
            historico_formatado.append(transacao_dict)
            
        return historico_formatado
    except sqlite3.Error as e:
        print(f"Erro ao obter histórico: {e}")
        return []
    finally:
        if conn: conn.close()

def obter_gastos_por_categoria(usuario_id, data_inicio=None, data_fim=None):
    conn = criar_conexao()
    if conn is None: return []
    try:
        params = [usuario_id]
        query = "SELECT categoria, SUM(valor) as total FROM transacoes WHERE usuario_id = ? AND tipo = 'saque' AND categoria IS NOT NULL"
        if data_inicio:
            query += " AND DATE(data_transacao) >= ?"
            params.append(data_inicio)
        if data_fim:
            query += " AND DATE(data_transacao) <= ?"
            params.append(data_fim)
        query += " GROUP BY categoria HAVING total > 0 ORDER BY total DESC"
        cursor = conn.execute(query, tuple(params))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao obter gastos por categoria: {e}")
        return []
    finally:
        if conn: conn.close()

def obter_resumo_mensal(usuario_id):
    conn = criar_conexao()
    if conn is None: return {'entradas': 0, 'saidas': 0}
    try:
        # Funções de data do SQLite são diferentes
        query = """
            SELECT
                SUM(CASE WHEN tipo = 'deposito' THEN valor ELSE 0 END) as total_entradas,
                SUM(CASE WHEN tipo = 'saque' THEN valor ELSE 0 END) as total_saidas
            FROM transacoes
            WHERE
                usuario_id = ? AND
                strftime('%Y-%m', data_transacao) = strftime('%Y-%m', 'now', 'localtime')
        """
        cursor = conn.execute(query, (usuario_id,))
        resultado = cursor.fetchone()
        entradas = resultado['total_entradas'] if resultado['total_entradas'] else 0
        saidas = resultado['total_saidas'] if resultado['total_saidas'] else 0
        return {'entradas': entradas, 'saidas': saidas}
    except sqlite3.Error as e:
        print(f"Erro ao obter resumo mensal: {e}")
        return {'entradas': 0, 'saidas': 0}
    finally:
        if conn: conn.close()

def obter_top_categorias(usuario_id, limite=5):
    conn = criar_conexao()
    if conn is None: return []
    try:
        query = """
            SELECT categoria, SUM(valor) as total
            FROM transacoes
            WHERE usuario_id = ? AND tipo = 'saque' AND categoria IS NOT NULL
              AND strftime('%Y-%m', data_transacao) = strftime('%Y-%m', 'now', 'localtime')
            GROUP BY categoria ORDER BY total DESC LIMIT ?
        """
        cursor = conn.execute(query, (usuario_id, limite))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao obter top categorias: {e}")
        return []
    finally:
        if conn: conn.close()

def obter_ultimas_transacoes(usuario_id, limite=4):
    conn = criar_conexao()
    if conn is None: return []
    try:
        query = "SELECT tipo, valor, categoria, data_transacao FROM transacoes WHERE usuario_id = ? ORDER BY data_transacao DESC LIMIT ?"
        cursor = conn.execute(query, (usuario_id, limite))
        historico_bruto = cursor.fetchall()

        historico_formatado = []
        for transacao_row in historico_bruto:
            transacao_dict = dict(transacao_row)
            dt_obj = datetime.strptime(transacao_dict['data_transacao'], '%Y-%m-%d %H:%M:%S')
            transacao_dict['data'] = dt_obj.strftime('%d/%m/%Y')
            del transacao_dict['data_transacao']
            historico_formatado.append(transacao_dict)
        return historico_formatado
    except sqlite3.Error as e:
        print(f"Erro ao obter últimas transações: {e}")
        return []
    finally:
        if conn: conn.close()

def obter_transacao_por_id(transacao_id):
    conn = criar_conexao()
    if conn is None: return None
    try:
        cursor = conn.execute("SELECT * FROM transacoes WHERE id = ?", (transacao_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao buscar transação por ID: {e}")
        return None
    finally:
        if conn: conn.close()

def excluir_transacao(transacao_id, usuario_id):
    conn = criar_conexao()
    if conn is None: return False
    try:
        conn.execute("BEGIN TRANSACTION")
        transacao = obter_transacao_por_id(transacao_id)
        if not transacao:
            conn.rollback()
            return False
        valor = transacao['valor']
        tipo = transacao['tipo']
        sinal_ajuste = "+" if tipo == 'saque' else "-"
        query_saldo = f"UPDATE usuarios SET saldo = saldo {sinal_ajuste} ? WHERE id = ?"
        conn.execute(query_saldo, (valor, usuario_id))
        conn.execute("DELETE FROM transacoes WHERE id = ?", (transacao_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao excluir transação: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def editar_transacao(transacao_id, usuario_id, novo_valor, nova_categoria):
    conn = criar_conexao()
    if conn is None: return {'sucesso': False}
    try:
        conn.execute("BEGIN TRANSACTION")
        transacao_original = obter_transacao_por_id(transacao_id)
        if not transacao_original:
            conn.rollback()
            return {'sucesso': False}
        valor_original = transacao_original['valor']
        diferenca = valor_original - novo_valor
        query_saldo = "UPDATE usuarios SET saldo = saldo + ? WHERE id = ?"
        conn.execute(query_saldo, (diferenca, usuario_id))
        query_update = "UPDATE transacoes SET valor = ?, categoria = ? WHERE id = ?"
        conn.execute(query_update, (novo_valor, nova_categoria, transacao_id))
        conn.commit()
        return {'sucesso': True}
    except sqlite3.Error as e:
        print(f"Erro ao editar transação: {e}")
        conn.rollback()
        return {'sucesso': False}
    finally:
        if conn: conn.close()

def definir_ou_atualizar_orcamento(usuario_id, categoria, valor, mes, ano):
    conn = criar_conexao()
    if conn is None: return False
    try:
        # SQLite usa a sintaxe INSERT ... ON CONFLICT ... DO UPDATE
        query = """
            INSERT INTO orcamentos (usuario_id, categoria, valor, mes, ano)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(usuario_id, categoria, mes, ano) DO UPDATE SET valor=excluded.valor
        """
        conn.execute(query, (usuario_id, categoria, valor, mes, ano))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao definir orçamento: {e}")
        return False
    finally:
        if conn: conn.close()

def obter_orcamentos_do_mes(usuario_id, mes, ano):
    conn = criar_conexao()
    if conn is None: return []
    try:
        query = "SELECT categoria, valor FROM orcamentos WHERE usuario_id = ? AND mes = ? AND ano = ?"
        cursor = conn.execute(query, (usuario_id, mes, ano))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao obter orçamentos: {e}")
        return []
    finally:
        if conn: conn.close()

def obter_gastos_vs_orcamentos(usuario_id, mes, ano):
    conn = criar_conexao()
    if conn is None: return []
    try:
        query = """
            SELECT
                o.categoria, o.valor as orcamento, COALESCE(SUM(t.valor), 0) as gasto
            FROM orcamentos o
            LEFT JOIN transacoes t ON o.usuario_id = t.usuario_id
                            AND o.categoria = t.categoria
                            AND t.tipo = 'saque'
                            AND CAST(strftime('%m', t.data_transacao) as integer) = o.mes
                            AND CAST(strftime('%Y', t.data_transacao) as integer) = o.ano
            WHERE o.usuario_id = ? AND o.mes = ? AND o.ano = ?
            GROUP BY o.categoria, o.valor ORDER BY o.categoria
        """
        cursor = conn.execute(query, (usuario_id, mes, ano))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao comparar gastos vs orçamentos: {e}")
        return []
    finally:
        if conn: conn.close()

def excluir_orcamento(usuario_id, categoria, mes, ano):
    conn = criar_conexao()
    if conn is None: return False
    try:
        query = "DELETE FROM orcamentos WHERE usuario_id = ? AND categoria = ? AND mes = ? AND ano = ?"
        conn.execute(query, (usuario_id, categoria, mes, ano))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao excluir orçamento: {e}")
        return False
    finally:
        if conn: conn.close()

