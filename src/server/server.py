# Importa a biblioteca de rede (Socket)
import socket
# Importa ferramentas do Sistema Operacional (para caminhos de pasta)
import os
# Importa a ferramenta de criptografia simétrica
from cryptography.fernet import Fernet

# --- CONFIGURAÇÕES INICIAIS ---
# '0.0.0.0' diz ao Windows/Linux: "Aceite conexões de qualquer placa de rede deste PC"
HOST = '0.0.0.0'  
# Porta lógica (canal) por onde os dados vão entrar (deve ser > 1024)
PORTA = 5001      
# Chave mestra: Se o cliente não tiver EXATAMENTE esta chave, o arquivo será lixo eletrônico
CHAVE_FIXA = b'uY7ByX6pW9j2Z8kL5mQ4nRtPvV1s3xAzC2bE4gH6jK8='

def iniciar_servidor():
    # PASSO 1: Preparar o "Tradutor" (Criptografia)
    # Criamos o objeto fernet que usará a chave fixa para abrir o cadeado dos dados
    fernet = Fernet(CHAVE_FIXA)
    
    # PASSO 2: Criar o "Aparelho Telefônico" (Socket)
    # AF_INET = Endereçamento IPv4
    # SOCK_STREAM = Protocolo TCP (Garante que os dados cheguem na ordem certa e sem erros)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # PASSO 3: Reservar a Porta no Sistema (Bind)
        # O SO "tranca" a porta 5001 para o uso exclusivo deste script
        servidor.bind((HOST, PORTA))
        
        # PASSO 4: Ficar em Modo de Espera (Listen)
        # O servidor entra em "modo de escuta", aguardando o sinal do cliente
        servidor.listen(1)
        
        print(f"[*] Servidor Online. Aguardando sinal do cliente...")

        # PASSO 5: Atender a Chamada (Accept)
        # O código PARA aqui e só continua quando alguém tenta conectar.
        # 'conn' é o canal exclusivo com esse cliente, 'addr' é o IP de quem ligou.
        conn, addr = servidor.accept()
        print(f"[+] Conexão aceita de: {addr}")

        # PASSO 6: Criar o Arquivo no Disco
        # 'wb' = Write Binary (Escrita Binária). Essencial para arquivos criptografados.
        with open("arquivo_recebido.txt", "wb") as f:
            
            # PASSO 7: Loop de Recebimento (Streaming)
            while True:
                # O servidor tenta ler 4096 bytes vindos da rede
                dados_criptografados = conn.recv(4096)
                
                # Se não chegar nada, significa que o cliente terminou o envio e fechou
                if not dados_criptografados:
                    break 
                
                try:
                    # PASSO 8: Descriptografar (Cipher)
                    # O Fernet verifica a assinatura e remove a camada de proteção
                    dados_limpos = fernet.decrypt(dados_criptografados)
                    
                    # PASSO 9: Salvar no HD
                    # Escreve os dados originais no arquivo 'arquivo_recebido.txt'
                    f.write(dados_limpos)
                except Exception:
                    print("[X] Erro: A chave de criptografia não bate com a do cliente!")
                    break

        print("[V] Arquivo recebido e descriptografado com sucesso!")

    except Exception as e:
        print(f"[X] Ocorreu um erro técnico: {e}")
    
    finally:
        # PASSO 10: Limpeza e Encerramento (Close)
        # Fecha a conexão com o cliente específico
        if 'conn' in locals(): conn.close()
        # Fecha o servidor e libera a porta 5001 para outros programas
        servidor.close()
        print("[*] Socket encerrado e porta liberada.")

if __name__ == "__main__":
    iniciar_servidor()