import importlib
import threading
import logging
from config import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
from telebot.apihelper import ApiException
from commands.contacto import contacto_command
from commands.help import help_command
from commands.constructores import constructores_command
from commands.trivia import trivia_command
from commands.video import video_command

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)

command_modules = [
    'video', 'contacto', 'pilots', 'constructores', 'calendario', 'help', 'trivia', 'resultados', 'sprint'
]

commands = {}
for module_name in command_modules:
    mod = importlib.import_module(f'commands.{module_name}')
    commands[module_name] = getattr(mod, f'{module_name}_command')

@bot.message_handler(commands=['contacto'])
def contacto_command_handler(message):
    contacto_command(message, bot)

@bot.message_handler(commands=['help'])
def help_command_handler(message):
    help_command(message, bot)

@bot.message_handler(commands=['constructores'])
def constructores_command_handler(message):
    constructores_command(message, bot)

@bot.message_handler(commands=['trivia'])
def trivia_command_handler(message):
    trivia_command(message, bot)

@bot.message_handler(commands=['video'])
def video_command_handler(message):
    video_command(message, bot)

def create_inline_buttons():
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("🗓️ Calendario 🗓️", callback_data='calendario'),
        InlineKeyboardButton("👲 Pilotos 👲", callback_data='pilots'),
        InlineKeyboardButton("🏎️ Constructores 🏎️", callback_data='constructores'),
        InlineKeyboardButton("⏯️ Video ⏯️", callback_data='video'),
        InlineKeyboardButton("💡 Ayuda 🆘", callback_data='help'),
        InlineKeyboardButton("📞 Contacto 🗣", callback_data='contacto'),
        InlineKeyboardButton("🎮 TrivialF1 🎮", callback_data='trivia')
    )
    return markup


def delete_message_later(chat_id, message_id, delay=2):
    def delete():
        try:
            bot.delete_message(chat_id, message_id)
        except Exception as e:
            logging.warning(f"Error al intentar eliminar el mensaje (ID: {message_id}) del chat {chat_id}: {e}")

    threading.Timer(delay, delete).start()


def escape_markdown_v2(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)


def start(message, user_name=None):
    user = message.from_user if hasattr(message, 'from_user') else message.chat
    name = user_name if user_name else escape_markdown_v2(user.first_name)
    last_name = escape_markdown_v2(user.last_name) if user.last_name else ""
    full_name = f"{name} {last_name}".strip()

    logging.info(f"Comando /start recibido de usuario: {full_name} (ID: {user.id})")

    mensaje_bienvenida = (
        f"🎉👋 *¡Bienvenido \\{full_name}\\!*\n\n"
        "🚥 *Este es un bot desarrollado para uso no comercial de* Fórmula 1 🏎💨\n\n"
        "✨ *Explora todo el contenido disponible*:\n\n"
        "🔹 *Pilotos*: _Descubre sus logros y estadísticas_\\.\n"
        "🔹 *Equipos*: _Información detallada de escuderías_\\.\n"
        "🔹 *Calendario*: _Fechas de carreras, horarios, *resultados* y eventos_\\.\n"
        "🔹 *Video*: ¡_Disfruta de contenido visual cada fin de semana de carrera_\\!\n"
        "🔹 *TrivialF1*: ¡_Juega al trivial de F1, a ver cuantas preguntas puedes acertar_\\!\\.\n"
        "🔹 *Contacto*: _Para cualquier fallo en la navegación o déjanos saber tus sugerencias_\\.\n\n"
        "🔻 *Selecciona una opción para comenzar:* 🔻"
    )

    bot.send_message(
        message.chat.id,
        mensaje_bienvenida,
        parse_mode="MarkdownV2",
        reply_markup=create_inline_buttons()
    )


@bot.message_handler(commands=['start'])
def start_command_handler(message):
    user_name = escape_markdown_v2(message.from_user.first_name)
    start(message, user_name=user_name)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    logging.info(f"Callback recibido con data: {call.data}, de usuario ID: {call.from_user.id}")
    try:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

        processing_message = bot.send_message(
            call.message.chat.id,
            "⏳ *Procesando tu selección*\\.\\.\\. 🔄",
            parse_mode="MarkdownV2"
        )
        delete_message_later(call.message.chat.id, processing_message.message_id, 2)

        if call.data == 'main_menu':
            user_name = escape_markdown_v2(call.from_user.first_name)
            start(call.message, user_name=user_name)
        elif call.data in commands:
            bot.send_chat_action(call.message.chat.id, "typing")  # Añadir animación de "escribiendo"
            commands[call.data](call.message, bot)
        else:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🚧 *Próximamente*\\.\\.\\. Estamos trabajando en nuevas funciones.",
                parse_mode="MarkdownV2"
            )
    except Exception as e:
        logging.error(f"Error en el callback '{call.data}' en el chat {call.message.chat.id}: {e}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    username = escape_markdown_v2(message.from_user.username or message.from_user.first_name)
    logging.info(f"Mensaje de usuario '{username}' (ID: {message.from_user.id}): {message.text}")
    
    bot.send_chat_action(message.chat.id, "typing")  # Añadir animación de "escribiendo"
    sleep(1)

    bot.send_message(
        message.chat.id,
        f"🚧 *Comando no reconocido* 🚧\n\n"
        f"Hola, *{username}*\\! Parece que has escrito un comando o mensaje que no entiendo\\.\n\n"
        "💡 *Consejo*: Revisa los comandos disponibles escribiendo */help* o usa los botones del *menú* para navegar correctamente en el bot\\. 🤖 \n\n*Aquí*\n  👇",
        parse_mode="MarkdownV2"
    )
    logging.info("Respuesta del bot enviada al usuario.")

def start_bot_polling():
    reintentos = 0
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
            reintentos = 0  # Resetear contador de reintentos tras una ejecución exitosa
        except ApiException as e:
            logging.warning(f"Error de la API de Telegram: {e}")
            reintentos += 1
            sleep_time = min(60, 5 * reintentos)
            logging.info(f"Reintentando en {sleep_time} segundos...")
            sleep(sleep_time)
        except Exception as e:
            logging.critical(f"Error crítico en infinity_polling: {e}")
            sleep(5)


if __name__ == '__main__':
    logging.info('Iniciando bot "Grid Guru Bot"...')
    logging.info('¡"Grid Guru Bot" On-line!')
    start_bot_polling()