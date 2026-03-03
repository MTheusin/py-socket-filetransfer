# --- IMPORTAÇÕES ---
import socket
import os
from Crypto.Cipher import AES
from tqdm import tqdm

# --- CONFIGURAÇÕES DE DESTINO ---
# Troque pelo IP da sua VM no VMware quando for testar na rede
HOST = '172.20.10.9' 
PORTA = 5001
CHAVE_AES = b'uY7ByX6pW9j2Z8kL' # Deve ser IGUAL à do servidor
NONCE = b'12345678'             # Deve ser IGUAL à do servidor

def enviar_arquivo(caminho_local):
    # --- PASSO 1: TRATAR O CAMINHO DO ARQUIVO ---
    # Remove aspas e troca \ por / para o Python não se confundir
    caminho_local = caminho_local.replace("\\", "/").strip('"').strip("'")
    
    if not os.path.exists(caminho_local):
        print("[X] Erro: Arquivo não encontrado!")
        return

    # Pegamos informações básicas do arquivo
    tamanho_arq = os.path.getsize(caminho_local)
    nome_arq = os.path.basename(caminho_local)

    # --- PASSO 2: PREPARAR O SOCKET E A CRIPTOGRAFIA ---
    # Criamos o criptografador AES (Modo CTR: rápido e eficiente)
    cipher = AES.new(CHAVE_AES, AES.MODE_CTR, nonce=NONCE)
    # Criamos o socket de conexão
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Tentamos conectar ao servidor
        s.connect((HOST, PORTA))
        
        # --- PASSO 3: ENVIAR METADADOS (O "CONTRATO") ---
        # Enviamos o nome (preenchendo até 64 espaços)
        s.send(nome_arq.ljust(64).encode())
        # Enviamos o tamanho (preenchendo até 16 espaços)
        s.send(str(tamanho_arq).ljust(16).encode())

        # --- PASSO 4: ENVIAR O ARQUIVO EM FLUXO (STREAMING) ---
        # tqdm mostra a velocidade de upload e o tempo restante (ETA)
        with tqdm(total=tamanho_arq, unit='B', unit_scale=True, desc=f"Enviando {nome_arq}") as pbar:
            # Abrimos o arquivo original para leitura binária ('rb')
            with open(caminho_local, "rb") as f:
                while True:
                    # Lemos um pedaço de 64KB do arquivo
                    bloco = f.read(64000)
                    if not bloco: break # Se o arquivo acabou, sai do loop
                    
                    # Criptografamos esse pedaço específico
                    dados_protegidos = cipher.encrypt(bloco)
                    
                    # Enviamos para o servidor. 
                    # sendall() garante que o Windows envie todo o bloco, sem perdas.
                    s.sendall(dados_protegidos)
                    
                    # Atualiza a barra de progresso no terminal
                    pbar.update(len(bloco))

        print("\n[V] Envio concluído com sucesso!")
        
    except Exception as e:
        print(f"\n[X] Erro na conexão: {e}")
    finally:
        # Fecha a conexão após o término ou erro
        s.close()

if __name__ == "__main__":
    # Pede o caminho do arquivo para o usuário
    caminho = input("Cole o caminho do arquivo (ex: C:/backup.zip): ")
    enviar_arquivo(caminho)