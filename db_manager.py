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

def registrar_transacao(usuario_id, tipo, valor, categoria=None):
    """Registra uma transação e atualiza o saldo do usuário de forma atômica."""
    conn = criar_conexao()
    if conn is None: return False
    
    cursor = conn.cursor()
    try:
        conn.start_transaction()

        # Query atualizada para incluir a categoria
        query_transacao = "INSERT INTO transacoes (usuario_id, tipo, valor, categoria) VALUES (%s, %s, %s, %s)"
        cursor.execute(query_transacao, (usuario_id, tipo, valor, categoria))
        
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

def registrar_transferencia(id_remetente, email_destinatario, valor):
    """
    Registra uma transferência entre dois usuários de forma atômica.
    Garante que a operação completa (saque, depósito, registros) ocorra com sucesso.
    """
    conn = criar_conexao()
    if conn is None: return {'sucesso': False, 'mensagem': 'Não foi possível conectar ao banco de dados.'}

    cursor = conn.cursor(dictionary=True) # dictionary=True é útil para pegar o id

    try:
        # 1. Iniciar a transação atômica
        conn.start_transaction()

        # 2. Verificar se o remetente tem saldo suficiente
        cursor.execute("SELECT saldo FROM usuarios WHERE id = %s FOR UPDATE", (id_remetente,)) # FOR UPDATE bloqueia a linha
        saldo_remetente = cursor.fetchone()['saldo']
        if saldo_remetente < valor:
            conn.rollback()
            return {'sucesso': False, 'mensagem': 'Saldo insuficiente.'}

        # 3. Verificar se o destinatário existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email_destinatario,))
        destinatario = cursor.fetchone()
        if not destinatario:
            conn.rollback()
            return {'sucesso': False, 'mensagem': 'Email do destinatário não encontrado.'}
        id_destinatario = destinatario['id']
        
        # 4. Evitar que o usuário transfira para si mesmo
        if id_remetente == id_destinatario:
            conn.rollback()
            return {'sucesso': False, 'mensagem': 'Você não pode transferir para si mesmo.'}

        # 5. Debitar o valor do remetente
        cursor.execute("UPDATE usuarios SET saldo = saldo - %s WHERE id = %s", (valor, id_remetente))

        # 6. Creditar o valor para o destinatário
        cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE id = %s", (valor, id_destinatario))
        
        # 7. Registrar a transação de 'saque' para o remetente
        # Podemos adicionar um novo tipo ENUM 'transferencia' no DB ou tratar como saque/deposito
        # Por simplicidade, vamos registrar como 'saque' por transferência.
        # Uma melhoria seria: ALTER TABLE transacoes MODIFY tipo ENUM('deposito', 'saque', 'transferencia_enviada', 'transferencia_recebida');
        cursor.execute("INSERT INTO transacoes (usuario_id, tipo, valor) VALUES (%s, 'saque', %s)", (id_remetente, valor))
        
        # 8. Registrar a transação de 'deposito' para o destinatário
        cursor.execute("INSERT INTO transacoes (usuario_id, tipo, valor) VALUES (%s, 'deposito', %s)", (id_destinatario, valor))

        # 9. Se tudo deu certo, confirmar as alterações
        conn.commit()
        return {'sucesso': True, 'mensagem': 'Transferência realizada com sucesso!'}

    except Error as e:
        print(f"Erro na transferência: {e}")
        conn.rollback() # Desfaz tudo se qualquer passo falhar
        return {'sucesso': False, 'mensagem': 'Ocorreu um erro interno. Tente novamente.'}
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
                categoria,
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

