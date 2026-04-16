import os
import json
import gspread
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials
import requests
import sys

app = Flask(__name__)

# Função para buscar o link na planilha
def get_link_from_sheet(post_id):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = json.loads(os.environ.get("GOOGLE_CREDS"))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
        client = gspread.authorize(creds)
        
        # Abre a planilha
        sheet = client.open_by_key(os.environ.get("SHEET_ID")).sheet1
        
        print(f" Procurando ID {post_id} na planilha...", flush=True)
        
        # Tenta achar o ID na Coluna A
        cell = sheet.find(str(post_id))
        link = sheet.cell(cell.row, 3).value # Coluna C
        msg = sheet.cell(cell.row, 4).value  # Coluna D
        
        return f"{msg} {link}"
    except Exception as e:
        print(f" Erro ao ler planilha: {e}", flush=True)
        return None

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == os.environ.get("VERIFY_TOKEN"):
        return request.args.get("hub.challenge")
    return "Erro de validação", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # Este print é vital: ele mostra tudo o que o Instagram enviou
    print(f" Dados recebidos do Instagram: {json.dumps(data)}", flush=True)

    for entry in data.get('entry', []):
        for change in entry.get('changes', []):
            if change['field'] == 'comments':
                val = change['value']
                text = val.get('text', '').lower()
                user_id = val.get('from', {}).get('id')
                post_id = val.get('media', {}).get('id')
                
                print(f" Comentário detectado: '{text}' no post {post_id}", flush=True)
                
                # Verifica se a palavra "quero" está no comentário
                if "quero" in text:
                    resposta = get_link_from_sheet(post_id)
                    if resposta:
                        print(f" Enviando DM para o usuário {user_id}...", flush=True)
                        send_dm(user_id, resposta)
                    else:
                        print(f" ID {post_id} não encontrado ou sem link na planilha.", flush=True)
    return "OK", 200

def send_dm(user_id, message):
    token = os.environ.get("META_TOKEN")
    # A URL oficial para Instagram Messaging
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={token}"
    
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": message}
    }
    
    response = requests.post(url, json=payload)
    print(f" Resposta da Meta ao enviar DM: {response.status_code} - {response.text}", flush=True)

if __name__ == "__main__":
    # Garante que o log apareça imediatamente
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
