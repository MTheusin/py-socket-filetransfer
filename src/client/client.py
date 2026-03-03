# Importa a biblioteca para comunicação em rede
import socket
# Importa para verificar caminhos e existência de arquivos
import os
# Importa a biblioteca que fará a criptografia (Cipher)
from cryptography.fernet import Fernet

# --- CONFIGURAÇÕES DE DESTINO ---
# '127.0.0.1' ou 'localhost' para rodar tudo no mesmo computador, caso utilizar outra máquina apontar o ip 192.168.x.x
HOST = '127.0.0.1'  
# A porta deve ser EXATAMENTE a mesma que o servidor está ouvindo
PORTA = 5001      
# A chave de criptografia deve ser simétrica e igual à do servidor
CHAVE_FIXA = b'uY7ByX6pW9j2Z8kL5mQ4nRtPvV1s3xAzC2bE4gH6jK8='

def enviar_arquivo(caminho_arquivo):
    # --- CORREÇÃO DE CAMINHO ---
    # Traduz as barras invertidas do Windows para barras comuns reconhecidas pelo Python
    caminho_arquivo = caminho_arquivo.replace("\\", "/")
    # Transforma o caminho em um endereço absoluto
    caminho_arquivo = os.path.abspath(caminho_arquivo)

    # PASSO 1: Verificação de Segurança Local
    # Antes de abrir rede, checamos se o arquivo que queremos enviar existe no disco
    if not os.path.exists(caminho_arquivo):
        print(f"[X] Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return

    # PASSO 2: Configurar o "Cadeado" (Criptografia)
    # Criamos o motor de cifra usando a nossa chave de 32 bytes
    fernet = Fernet(CHAVE_FIXA)
    
    # Obtemos metadados para o protocolo do servidor
    nome_arquivo = os.path.basename(caminho_arquivo)
    tamanho_arquivo = os.path.getsize(caminho_arquivo)
    
    # PASSO 3: Criar o Socket do Cliente
    # AF_INET = IPv4 | SOCK_STREAM = TCP (Conexão confiável)
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # PASSO 4: Solicitar Conexão (Connect)
        # O cliente tenta "discar" para o IP e Porta do servidor (Localhost)
        cliente.connect((HOST, PORTA))
        print(f"[*] Conectado ao servidor local em {HOST}:{PORTA}")

        # ENVIO DE METADADOS (Protocolo estabelecido no server.py)
        # Envia nome (64 bytes) e tamanho (16 bytes) com preenchimento fixo
        cliente.send(nome_arquivo.ljust(64).encode())
        cliente.send(str(tamanho_arquivo).ljust(16).encode())

        # PASSO 5: Abrir o Arquivo para Leitura
        # 'rb' = Read Binary (Leitura Binária). Essencial para manter a integridade
        with open(caminho_arquivo, "rb") as f:
            print(f"[*] Lendo e enviando: {nome_arquivo} ({tamanho_arquivo} bytes)")
            
            # PASSO 6: Loop de Leitura e Envio
            while True:
                # Lemos o arquivo em pedaços (chunks) de 1024 bytes
                dados_originais = f.read(1024)
                
                # Se não houver mais dados, o arquivo acabou
                if not dados_originais:
                    break
                
                # PASSO 7: Aplicar a Criptografia (Cipher)
                # O bloco é cifrado antes de ser transmitido
                dados_criptografados = fernet.encrypt(dados_originais)
                
                # PASSO 8: Disparar na Rede (Send)
                # Envia o pacote cifrado pelo túnel TCP
                cliente.send(dados_criptografados)

        print("[V] Arquivo enviado com sucesso via Localhost!")

    except Exception as e:
        # Captura erros de conexão recusada ou falhas de rede local
        print(f"[X] Erro na transmissão: {e}")
    
    finally:
        # PASSO 9: Desligar a Conexão (Close)
        # Libera os recursos de rede do computador
        cliente.close()
        print("[*] Socket do cliente encerrado.")

if __name__ == "__main__":
    # O .strip remove aspas extras que o Windows coloca ao copiar o caminho
    path = input("Digite ou cole o caminho do arquivo: ").strip('"').strip("'")
    enviar_arquivo(path)