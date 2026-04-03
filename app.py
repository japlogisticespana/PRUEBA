import os, asyncio, time
import requests
import telegram

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]
bot       = telegram.Bot(token=BOT_TOKEN)

UMBRAL        = 1.5
INTERVALO_SEG = 60

def obtener_top_monedas():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 20,
        "page": 1,
        "price_change_percentage": "1h"
    }
    r = requests.get(url, params=params, timeout=10)
    return r.json()

async def enviar_alerta(mensaje):
    await bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode="Markdown")

async def monitorear():
    print("Bot iniciado, monitoreando top 20 por volumen...")
    while True:
        try:
            monedas = obtener_top_monedas()
            print(f"Revisando {len(monedas)} monedas...")

            for m in monedas:
                nombre  = m["symbol"].upper()
                precio  = m["current_price"]
                cambio  = m.get("price_change_percentage_1h_in_currency", 0) or 0
                volumen = m["total_volume"]

                if cambio >= UMBRAL:
                    msg = (
                        f"🟢📈 *ALZA FUERTE*\n"
                        f"*{nombre}/USDT* subió `{cambio:.2f}%` en 1h\n"
                        f"Precio: `{precio:,} USDT`\n"
                        f"Volumen: `{volumen:,.0f}`"
                    )
                    await enviar_alerta(msg)
                    print(f"ALZA: {nombre} {cambio:.2f}%")

                elif cambio <= -UMBRAL:
                    msg = (
                        f"🔴📉 *BAJA FUERTE*\n"
                        f"*{nombre}/USDT* bajó `{cambio:.2f}%` en 1h\n"
                        f"Precio: `{precio:,} USDT`\n"
                        f"Volumen: `{volumen:,.0f}`"
                    )
                    await enviar_alerta(msg)
                    print(f"BAJA: {nombre} {cambio:.2f}%")

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(INTERVALO_SEG)

if __name__ == "__main__":
    asyncio.run(monitorear())
