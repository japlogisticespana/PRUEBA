from flask import Flask, request
import telegram
import asyncio, os

app = Flask(__name__)
BOT_TOKEN  = os.environ["BOT_TOKEN"]
CHAT_ID    = os.environ["CHAT_ID"]
bot        = telegram.Bot(token=BOT_TOKEN)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    mensaje = data.get("message", str(data))
    
    if "ALZA" in mensaje:
        emoji = "🟢📈"
    elif "BAJA" in mensaje:
        emoji = "🔴📉"
    else:
        emoji = "⚡"
    
    texto = f"{emoji} *Alerta 15min*\n{mensaje}"
    asyncio.run(bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode="Markdown"))
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
