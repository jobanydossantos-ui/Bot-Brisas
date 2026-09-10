from flask import Flask, request
import requests
from datetime import datetime
import os

app = Flask(__name__)

TOKEN_WHATSAPP = "EAAS5325EUUEBScxbiPZCibjWFtkTN9wD92EWnfHXN6pwibrUrtph7BofKsIDOoo5ezQ42oTxcRzFRQIae37b2q3dM0OyZAW5yfjTiEspVzteZBDnERK6rlXiZCvSj3vADIjkRt4MgjD6yl5IsdZBCS01d2TflZCyaJzZAsmXpfTHyqIHH09CfxLQLceN9vL7lCfyQZDZD"
ID_NUMERO = "1310387282157551"
VERIFY_TOKEN = "brisas123"

PROMOS = {
    "lunes": "Lunes cerrados, te esperamos el martes.",
    "martes": "Martes carta completa y micheladas bien frias.",
    "miercoles": "Miercoles Perlas Negras 2x1 hasta 5pm",
    "jueves": "Jueves Cocteleria de Litro en $100 y Perla 2x1 hasta 5pm",
    "viernes": "Viernes Cocteleria Litro $100 y Perla 2x1 hasta 5pm",
    "sabado": "Sabado de Botellas y Perla Negra",
    "domingo": "Domingo familiar con consumo"
}

def enviar(to, texto):
    url = f"https://graph.facebook.com/v20.0/{ID_NUMERO}/messages"
    headers = {"Authorization": f"Bearer {TOKEN_WHATSAPP}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": texto}}
    r = requests.post(url, headers=headers, json=data)
    print(r.status_code, r.text[:500])
    return r

@app.route("/")
def inicio():
    return "BOT LAS BRISAS OFICIAL ACTIVO +52 664", 200

@app.route("/webhook", methods=["GET"])
def verificar():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        value = data["entry"][0]["changes"][0]["value"]
        if "messages" in value:
            de = value["messages"][0]["from"]
            texto = value["messages"][0].get("text", {}).get("body", "").lower()
            hoy_en = datetime.now().strftime("%A").lower()
            mapa = {"monday":"lunes","tuesday":"martes","wednesday":"miercoles","thursday":"jueves","friday":"viernes","saturday":"sabado","sunday":"domingo"}
            hoy = mapa.get(hoy_en, "viernes")
            if any(x in texto for x in ["hola","menu","carta","promo","hoy"]):
                resp = f"Hola! 🌴 Soy Brisa de Las Brisas.\n\nHoy es {hoy}: {PROMOS[hoy]}"
            else:
                resp = f"{PROMOS[hoy]}"
            enviar(de, resp)
    except Exception as e:
        print(e)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
