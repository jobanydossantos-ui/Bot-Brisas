from flask import Flask, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

TOKEN_WHATSAPP = os.environ.get("TOKEN_WHATSAPP")
ID_NUMERO = os.environ.get("ID_NUMERO")
VERIFY_TOKEN = "brisas123"

PROMOS = {
    "martes": "Martes sin promocion especial, pero con la compra de su bebida, los alimentos son totalmente gratis hasta las 08:00 PM.",
    "miercoles": "Miercoles de Perlas Negras al 2x1 hasta las 09:00 PM y Litros en $100.",
    "jueves": "Jueves de Cocteleria de Litro en $100 y Botellas seleccionadas en $999 ya incluye refrescos hasta las 09:00 PM. Horario extendido con musica en vivo.",
    "viernes": "Viernes de Cocteleria de Litro en $100 y Botellas seleccionadas en $999 ya incluye refrescos hasta las 09:00 PM. Horario extendido con grupos de Salsa, Cumbia, Norteño, Mariachi o DJ.",
    "sabado": "Sabado de Botellas seleccionadas y Perlas Negras al 2x1. Horario extendido con musica en vivo.",
    "domingo": "Domingo familiar. Con la compra de su bebida, los alimentos son totalmente gratis hasta las 08:00 PM.",
    "lunes": "Lunes permanecemos cerrados. Le esperamos de Martes a Domingo de 01:00 PM a 08:00 PM."
}

usuarios = {}

def enviar(to, texto):
    url = f"https://graph.facebook.com/v20.0/{ID_NUMERO}/messages"
    headers = {"Authorization": f"Bearer {TOKEN_WHATSAPP}"}
    data = {"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":texto}}
    requests.post(url, headers=headers, json=data)

@app.route("/")
def inicio():
    return "Bot Brisa Las Brisas activo"

@app.route("/webhook", methods=["GET"])
def verificar():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        value = data["entry"][0]["changes"][0]["value"]
        if "messages" in value:
            msg = value["messages"][0]
            de = msg["from"]
            texto = msg.get("text",{}).get("body","").lower()
            estado = usuarios.get(de, {}).get("estado", "inicio")

            if estado == "inicio":
                dia_en = datetime.now().strftime("%A").lower()
                trad = {"monday":"lunes","tuesday":"martes","wednesday":"miercoles","thursday":"jueves","friday":"viernes","saturday":"sabado","sunday":"domingo"}
                dia_es = trad.get(dia_en, "martes")
                promo = PROMOS.get(dia_es)
                enviar(de, f"Hola, bienvenido al Centro Botanero Las Brisas. Soy Brisa, anfitriona virtual.\n\nHorario: Martes a Domingo de 01:00 PM a 08:00 PM. Jueves, Viernes y Sabado horario extendido con musica en vivo.\n\nCon la compra de su bebida, los alimentos son totalmente gratis hasta las 08:00 PM.\n\nPromocion de hoy {dia_es.capitalize()}: {promo}\n\nEscriba: RESERVA / PROMO / HORARIO")
                usuarios[de] = {"estado":"menu"}

            elif "promo" in texto:
                dia_en = datetime.now().strftime("%A").lower()
                trad = {"monday":"lunes","tuesday":"martes","wednesday":"miercoles","thursday":"jueves","friday":"viernes","saturday":"sabado","sunday":"domingo"}
                promo = PROMOS.get(trad.get(dia_en,"martes"))
                enviar(de, f"Promocion de hoy:\n{promo}")

            elif "horario" in texto:
                enviar(de, "Centro Botanero Las Brisas\nMartes a Domingo: 01:00 PM a 08:00 PM\nJueves, Viernes y Sabado: Horario extendido con musica en vivo.\nLunes: Cerrado\nAlimentos gratis con su bebida hasta las 08:00 PM.")

            elif "reserva" in texto or estado == "menu":
                enviar(de, "Con gusto. ¿Para cuantas personas sera la reserva?")
                usuarios[de]["estado"] = "personas"

            elif estado == "personas":
                usuarios[de]["personas"] = texto
                enviar(de, f"Perfecto, {texto} personas. ¿Para que dia y a que hora?")
                usuarios[de]["estado"] = "hora"

            elif estado == "hora":
                usuarios[de]["hora"] = texto
                enviar(de, "Confirmado. ¿Zona de preferencia? Terraza, Familiar o Barra")
                usuarios[de]["estado"] = "zona"

            elif estado == "zona":
                usuarios[de]["zona"] = texto
                enviar(de, "Excelente. ¿Celebran algo especial? Cumpleaños, Aniversario, Reunion o Visita casual")
                usuarios[de]["estado"] = "motivo"

            elif estado == "motivo":
                usuarios[de]["motivo"] = texto
                enviar(de, "Gracias. ¿A nombre de quien queda la reservacion?")
                usuarios[de]["estado"] = "nombre"

            elif estado == "nombre":
                enviar(de, f"Gracias {texto}. Su reserva queda confirmada.\n\nResumen:\nPersonas: {usuarios[de]['personas']}\nFecha: {usuarios[de]['hora']}\nZona: {usuarios[de]['zona']}\nMotivo: {usuarios[de]['motivo']}\n\nLe recordamos alimentos gratis con su bebida hasta las 08:00 PM.\nLo esperamos en Las Brisas.")
                usuarios[de] = {"estado":"inicio"}
    except Exception as e:
        print(e)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
