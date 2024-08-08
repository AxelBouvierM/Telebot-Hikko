import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import mysql.connector
import json

TOKEN = 'TU_TOKEN_BOT_TELEGRAM'
bot = telebot.TeleBot(TOKEN)

# Conexión a la base de datos.
def DBconnection():
    return mysql.connector.connect(
        host="TU_HOST",
        user="TU_USER",
        password="TU_PASSWORD",
        database="TU_DATABASE"
    )

# Bienvenida, comando /start.
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, '¡Hola! ¿Qué necesitas? 😀')
    mainMenu(message.chat.id)
    
# Definicion del menú principal
def mainMenu (message_id):
    # Creacion de botones
    markup = InlineKeyboardMarkup()
    # Callback_data es un id del botón, capturable a traves del decorador callback_query_handler
    markup.add(InlineKeyboardButton("¡Quiero saber el clima! ☀", callback_data="consulta_clima"))
    markup.add(InlineKeyboardButton("¡Quiero contar! 🔢", callback_data="quiero_contar"))
    markup.add(InlineKeyboardButton("¡Analizar mi comentario! 👨‍💻", callback_data="analizar_comentario"))
    markup.add(InlineKeyboardButton("¡Sobre Hikko! 👨", callback_data="sobre_hikko"))
    bot.send_message(message_id, 'Selecciona una opción:', reply_markup=markup)

# Decorador para obtencion de la accion de los botones.
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "consulta_clima":
        msg = bot.send_message(call.message.chat.id, 'Por favor, ingresa el nombre de la ciudad:')
        # register_next_step_handler define donde continuar la accion luego de obtener una respuesta...
        bot.register_next_step_handler(msg, obtener_clima)
    elif call.data == "quiero_contar":
        # Ejecución de la funcion count: Realiza una busqueda en la BD para incrementar el contador para el user_id 
        cant = count(call.from_user.id, call.message.chat.id)
        bot.send_message(call.message.chat.id, f'Usted ha interactuado {cant} veces')
        mainMenu(call.message.chat.id)
    elif call.data == 'analizar_comentario':
        msg = bot.send_message(call.message.chat.id, 'Por favor, ingresa el comentario a analizar:')
        bot.register_next_step_handler(msg, analizar_comentario)
    elif call.data == "sobre_hikko":
        msg = bot.send_message(call.message.chat.id, 'Por favor, ingresa tu consulta:')
        bot.register_next_step_handler(msg, asistente_hikko)

# Funcion para la opcion consultar clima, obtencion de coordenadas y clima.
def obtener_clima(message):
    try:
        # Request para obtener las coordenadas a partir del nombre de la ciudad o país...
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': message.text,
            'format': 'json'
        }
        headers = {
        'User-Agent': 'MiBot/1.0 (miemail@dominio.com)'
        }
        response = requests.get(url, params=params, headers=headers)
        coordinates = response.json()
    
        # Control para validar la obtencion de las coordenadas
        if (coordinates and coordinates[0] and coordinates[0]['lat'] and coordinates[0]['lon']):
            latitud = coordinates[0]['lat'].replace('-', '')
            longitud = coordinates[0]['lon'].replace('-', '')
        
            # Request a API para la obtencion del estado del clima...
            url = 'https://api.openweathermap.org/data/2.5/weather'
            params = {
                'lat': latitud,
                'lon': longitud,
                'appid': 'TU_APP_ID'
            }
            response = requests.get(url, params=params)
            weather = response.json()
        
            # Clima en la ciudad:
            main = weather['weather'][0]['description']
            temp = round(weather['main']['temp'] - 273.15, 2) #Conversion de Kelvin a Celsius
            temp_min = round(weather['main']['temp_min'] - 273.15, 2)
            temp_max = round(weather['main']['temp_max'] - 273.15, 2)
            humidity = weather['main']['humidity']
        
            formattedMsg = f'El clima en {message.text} es el siguiente: \n*Estado actual*: {main} \n*Temperatura actual*: {temp}° \n*Temperatura mínima*: {temp_min}° \n*Temperatura máxima*: {temp_max}° \n*Humedad*: {humidity}%'
            # Ejecución de función para generar comentario/recomendacion con openai...
            comment = generar_comentario(message)
            msg = bot.send_message(message.chat.id, formattedMsg, parse_mode='Markdown')
            msg = bot.send_message(message.chat.id, comment)

            mainMenu(message.chat.id)
        else:
            # Ciudad/país invalidos o no se encontraron resultados para la localidad ingresada...
            msg = bot.send_message(message.chat.id, 'No hemos encontrado la ciudad indicada. Por favor, verifica que el nombre de la ciudad no contenga faltas ortográficas y/o sea una ciudad válida.')
            msg = bot.send_message(message.chat.id, 'Ingrese nuevamente la ciudad:')
            # Se vuelve a llamar a la funcion obtener_clima para realizar nuevamente el proceso.
            bot.register_next_step_handler(msg, obtener_clima)
    except Exception as e:
        msg = bot.send_message(message.chat.id, '¡Ha ocurrido un error! 😐')
        mainMenu(message.chat.id)
        #print(f'Error en APIs: {e}')

# Funcion para la opcion "quiero contar", incrementa un contador unico por usuario en cada interacción con el botón.
def count(user_id, chat_id):
    try:
        # Conexión a la BD
        connection = DBconnection()
        cursor = connection.cursor()
        # Para el user_id indicado se obtiene el contador...
        cursor.execute("SELECT counter FROM user_counters WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if result:
            count = result[0]
        else:
            count = 0

        if count > 0:
            # Setea el incremento del contador en la tabla de la BD...
            cursor.execute('UPDATE user_counters SET counter = counter + 1 WHERE user_id = %s', (user_id,))
            count = count + 1
        else:
            cursor.execute('INSERT INTO user_counters (user_id, counter) VALUES (%s, 1)', (user_id,))
            count = 1

        connection.commit()
        cursor.close()
        connection.close()
    
        return count
    except Exception as e:
        msg = bot.send_message(chat_id, '¡Ha ocurrido un error! 😐')
        mainMenu(chat_id)

# Funcion para la opcion "Analizar mi comentario", en base a un comentario ingresado openai evalua el sentimiento del mismo: Positivo, Negativo o Neutro
def analizar_comentario(message):
    try:
        # Request a Openai...
        url = "https://api.openai.com/v1/chat/completions"

        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Tu eres un ayudante de un bot de telegram, en el cual tu única acción es analizar el sentimiento de una conversación. Los sentimientos posibles son: positivo negativo o neutral. Es muy importante que solo respondas con una de estas tres opciones"
                },
                {
                    "role": "user",
                    "content": f'{message}'
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'TU_TOKEN'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        senti = response.json()
        senti = senti['choices'][0]['message']['content']
        
        msg = bot.send_message(message.chat.id, f'Su sentimiento es: *{senti}*', parse_mode='Markdown')
        mainMenu(message.chat.id)
    except Exception as e:
        msg = bot.send_message(message.chat.id, '¡Ha ocurrido un error! 😐')
        mainMenu(message.chat.id)

# Funcion para generar comentario de recomandacion en la opcion de clima.
def generar_comentario(message):
    try:
        # Request a Openai para generar el comentario...
        url = "https://api.openai.com/v1/chat/completions"

        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Tu eres un ayudante de un bot de telegram, el cual tu única funcion sera generar un comentario cuando el usuario consulta el clima para que la experiencia sea mas calida, puede ser respecto al clima o a la ciudad consultada, dar algun consejo o informacion breve de la ciudad. El comentario debe ser breve y puedes utilizar emojis. "
                },
                {
                    "role": "user",
                    "content": f'{message}'
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'TU_TOKEN',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        comment = response.json()
        return comment['choices'][0]['message']['content']
        
    except Exception as e:
        msg = bot.send_message(message.chat.id, '¡Ha ocurrido un error! 😐')
        mainMenu(message.chat.id)

# Funcion para la opcion "sobre hikko", en base a informacion la informacion disponible responde preguntas...
def asistente_hikko(message):
    try:
        url = "https://api.openai.com/v1/chat/completions"

        payload = json.dumps({
            #"model": "gpt-3.5-turbo",
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": 'Eres un asistente de bot de telegram. Trabajas para Hikko y tu funcion es brindar informacion sobre la empresa. Bajo ningun punto de vista puedes responder informacion que no se encuentre en el contexto.\
                                Tienes completamente prohibido dar informacion que no se encuentre en el contexto o informacion personal. Puedes utilizar emojis para una charla mas amable. No saludes con un hola, ya que la conversacion cuando llega a vos ya esta iniciada, si podes dar otro tipo de saludos. \
                                La informacion de la empresa es la siguiente: \
                                Sobre Hikko: Creamos Hikko para materializar un futuro comprometido y dinámico: mejores servicios, mejores productos, mejores ideas. Emprender, con cada organización y cada persona, un viaje hacia posibilidades inimaginadas. \
                                Hikko surge de la fusión entre Nimacloud y Nerv: dos organizaciones con capacidades complementarias y una visión compartida. Integramos esa experiencia para crear productos de servicio al cliente automatizados y ofrecer servicios de Salesforce de primer nivel.\
                                PROPÓSITO: Impulsados por un propósito que tiene sentido en la interacción:\
                                -	Escalar organizaciones: Nos mueve la satisfacción de ascender y descubrir. Acompañar a nuestros clientes hasta la cima. \
                                -	Empoderar comunidades: Estamos en la misión de mejorar realidades y promover el desarrollo de agentes de cambio. \
                                -	Expandir el impacto: Somos la piedra que genera ondas en el agua. Y comienza una cascada de verdadero cambio. \
                                Nuestra sede, origen y espíritu son uruguayos: un verdadero símbolo de estabilidad, y un faro regional en tecnología, negocios y servicios. Conocidos por nuestro trabajo apasionado, afecto, transparencia y singularidad, en una época en la que todo esto parece escaso. \
                                Nuestros servicios: \
                                Somos el Socio de Servicios de Salesforce que te permitirá escalar tu negocio, equipos y sistemas.\
                                Amplía tu capacidad en Salesforce: Juntamos las necesidades específicas de Salesforce de tu organización con las personas adecuadas para atenderlas. \
                                Servicios gestionados: Formamos un equipo multidisciplinario de los mejores en su clase para encontrar la clave de la visión a largo plazo. Nuestra propia metodología y mejores prácticas, a tu servicio. \
                                Servicios de aumento de personal: Tú conoces las piezas que faltan en tu equipo y nosotros proporcionamos el talento para completarlas. \
                                Servicios Estratégicos de Salesforce. \
                                Consultoría: Realizamos un análisis profundo de tu organización Salesforce para estudiar tus procesos y detectar oportunidades de mejora. \
                                Capacitación: Proporcionamos a tu equipo el mejor conjunto de herramientas para que puedan aprovechar al máximo un ecosistema vasto y rico. \
                                Cómo ayudamos a tu empresa: \
                                -	Mejora los resultados de tu servicio al cliente: ahorra dinero y aumenta la eficiencia. \
                                -	Escala sin limitaciones: Añade flujos inteligentes al soporte al cliente para desbloquear el crecimiento gestionando un mayor volumen de interacciones. \
                                -	Reduce costos: Integra autoservicio para los usuarios y optimiza tus procesos de soporte incorporando agentes solo cuando sea necesario. \
                                -	Mejora la experiencia del cliente: Proporciona una experiencia centralizada y omnicanal que encantará a tus clientes y reducirá la rotación.'
                },
                {
                    "role": "user",
                    "content": f'{message}'
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'TU_TOKEN',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        comment = response.json()
        msg = bot.send_message(message.chat.id, comment['choices'][0]['message']['content'])
        mainMenu(message.chat.id)
        
    except Exception as e:
        msg = bot.send_message(message.chat.id, '¡Ha ocurrido un error! 😐')
        mainMenu(message.chat.id)

if __name__ == '__main__':
    bot.polling(none_stop=True)