import os, asyncio, time
import ccxt
import telegram

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]
bot       = telegram.Bot(token=BOT_TOKEN)

# Pares que quieres vigilar
PARES = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]

# Umbral de movimiento fuerte (%)
UMBRAL = 1.5

exchange = ccxt.binance()

def obtener_cambio_15min(par):
    velas = exchange.fetch_ohlcv(par, timeframe="15m", limit=2)
    ultima = velas[-1]
    apertura = ultima[1]
    cierre   = ultima[4]
    cambio   = (cierre - apertura) / apertura * 100
    return cambio, cierre

async def enviar_alerta(mensaje):
    await bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode="Markdown")

async def monitorear():
    print("Bot iniciado, monitoreando...")
    while True:
        for par in PARES:
            try:
                cambio, precio = obtener_cambio_15min(par)
                nombre = par.replace("/", "")

                if cambio >= UMBRAL:
                    msg = f"🟢📈 *ALZA FUERTE*\n*{nombre}* subió `{cambio:.2f}%`\nPrecio: `{precio}`"
                    await enviar_alerta(msg)
                    print(f"ALZA: {par} {cambio:.2f}%")

                elif cambio <= -UMBRAL:
                    msg = f"🔴📉 *BAJA FUERTE*\n*{nombre}* bajó `{cambio:.2f}%`\nPrecio: `{precio}`"
                    await enviar_alerta(msg)
                    print(f"BAJA: {par} {cambio:.2f}%")

            except Exception as e:
                print(f"Error con {par}: {e}")

        time.sleep(60)  # Revisa cada 60 segundos

if __name__ == "__main__":
    asyncio.run(monitorear())
