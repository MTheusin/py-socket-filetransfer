import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)
# Define o caminho para a pasta 'teste' que o servidor de socket alimenta
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'teste')

def formatar_tamanho(tamanho_bytes):
    """Converte bytes para KB, MB, GB de forma legível."""
    for unidade in ['B', 'KB', 'MB', 'GB']:
        if tamanho_bytes < 1024.0:
            return f"{tamanho_bytes:.2f} {unidade}"
        tamanho_bytes /= 1024.0
    return f"{tamanho_bytes:.2f} TB"

@app.route('/')
def index():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    lista_arquivos = []
    for nome in os.listdir(UPLOAD_FOLDER):
        caminho = os.path.join(UPLOAD_FOLDER, nome)
        # os.path.getsize obtém o tamanho real do arquivo para o usuário
        tamanho = formatar_tamanho(os.path.getsize(caminho))
        
        lista_arquivos.append({
            'nome': nome,
            'tamanho': tamanho
        })
    
    return render_template('index.html', arquivos=lista_arquivos)

@app.route('/download/<nome_arquivo>')
def baixar_arquivo(nome_arquivo):
    return send_from_directory(UPLOAD_FOLDER, nome_arquivo, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)