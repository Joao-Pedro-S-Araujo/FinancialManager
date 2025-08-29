import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# --- Configurações de Conexão ---
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def criar_conexao():
    """Cria e retorna uma conexão com o banco de dados."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# --- Funções de Gerenciamento de Banco ---

def inicializar_banco():
    """Cria as tabelas se elas não existirem."""
    conn = criar_conexao()
    if conn is None:
        return
        
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT PRIMARY KEY AUTO_INCREMENT,
                email VARCHAR(255) NOT NULL UNIQUE,
                senha_hash VARCHAR(255) NOT NULL,
                saldo DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INT PRIMARY KEY AUTO_INCREMENT,
                usuario_id INT NOT NULL,
                tipo ENUM('deposito', 'saque') NOT NULL,
                valor DECIMAL(10, 2) NOT NULL,
                data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
    except Error as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        cursor.close()
        conn.close()

# --- Funções de Usuário ---

def adicionar_usuario(email, senha_hash):
    """Adiciona um novo usuário ao banco de dados."""
    conn = criar_conexao()
    if conn is None: return False
    
    cursor = conn.cursor()
    try:
        query = "INSERT INTO usuarios (email, senha_hash) VALUES (%s, %s)"
        cursor.execute(query, (email, senha_hash))
        conn.commit()
        return True
    except Error as e:
        print(f"Erro ao adicionar usuário: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def buscar_usuario_por_email(email):
    """Busca um usuário pelo email e retorna seus dados."""
    conn = criar_conexao()
    if conn is None: return None
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM usuarios WHERE email = %s"
        cursor.execute(query, (email,))
        usuario = cursor.fetchone()
        return usuario
    except Error as e:
        print(f"Erro ao buscar usuário: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# --- Funções Financeiras ---

def registrar_transacao(usuario_id, tipo, valor):
    """Registra uma transação e atualiza o saldo do usuário de forma atômica."""
    conn = criar_conexao()
    if conn is None: return False
    
    cursor = conn.cursor()
    try:
        conn.start_transaction()

        query_transacao = "INSERT INTO transacoes (usuario_id, tipo, valor) VALUES (%s, %s, %s)"
        cursor.execute(query_transacao, (usuario_id, tipo, valor))
        
        sinal = "+" if tipo == 'deposito' else "-"
        query_saldo = f"UPDATE usuarios SET saldo = saldo {sinal} %s WHERE id = %s"
        cursor.execute(query_saldo, (valor, usuario_id))
        
        conn.commit()
        return True
    except Error as e:
        print(f"Erro ao registrar transação: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def obter_saldo(usuario_id):
    """Obtém o saldo atual de um usuário."""
    conn = criar_conexao()
    if conn is None: return 0.0
    
    cursor = conn.cursor()
    try:
        query = "SELECT saldo FROM usuarios WHERE id = %s"
        cursor.execute(query, (usuario_id,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else 0.0
    except Error as e:
        print(f"Erro ao obter saldo: {e}")
        return 0.0
    finally:
        cursor.close()
        conn.close()

def obter_historico(usuario_id):
    """Retorna o histórico de transações de um usuário."""
    conn = criar_conexao()
    if conn is None: 
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                tipo, 
                valor, 
                data_transacao
            FROM 
                transacoes 
            WHERE 
                usuario_id = %s
            ORDER BY 
                data_transacao DESC
        """
        
        params = (usuario_id,)
        cursor.execute(query, params)
        historico_bruto = cursor.fetchall()

        # Formatar a data no Python para evitar erros de SQL.
        historico_formatado = []
        for transacao in historico_bruto:
            # Cria a chave 'data' com a data/hora formatada.
            transacao['data'] = transacao['data_transacao'].strftime('%d/%m/%Y %H:%M:%S')
            # Remove a chave original com o objeto datetime.
            del transacao['data_transacao']
            historico_formatado.append(transacao)
            
        return historico_formatado

    except Error as e:
        print(f"Erro ao obter histórico para o usuario_id: {usuario_id}")
        print(f"Detalhe do erro: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

