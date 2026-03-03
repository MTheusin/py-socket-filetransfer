import os
from flask import Flask, render_template, send_from_directory, abort

app = Flask(__name__)

# Define o caminho da pasta de arquivos relativo ao local do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'teste')

@app.route('/')
def listar_arquivos():
    if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
    arquivos = os.listdir(UPLOAD_FOLDER)
    # Renderiza a lista de arquivos para o index.html
    return render_template('index.html', arquivos=arquivos)

@app.route('/download/<nome_arquivo>')
def baixar_arquivo(nome_arquivo):
    try:
        # Envia o arquivo para o navegador
        return send_from_directory(UPLOAD_FOLDER, nome_arquivo, as_attachment=True)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    # Roda na 8080 para o NPM redirecionar
    app.run(host='0.0.0.0', port=8080)