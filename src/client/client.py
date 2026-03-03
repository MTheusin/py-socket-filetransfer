# Importa a biblioteca para comunicação em rede
import socket
# Importa para verificar se o arquivo existe antes de tentar ler
import os
# Importa a biblioteca que fará a criptografia (Cipher)
from cryptography.fernet import Fernet

# --- CONFIGURAÇÕES DE DESTINO ---
# Endereço IP do Servidor (127.0.0.1 se estiver no mesmo PC)
HOST = '127.0.0.1'  
# A porta deve ser EXATAMENTE a mesma que o servidor está ouvindo
PORTA = 5001      
# A chave de criptografia deve ser IGUAL à do servidor
CHAVE_FIXA = b'uY7ByX6pW9j2Z8kL5mQ4nRtPvV1s3xAzC2bE4gH6jK8='

def enviar_arquivo(caminho_arquivo):
    # PASSO 1: Verificação de Segurança Local
    # Antes de abrir rede, checamos se o arquivo que queremos enviar existe no disco
    if not os.path.exists(caminho_arquivo):
        print(f"[X] Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return

    # PASSO 2: Configurar o "Cadeado" (Criptografia)
    # Criamos o motor de cifra usando a nossa chave de 32 bytes
    fernet = Fernet(CHAVE_FIXA)
    
    # PASSO 3: Criar o Socket do Cliente
    # AF_INET = IPv4 | SOCK_STREAM = TCP (Conexão confiável)
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # PASSO 4: Solicitar Conexão (Connect)
        # O cliente tenta "discar" para o IP e Porta do servidor.
        # Se o servidor não estiver rodando ou o firewall bloquear, o erro ocorre aqui.
        cliente.connect((HOST, PORTA))
        print(f"[*] Conectado ao servidor {HOST}:{PORTA}")

        # PASSO 5: Abrir o Arquivo para Leitura
        # 'rb' = Read Binary (Leitura Binária). Lemos os bytes puros do arquivo.
        with open(caminho_arquivo, "rb") as f:
            print(f"[*] Iniciando leitura e criptografia de: {caminho_arquivo}")
            
            # PASSO 6: Loop de Leitura e Envio
            while True:
                # Lemos o arquivo em pedaços (chunks) de 1KB (1024 bytes)
                # Isso evita gastar muita memória RAM em arquivos grandes
                dados_originais = f.read(1024)
                
                # Se não houver mais dados para ler, saímos do loop
                if not dados_originais:
                    break
                
                # PASSO 7: Aplicar a Criptografia (Cipher)
                # Transformamos o texto/binário original em uma "sopa de bytes" ilegível
                dados_criptografados = fernet.encrypt(dados_originais)
                
                # PASSO 8: Disparar na Rede (Send)
                # O comando send() joga os bytes criptografados no túnel TCP
                cliente.send(dados_criptografados)

        print("[V] Arquivo enviado com sucesso e totalmente protegido!")

    except Exception as e:
        # Captura erros como: Servidor Offline, Queda de Internet, etc.
        print(f"[X] Erro crítico na transmissão: {e}")
    
    finally:
        # PASSO 9: Desligar a Conexão (Close)
        # Avisa ao servidor que não há mais nada a enviar e libera os recursos do PC
        cliente.close()
        print("[*] Socket do cliente encerrado.")

if __name__ == "__main__":
    # Inicia o processo enviando um arquivo chamado 'teste.txt'
    enviar_arquivo("test.txt")