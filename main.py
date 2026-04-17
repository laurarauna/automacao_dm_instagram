import os
import json
import gspread
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials
import requests

app = Flask(__name__)

def get_link_from_sheet(post_id):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = json.loads(os.environ.get("GOOGLE_CREDS"))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(os.environ.get("SHEET_ID")).sheet1
        
        print(f" Procurando ID {post_id} na planilha...", flush=True)
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
    print(f" Dados recebidos: {json.dumps(data)}", flush=True)

    for entry in data.get('entry', []):
        for change in entry.get('changes', []):
            if change['field'] == 'comments':
                val = change['value']
                text = val.get('text', '').lower()
                comment_id = val.get('id') # ID DO COMENTÁRIO
                post_id = val.get('media', {}).get('id')
                
                if "quero" in text:
                    resposta = get_link_from_sheet(post_id)
                    if resposta:
                        print(f" Respondendo ao comentário {comment_id}...", flush=True)
                        send_private_reply(comment_id, resposta)
    return "OK", 200

def send_private_reply(comment_id, message):
    token = os.environ.get("META_TOKEN")
    # Este endpoint 'private_replies' é o segredo para evitar o erro #3
    url = f"https://graph.facebook.com/v19.0/{comment_id}/private_replies?access_token={token}"
    
    payload = {"message": message}
    response = requests.post(url, json=payload)
    print(f" Resposta da Meta: {response.status_code} - {response.text}", flush=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
