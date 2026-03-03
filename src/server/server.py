# --- IMPORTAÇÕES ---
import socket  # Biblioteca nativa para comunicação de rede (abrir o "cano" de dados)
import os      # Biblioteca para manipular pastas e caminhos de arquivos no sistema
from Crypto.Cipher import AES # Motor de criptografia profissional (mais leve que o Fernet)
from tqdm import tqdm         # Biblioteca que gera a barra de progresso visual no terminal

# --- CONFIGURAÇÕES DE REDE ---
HOST = '0.0.0.0'  # Escuta em todas as placas de rede (Ethernet, Wi-Fi, Localhost)
PORTA = 5001      # O "canal" específico por onde os dados entrarão
CHAVE_AES = b'uY7ByX6pW9j2Z8kL'  # Chave secreta de 16 bytes (o "segredo" compartilhado)
NONCE = b'12345678'             # Número especial para o modo CTR (deve ser igual no cliente)

def iniciar_servidor():
    # --- PASSO 1: LOCALIZAR A PASTA DE DESTINO ---
    # Pegamos o caminho onde este script está (pasta /server)
    diretorio_do_script = os.path.dirname(os.path.abspath(__file__))
    # Navegamos: subimos um nível (..) para /src e entramos em /app/teste
    # É aqui que o Web App buscará os arquivos para download
    pasta_destino = os.path.abspath(os.path.join(diretorio_do_script, '..', 'app', 'teste'))
    
    # Se a pasta não existir (ex: primeira vez rodando), nós a criamos
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    # --- PASSO 2: CONFIGURAR O SOCKET (REDE) ---
    # Criamos o objeto de rede usando IPv4 (AF_INET) e TCP (SOCK_STREAM)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permite reiniciar o script sem que o Windows bloqueie a porta por "estar em uso"
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Vincula o script ao IP e à Porta configurados
    servidor.bind((HOST, PORTA))
    # Coloca o servidor em modo de espera (aguardando o cliente "discar")
    servidor.listen(5)
    
    print(f"[*] SERVIDOR ONLINE | Salvando em: {pasta_destino}")

    # Loop infinito: após receber um arquivo, ele volta a esperar o próximo
    while True:
        # accept() para o código aqui e só libera quando um cliente conecta
        conn, addr = servidor.accept()
        print(f"\n[+] Conexão vinda de: {addr}")

        try:
            # --- PASSO 3: PROTOCOLO DE METADADOS ---
            # Recebemos primeiro o nome do arquivo (limite de 64 caracteres)
            nome_arquivo = conn.recv(64).decode().strip()
            # Depois recebemos o tamanho total do arquivo (limite de 16 caracteres)
            tamanho_total = int(conn.recv(16).decode().strip())
            
            caminho_final = os.path.join(pasta_destino, nome_arquivo)
            
            # --- PASSO 4: CONFIGURAR DESCRIPTOGRAFIA ---
            # Criamos o "descriptografador" AES no modo CTR (melhor para arquivos grandes)
            cipher = AES.new(CHAVE_AES, AES.MODE_CTR, nonce=NONCE)

            # --- PASSO 5: RECEBIMENTO COM BARRA DE PROGRESSO ---
            # tqdm cria a barra visual. unit='B' mostra o progresso em Bytes/Megabytes
            with tqdm(total=tamanho_total, unit='B', unit_scale=True, desc=f"Recebendo {nome_arquivo}") as pbar:
                # Abrimos o arquivo no modo 'wb' (Escrita Binária)
                with open(caminho_final, "wb") as f:
                    bytes_recebidos = 0
                    while bytes_recebidos < tamanho_total:
                        # Lemos blocos de 64KB (65536 bytes) por vez para não travar a rede
                        pacote = conn.recv(65536)
                        if not pacote: break
                        
                        # Descriptografamos o bloco e escrevemos direto no HD
                        #print(pacote) #Exibe os pacote criptografados
                        dados_limpos = cipher.decrypt(pacote)
                        f.write(dados_limpos)
                        
                        # Atualizamos o contador e a barra visual
                        bytes_recebidos += len(pacote)
                        pbar.update(len(pacote))

            print(f"[V] Arquivo '{nome_arquivo}' finalizado com sucesso!")
        
        except Exception as e:
            print(f"[X] Erro durante a recepção: {e}")
        finally:
            # Fecha a conexão com este cliente específico, mas mantém o servidor ligado
            conn.close()

if __name__ == "__main__":
    iniciar_servidor()