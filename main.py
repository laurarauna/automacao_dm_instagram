import os
import json
import gspread
import random
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
        
        palavra_chave = sheet.cell(cell.row, 2).value.lower() 
        link = sheet.cell(cell.row, 3).value 
        msg = sheet.cell(cell.row, 4).value  
        
        return palavra_chave, f"{msg} {link}"
    except Exception as e:
        print(f" Erro ao ler planilha (ou Post não cadastrado): {e}", flush=True)
        return None, None

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
            if change.get('field') == 'comments':
                val = change.get('value', {})
                text = val.get('text', '').lower()
                user_name = val.get('from', {}).get('username')
                post_id = val.get('media', {}).get('id')
                comment_id = val.get('id') 
                
                # Ignorar se o comentário for da própria conta
                if user_name == "casa__curadoria":
                    continue

                palavra_esperada, resposta = get_link_from_sheet(post_id)

                if palavra_esperada and palavra_esperada in text:
                    print(f" Gatilho '{palavra_esperada}' detectado de {user_name}. Enviando link...", flush=True)
                    send_instagram_dm(comment_id, resposta) 
                    
                    # Responde o comentário publicamente no post
                    reply_to_comment(comment_id, user_name) 
                    
                elif palavra_esperada:
                    print(f" Comentário ignorado. O gatilho para este post é '{palavra_esperada}', mas o usuário digitou '{text}'.", flush=True)

    return "OK", 200

def send_instagram_dm(comment_id, message_text):
    token = os.environ.get("META_TOKEN") 
    url = f"https://graph.instagram.com/v25.0/me/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "recipient": {"comment_id": comment_id}, 
        "message": {"text": message_text}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f" Resultado da DM: {response.status_code} - {response.text}", flush=True)

def reply_to_comment(comment_id, username):
    token = os.environ.get("META_TOKEN") 
    url = f"https://graph.instagram.com/v25.0/{comment_id}/replies"
    
    # LISTA DE RESPOSTAS PERSONALIZADAS:
    lista_de_respostas = [
        f"Oii, @{username}! Já te chamei no direct com o link, verifica se chegou! ✨",
        f"Oie, @{username}! Tudo bem? Te mandei no direct, veja se chegou certinho",
        f"Oi, @{username}! Enviei na sua DM ✨",
        f"Prontinho @{username} 🧡! Veja se chegou certinho na sua DM",
        f"@{username}, mandei no seu direct! Veja se chegou pra você"
    ]
    
    mensagem_sorteada = random.choice(lista_de_respostas)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": mensagem_sorteada
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f" Resultado da Resposta no Post: {response.status_code} - {response.text}", flush=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
