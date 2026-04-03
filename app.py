import os, asyncio, time
import ccxt
import telegram

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]
bot       = telegram.Bot(token=BOT_TOKEN)

UMBRAL        = 1.5   # % mínimo de movimiento para alertar
TOP_N         = 20    # cuántos pares vigilar
INTERVALO_SEG = 60    # cada cuántos segundos revisa

exchange = ccxt.bybit()

def obtener_top_pares():
    tickers = exchange.fetch_tickers()
    usdt = {
        k: v for k, v in tickers.items()
       if k.endswith("/USDT:USDT") == False and k.endswith("/USDT") and v.get("quoteVolume")
    }
    ordenados = sorted(usdt.items(), key=lambda x: x[1]["quoteVolume"], reverse=True)
    return [par for par, _ in ordenados[:TOP_N]]

def obtener_cambio_15min(par):
    velas    = exchange.fetch_ohlcv(par, timeframe="15m", limit=2)
    ultima   = velas[-1]
    apertura = ultima[1]
    cierre   = ultima[4]
    volumen  = ultima[5]
    cambio   = (cierre - apertura) / apertura * 100
    return cambio, cierre, volumen

async def enviar_alerta(mensaje):
    await bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode="Markdown")

async def monitorear():
    print("Bot iniciado, monitoreando top 20 por volumen...")
    while True:
        try:
            pares = obtener_top_pares()
            print(f"Monitoreando: {pares}")
        except Exception as e:
            print(f"Error obteniendo pares: {e}")
            time.sleep(INTERVALO_SEG)
            continue

        for par in pares:
            try:
                cambio, precio, volumen = obtener_cambio_15min(par)
                nombre = par.replace("/", "")

                if cambio >= UMBRAL:
                    msg = (
                        f"🟢📈 *ALZA FUERTE*\n"
                        f"*{nombre}* subió `{cambio:.2f}%`\n"
                        f"Precio: `{precio:,.4f} USDT`\n"
                        f"Volumen 15min: `{volumen:,.0f}`"
                    )
                    await enviar_alerta(msg)
                    print(f"ALZA: {par} {cambio:.2f}%")

                elif cambio <= -UMBRAL:
                    msg = (
                        f"🔴📉 *BAJA FUERTE*\n"
                        f"*{nombre}* bajó `{cambio:.2f}%`\n"
                        f"Precio: `{precio:,.4f} USDT`\n"
                        f"Volumen 15min: `{volumen:,.0f}`"
                    )
                    await enviar_alerta(msg)
                    print(f"BAJA: {par} {cambio:.2f}%")

            except Exception as e:
                print(f"Error con {par}: {e}")

        time.sleep(INTERVALO_SEG)

if __name__ == "__main__":
    asyncio.run(monitorear())
