# Importa a biblioteca de rede (Socket)
import socket
# Importa ferramentas do Sistema Operacional (para caminhos de pasta)
import os
# Importa a ferramenta de criptografia simétrica (Cipher)
from cryptography.fernet import Fernet

# --- CONFIGURAÇÕES INICIAIS ---
# '127.0.0.1' para testes locais ou '0.0.0.0' para aceitar conexões externas
HOST = '127.0.0.1'  
# Porta lógica por onde os dados vão entrar (deve ser a mesma no cliente)
PORTA = 5001      
# Chave mestra: Deve ser EXATAMENTE igual à chave configurada no cliente
CHAVE_FIXA = b'uY7ByX6pW9j2Z8kL5mQ4nRtPvV1s3xAzC2bE4gH6jK8='

def iniciar_servidor():
    # PASSO 1: Preparar o "Tradutor" (Criptografia)
    # Criamos o objeto fernet que usará a chave fixa para abrir o cadeado dos dados
    fernet = Fernet(CHAVE_FIXA)
    
    # PASSO 2: Garantir o Diretório de Destino (Integrado com a pasta do Web App)
    # Definimos o caminho para a pasta 'teste' que está dentro da pasta 'app'
    diretorio_app = os.path.dirname(os.path.abspath(__file__))
    pasta_destino = os.path.join(diretorio_app, '..','app', 'teste')

    # Se a pasta dentro de 'app' não existir, o script a cria automaticamente
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"[*] Pasta de destino confirmada em: {pasta_destino}")
    
    # PASSO 3: Criar o "Aparelho Telefônico" (Socket)
    # AF_INET = IPv4 | SOCK_STREAM = TCP (Garante integridade e ordem dos dados)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permite reiniciar o servidor sem esperar o timeout da porta no SO
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # PASSO 4: Reservar a Porta no Sistema (Bind)
        # O sistema reserva a porta 5001 exclusivamente para este script
        servidor.bind((HOST, PORTA))
        
        # PASSO 5: Ficar em Modo de Espera (Listen)
        # O servidor aguarda conexões. O '5' é o tamanho da fila de espera
        servidor.listen(5)
        
        print(f"[*] Servidor Online em {HOST}:{PORTA}. Aguardando arquivos...")

        # PASSO 6: Loop de Serviço (Mantém o servidor sempre ligado)
        while True:
            try:
                # PASSO 7: Atender a Chamada (Accept)
                # O código pausa aqui até que um cliente se conecte
                conn, addr = servidor.accept()
                print(f"\n[+] Conexão aceita de: {addr}")

                # PASSO 8: Receber Metadados (Protocolo do Cliente)
                # Lê os primeiros 64 bytes para o nome e 16 bytes para o tamanho
                nome_arquivo = conn.recv(64).decode().strip()
                tamanho_total = int(conn.recv(16).decode().strip())
                
                # Define o caminho completo onde o arquivo será salvo (dentro de app/teste)
                caminho_final = os.path.join(pasta_destino, nome_arquivo)
                bytes_recebidos_total = 0

                # PASSO 9: Criar o Arquivo no Disco
                # 'wb' = Escrita Binária. Imprescindível para dados criptografados
                with open(caminho_final, "wb") as f:
                    print(f"[*] Recebendo '{nome_arquivo}'...")
                    
                    # PASSO 10: Loop de Recebimento (Streaming)
                    while bytes_recebidos_total < tamanho_total:
                        # Lemos pacotes de 4096 bytes para suportar o overhead da criptografia
                        dados_criptografados = conn.recv(4096)
                        
                        if not dados_criptografados:
                            break 
                        
                        try:
                            # PASSO 11: Descriptografar (Cipher)
                            # Remove a proteção dos bytes antes de salvar no arquivo
                            dados_limpos = fernet.decrypt(dados_criptografados)
                            
                            # PASSO 12: Salvar no HD
                            # Grava os dados originais no destino final
                            f.write(dados_limpos)
                            bytes_recebidos_total += len(dados_limpos)
                        except Exception as e:
                            print(f"[X] Falha na descriptografia: {e}")
                            break

                print(f"[V] Arquivo '{nome_arquivo}' salvo com sucesso em app/teste!")

            except Exception as e:
                print(f"[X] Erro na conexão atual: {e}")
            finally:
                # PASSO 13: Fechar Conexão Individual
                # Libera o cliente atual mas mantém o servidor rodando
                conn.close()

    except Exception as e:
        print(f"[X] Erro crítico no servidor: {e}")
    
    finally:
        # PASSO 14: Encerramento Geral
        # Fecha o socket principal ao encerrar o script
        servidor.close()
        print("[*] Servidor encerrado.")

if __name__ == "__main__":
    iniciar_servidor()