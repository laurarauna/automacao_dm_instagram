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
                user_id = val.get('from', {}).get('id')
                user_name = val.get('from', {}).get('username')
                post_id = val.get('media', {}).get('id')
                
                # Ignorar se o comentário for da própria conta
                if user_name == "casa__curadoria":
                    continue

                if "quero" in text:
                    resposta = get_link_from_sheet(post_id)
                    if resposta:
                        print(f" Comentário de {user_name} detectado. Enviando link...", flush=True)
                        send_instagram_dm(user_id, resposta)
    return "OK", 200

def send_instagram_dm(recipient_id, message_text):
    token = os.environ.get("META_TOKEN") # O TOKEN IGAA... QUE VOCÊ JÁ TEM
    # USANDO O ENDPOINT QUE FUNCIONOU NO SEU CURL
    url = f"https://graph.instagram.com/v25.0/me/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f" Resultado da DM: {response.status_code} - {response.text}", flush=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
