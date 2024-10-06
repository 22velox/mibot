from config import *
import telebot
from telebot import types
import requests
from json.decoder import JSONDecodeError

bot = telebot.TeleBot(TELEGRAM_TOKEN)

PILOTS_API_URL = "http://ergast.com/api/f1/2024/drivers.json"
SESSIONS_API_URL = "https://ergast.com/api/f1/2024.json"
CONSTRUCTORS_API_URL = "http://ergast.com/api/f1/2024/constructors.json"
QUALIFYING_API_URL = "http://ergast.com/api/f1/2024/18/qualifying.json"
LAST_RACE_API_URL = "http://ergast.com/api/f1/2024/18/results.json"
NEXT_RACE_API_URL = "http://ergast.com/api/f1/current.json"

last_messages = {}

def delete_last_message(chat_id):
    if chat_id in last_messages:
        try:
            bot.delete_message(chat_id, last_messages[chat_id])
        except Exception as e:
            print(f"Error al borrar mensaje anterior: {e}")

def send_typing_action(chat_id):
    bot.send_chat_action(chat_id, 'typing')

def get_json_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except JSONDecodeError as e:
        raise ValueError(f"Error en el formato JSON: {e}")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Error de conexión o en la solicitud: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    delete_last_message(message.chat.id)

    markup = types.InlineKeyboardMarkup()

    pilots_button = types.InlineKeyboardButton("Pilotos", callback_data="pilotos")
    sessions_button = types.InlineKeyboardButton("Sesiones2024", callback_data="sesiones2024")
    constructors_button = types.InlineKeyboardButton("Constructores", callback_data="constructores")
    qualifying_button = types.InlineKeyboardButton("Clasificación", callback_data="clasificacion")
    last_race_button = types.InlineKeyboardButton("Últ.carrera", callback_data="ult_carrera")
    next_race_button = types.InlineKeyboardButton("Próx.carrera", callback_data="prox_carrera")

    markup.add(pilots_button, constructors_button)
    markup.add(sessions_button, qualifying_button, last_race_button, next_race_button)

    send_typing_action(message.chat.id)
    sent_message = bot.send_message(message.chat.id, "¡Bienvenido! Aquí abajo tienes varios botones para consultar lo que necesites saber:", reply_markup=markup)

    last_messages[message.chat.id] = sent_message.message_id

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == "pilotos":
        handle_pilots_command(call.message)
    elif call.data == "sesiones2024":
        handle_sessions_command(call.message)
    elif call.data == "constructores":
        handle_constructors_command(call.message)
    elif call.data == "clasificacion":
        handle_qualifying_command(call.message)
    elif call.data == "ult_carrera":
        handle_last_race_command(call.message)

@bot.message_handler(commands=['pilotos'])
def handle_pilots_command(message):
    delete_last_message(message.chat.id)
    send_typing_action(message.chat.id)
    
    try:
        data = get_json_data(PILOTS_API_URL)
        drivers_data = data['MRData']['DriverTable']['Drivers']
        
        if not drivers_data:
            sent_message = bot.send_message(message.chat.id, "No hay pilotos disponibles para la temporada actual.")
            last_messages[message.chat.id] = sent_message.message_id
            return
        
        pilots_list = "\n\n".join(
            f"Nombre: {driver['givenName']} {driver['familyName']}\n"
            f"Número: {driver.get('permanentNumber', 'N/A')}\n"
            f"Nacionalidad: {driver['nationality']}\n"
            f"Fecha de nacimiento: {driver['dateOfBirth']}"
            for driver in drivers_data
        )
        
        sent_message = bot.send_message(message.chat.id, pilots_list)
        last_messages[message.chat.id] = sent_message.message_id
    
    except (ValueError, ConnectionError) as e:
        sent_message = bot.send_message(message.chat.id, f"Error al obtener los datos de los pilotos: {e}")
        last_messages[message.chat.id] = sent_message.message_id

@bot.message_handler(commands=['sesiones2024'])
def handle_sessions_command(message):
    delete_last_message(message.chat.id)
    send_typing_action(message.chat.id)
    
    try:
        data = get_json_data(SESSIONS_API_URL)
        sessions_data = data['MRData']['RaceTable']['Races']
        
        if not sessions_data:
            sent_message = bot.send_message(message.chat.id, "No hay sesiones disponibles.")
            last_messages[message.chat.id] = sent_message.message_id
            return
        
        sessions_list = "\n\n".join(
            f"Gran Premio: {session['raceName']}\n"
            f"Fecha: {session['date']}\n"
            f"Ubicación: {session['Circuit']['Location']['locality']}, {session['Circuit']['Location']['country']}"
            for session in sessions_data
        )
        
        sent_message = bot.send_message(message.chat.id, sessions_list)
        last_messages[message.chat.id] = sent_message.message_id
    
    except (ValueError, ConnectionError) as e:
        sent_message = bot.send_message(message.chat.id, f"Error al obtener los datos de las sesiones: {e}")
        last_messages[message.chat.id] = sent_message.message_id

@bot.message_handler(commands=['constructores'])
def handle_constructors_command(message):
    delete_last_message(message.chat.id)
    send_typing_action(message.chat.id)
    
    try:
        data = get_json_data(CONSTRUCTORS_API_URL)
        constructors_data = data['MRData']['ConstructorTable']['Constructors']
        
        if not constructors_data:
            sent_message = bot.send_message(message.chat.id, "No hay constructores disponibles.")
            last_messages[message.chat.id] = sent_message.message_id
            return

        constructors_list = "\n\n".join(
            f"Nombre: {constructor['name']}\n"
            f"Nacionalidad: {constructor['nationality']}"
            for constructor in constructors_data
        )
        
        sent_message = bot.send_message(message.chat.id, constructors_list)
        last_messages[message.chat.id] = sent_message.message_id
    
    except (ValueError, ConnectionError) as e:
        sent_message = bot.send_message(message.chat.id, f"Error al obtener los datos de los constructores: {e}")
        last_messages[message.chat.id] = sent_message.message_id

@bot.message_handler(commands=['clasificacion'])
def handle_qualifying_command(message):
    delete_last_message(message.chat.id)
    send_typing_action(message.chat.id)
    
    try:
        data = get_json_data(QUALIFYING_API_URL)
        qualifying_data = data['MRData']['RaceTable']['Races'][0]['QualifyingResults']
        
        if not qualifying_data:
            sent_message = bot.send_message(message.chat.id, "No hay datos de clasificación disponibles.")
            last_messages[message.chat.id] = sent_message.message_id
            return
        
        qualifying_list = "\n\n".join(
            f"Piloto: {result['Driver']['givenName']} {result['Driver']['familyName']}\n"
            f"Posición: {result['position']}\n"
            f"Constructor: {result['Constructor']['name']}\n"
            f"Q1: {result.get('Q1', 'N/A')}\n"
            f"Q2: {result.get('Q2', 'N/A')}\n"
            f"Q3: {result.get('Q3', 'N/A')}"
            for result in qualifying_data
        )
        
        sent_message = bot.send_message(message.chat.id, qualifying_list)
        last_messages[message.chat.id] = sent_message.message_id
    
    except (ValueError, ConnectionError) as e:
        sent_message = bot.send_message(message.chat.id, f"Error al obtener los datos de clasificación: {e}")
        last_messages[message.chat.id] = sent_message.message_id

@bot.message_handler(commands=['ult_carrera'])
def handle_last_race_command(message):
    delete_last_message(message.chat.id)
    send_typing_action(message.chat.id)

    try:
        data = get_json_data(LAST_RACE_API_URL)
        race_data = data['MRData']['RaceTable']['Races'][0]['Results']

        if not race_data:
            sent_message = bot.send_message(message.chat.id, "No hay datos disponibles de la última carrera.")
            last_messages[message.chat.id] = sent_message.message_id
            return

        race_results = "\n\n".join(
            f"Posición: {result['position']}\n"
            f"Piloto: {result['Driver']['givenName']} {result['Driver']['familyName']}\n"
            f"Constructor: {result['Constructor']['name']}\n"
            f"Tiempo: {result.get('Time', {}).get('time', 'N/A')}"
            for result in race_data
        )

        sent_message = bot.send_message(message.chat.id, race_results)
        last_messages[message.chat.id] = sent_message.message_id

    except (ValueError, ConnectionError) as e:
        sent_message = bot.send_message(message.chat.id, f"Error al obtener los resultados de la última carrera: {e}")
        last_messages[message.chat.id] = sent_message.message_id

@bot.callback_query_handler(func=lambda call: call.data == "prox_carrera")
def handle_next_race_button(call):
    handle_next_race_command(call.message)

@bot.message_handler(commands=['prox_carrera'])
def handle_next_race_command(message):
    if message.chat.id in last_messages:
        try:
            bot.delete_message(message.chat.id, last_messages[message.chat.id])
        except:
            pass

    bot.send_chat_action(message.chat.id, 'typing')

    try:
        response = requests.get(NEXT_RACE_API_URL)
        race_data = response.json()['MRData']['RaceTable']['Races'][0]

        if not race_data:
            sent_message = bot.send_message(message.chat.id, "No hay datos disponibles de la próxima carrera.")
            last_messages[message.chat.id] = sent_message.message_id
            return

        race_info = (
            f"Gran Premio: {race_data['raceName']}\n"
            f"Fecha: {race_data['date']}\n"
            f"Ubicación: {race_data['Circuit']['Location']['locality']}, {race_data['Circuit']['Location']['country']}\n"
        )

        sent_message = bot.send_message(message.chat.id, race_info)
        last_messages[message.chat.id] = sent_message.message_id
    
    except requests.exceptions.RequestException as e:
        sent_message = bot.send_message(message.chat.id, f"Error al obtener los datos de la próxima carrera: {e}")
        last_messages[message.chat.id] = sent_message.message_id

if __name__ == '__main__':
    print('Bot on-line')
    bot.infinity_polling()
