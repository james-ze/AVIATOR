from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import time
import os
import asyncio

# Variables globales
gale_aplicado = False
entrada_confirmada = False
historico = {"🍀": 0, "❌": 0}
greens_consecutivos = 0
ultimo_green = False
mensaje_posible_entrada = None
mensaje_abortar = None
hubo_posible_entrada = False
esperando_abortar = False
mensaje_gale = None
monitoreando = True  # Nueva variable para controlar el monitoreo

# Función para manejar el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu bot. Estoy monitoreando los datos en tiempo real.")

# Función para enviar datos a Telegram
async def enviar_datos(context: ContextTypes.DEFAULT_TYPE, chat_id, mensaje):
    return await context.bot.send_message(chat_id=chat_id, text=mensaje)

# Función para borrar un mensaje
async def borrar_mensaje(context: ContextTypes.DEFAULT_TYPE, chat_id, mensaje_id):
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=mensaje_id)
    except Exception as e:
        print(f"Error al borrar mensaje: {e}")

# Función para eliminar un mensaje después de un retraso
async def eliminar_mensaje_con_retraso(context: ContextTypes.DEFAULT_TYPE, chat_id, mensaje_id, retraso=5):
    await asyncio.sleep(retraso)
    await borrar_mensaje(context, chat_id, mensaje_id)

# Función para calcular la asertividad
def calcular_asertividad():
    total = historico["🍀"] + historico["❌"]
    if total == 0:
        return 0.0
    return (historico["🍀"] / total) * 100

# Función para formatear números con comas
def formatear_numero(valor):
    if isinstance(valor, str):
        return float(valor.replace(",", ""))
    return float(valor)

# Función para monitorear el archivo y enviar datos
async def monitorear_archivo(context: ContextTypes.DEFAULT_TYPE):
    global gale_aplicado, entrada_confirmada, greens_consecutivos, ultimo_green
    global mensaje_posible_entrada, mensaje_abortar, hubo_posible_entrada, esperando_abortar, mensaje_gale, monitoreando

    ultimo_tamano = 0
    while monitoreando:  # Solo monitorear mientras la variable sea True
        if os.path.exists('resultados.txt'):
            tamano_actual = os.path.getsize('resultados.txt')
            if tamano_actual > ultimo_tamano:
                with open('resultados.txt', 'r') as archivo:
                    archivo.seek(ultimo_tamano)
                    nuevas_lineas = archivo.readlines()
                    ultimo_tamano = archivo.tell()

                    for linea in nuevas_lineas:
                        try:
                            datos = eval(linea.strip())
                            datos = [formatear_numero(valor) for valor in datos]
                            if len(datos) >= 2:
                                valor1, valor2 = datos[0], datos[1]

                                # 1. Entrada confirmada (2x)
                                if not entrada_confirmada and valor1 >= 2.0 and valor2 >= 2.0:
                                    mensaje = (
                                        "✅   ENTRADA CONFIRMADA   ✅\n\n"
                                        f"👉 INGRESAR DESPUÉS: {valor1}x\n"
                                        "💰 RETIRAR EN: 1.5x\n\n"
                                        "🔁 MÁXIMO 1 GALES"
                                    )
                                    await enviar_datos(context, context.job.chat_id, mensaje)
                                    entrada_confirmada = True
                                    gale_aplicado = False
                                    hubo_posible_entrada = False
                                    esperando_abortar = False

                                    if mensaje_posible_entrada:
                                        asyncio.create_task(eliminar_mensaje_con_retraso(context, context.job.chat_id, mensaje_posible_entrada.message_id, 5))

                                # 2. Green (≥1.5x)
                                elif entrada_confirmada and valor1 >= 1.5:
                                    if mensaje_gale:  # Borrar mensaje de Gale
                                        await borrar_mensaje(context, context.job.chat_id, mensaje_gale.message_id)
                                        mensaje_gale = None

                                    historico["🍀"] += 1
                                    greens_consecutivos += 1
                                    mensaje = (
                                        "🍀🍀🍀   GREEN!!!   🍀🍀🍀\n\n"
                                        f"✅ Resultado: {valor1}x\n\n"
                                        f"📊 Porcentaje hasta ahora:🍀{historico['🍀']} ❌{historico['❌']}\n"
                                        f"💹 Asertividad: {calcular_asertividad():.2f}%\n"
                                        f"✅ Greens consecutivos: {greens_consecutivos}"
                                    )
                                    await enviar_datos(context, context.job.chat_id, mensaje)
                                    entrada_confirmada = False
                                    ultimo_green = True

                                # 3. Red (<1.5x después de Gale)
                                elif entrada_confirmada and valor1 < 1.5:
                                    if mensaje_gale:  # Borrar mensaje de Gale
                                        await borrar_mensaje(context, context.job.chat_id, mensaje_gale.message_id)
                                        mensaje_gale = None

                                    if not gale_aplicado:
                                        mensaje_gale = await enviar_datos(context, context.job.chat_id, "⚠️ APLICAR PROTECCIÓN GALE 1 ⚠️\n\nENTRAR AHORA!")
                                        gale_aplicado = True
                                    else:
                                        historico["❌"] += 1
                                        greens_consecutivos = 0
                                        mensaje = (
                                            "❌ RED :(  \n"
                                            f"A veces puede suceder, ¡pero basta con gestionar tu banca!\n\n"
                                            f"📊 Porcentaje hasta ahora:🍀 {historico['🍀']}❌{historico['❌']}\n"
                                            f"💹 Asertividad: {calcular_asertividad():.2f}%\n"
                                        )
                                        await enviar_datos(context, context.job.chat_id, mensaje)
                                        entrada_confirmada = False
                                        gale_aplicado = False

                                # 4. Posible entrada (≥2x)
                                if not entrada_confirmada and (valor1 >= 2.0) and not esperando_abortar:
                                    mensaje = "⚠️ ATENCIÓN\nPosible entrada, espere confirmación"
                                    mensaje_posible_entrada = await enviar_datos(context, context.job.chat_id, mensaje)
                                    hubo_posible_entrada = True
                                    esperando_abortar = True

                                # 5. Abortar entrada (<2x)
                                if not entrada_confirmada and (valor1 < 2.0) and esperando_abortar:
                                    mensaje = "⚠️ Abortar posible entrada..."
                                    mensaje_abortar = await enviar_datos(context, context.job.chat_id, mensaje)
                                    hubo_posible_entrada = False
                                    esperando_abortar = False

                                    if mensaje_posible_entrada:
                                        asyncio.create_task(eliminar_mensaje_con_retraso(context, context.job.chat_id, mensaje_posible_entrada.message_id, 5))
                                    asyncio.create_task(eliminar_mensaje_con_retraso(context, context.job.chat_id, mensaje_abortar.message_id, 5))

                        except Exception as e:
                            print(f"Error al procesar la línea: {linea}. Error: {e}")
        await asyncio.sleep(2)

# Función para iniciar el monitoreo
async def iniciar_monitoreo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global monitoreando
    monitoreando = True
    chat_id = update.message.chat_id
    context.job_queue.run_once(lambda ctx: monitorear_archivo(ctx), when=0, chat_id=chat_id)
    await update.message.reply_text("Monitoreo de datos iniciado.")

# Función para terminar el monitoreo
async def terminar_monitoreo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global monitoreando
    monitoreando = False
    await update.message.reply_text("Monitoreo de datos detenido.")

# Configurar la aplicación del bot
aplicacion = ApplicationBuilder().token("7234323027:AAF03nr9cvHbR49VlM8eK5WCPJlbLXCtFjI").build()

# Registrar los manejadores de comandos
aplicacion.add_handler(CommandHandler("start", start))
aplicacion.add_handler(CommandHandler("iniciar", iniciar_monitoreo))
aplicacion.add_handler(CommandHandler("terminar", terminar_monitoreo))  # Nuevo comando

# Iniciar el bot
aplicacion.run_polling()
