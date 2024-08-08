# Telegram Bot con Python

Este proyecto es un bot de Telegram desarrollado en Python utilizando la biblioteca telebot. El bot está diseñado para interactuar con los usuarios a través de un menú principal que ofrece diversas funcionalidades integradas con OpenAI y OpenWeatherMap.

**Características**

*Consulta del Clima:*

Permite ingresar un país o ciudad para consultar el estado del clima. La implementación actual utiliza una API gratuita de [OpenStreetMap](https://nominatim.openstreetmap.org/search) para obtener las coordenadas del lugar ingresado. Luego, se utiliza [OpenWeatherMap](https://openweathermap.org/api) para obtener la información climática. Además, se genera un comentario o recomendación basado en el clima o la localidad utilizando GPT-3.5 de [OpenAI](https://platform.openai.com/docs/overview).

Como mejora recomendada, es aconsejable utilizar una API de Geocoding más precisa, como la de [Google](https://developers.google.com/maps/documentation/geocoding/overview?hl=es-419) (https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={key}), ya que la API de OpenStreetMap puede presentar problemas de exactitud en las coordenadas.

*Contador de Interacciones:*

Mantiene un contador único por usuario, identificado por el user_id de Telegram. Este contador se incrementa cada vez que se selecciona esta opción. El contador es persistente ante caídas o cierres de la aplicación. Para lograr esto, se utiliza una tabla en MySQL que identifica a cada usuario por su user_id.

Para este proyecto elegí [MySQL](https://www.mysql.com) como sistema de gestión de bases de datos ya que es fácil de usar y cuenta con una gran comunidad de soporte para resolver problemas que se pudieran llegar a presentar. Además, es la base de datos que mejor conozco, lo cual me permitió desarrollar rápidamente el proyecto dado el tiempo limitado. Otro factor importante es la fácil integración con Python.

*Análisis de Sentimientos:*

Permite ingresar un comentario y se analiza el sentimiento del mismo (positivo, negativo o neutro) utilizando GPT-3.5 de [OpenAI](https://platform.openai.com/docs/overview).

*Información de la Empresa:*

Para esta última opción, decidí simular un asistente virtual, una herramienta con mucho potencial para las empresas hoy en día. Este es un boceto inicial que simula lo que podría ser un entrenamiento con documentos o páginas web mediante scraping, donde el bot responde en base a la información disponible; en este caso, información sobre Hikko. Sin embargo, se podría adaptar para ser un asistente interno de la empresa, un asistente de ventas, o para simplificar la información de cara a los usuarios.

Actualmente, proporciona información relevante de la empresa basada en un contexto dado, utilizando GPT-4 de [OpenAI](https://platform.openai.com/docs/overview).

**Requisitos:**
- *Creación del bot en Telegram:*
    - Para ello, dentro de [Telegram](https://core.telegram.org), debemos crear un nuevo bot. En el buscador, debemos buscar "BotFather". Una vez iniciada la conversación (/start), debemos proceder con la creación del bot utilizando el comando /newbot. A continuación, se nos solicitará el nombre y un username que deseamos otorgarle al bot. Luego de esto, el bot estará creado y podremos obtener el token para la conexión.

- *Se deben instalar las dependencias necesarias:*
    - pip install telebot
    - pip install mysql-connector-python

- *Configuracion de la base de datos:*
    - CREATE DATABASE telegram_bot;
    - USE telegram_bot;
    - CREATE TABLE contador (
        user_id BIGINT PRIMARY KEY,
        count INT NOT NULL
    );

    user_id: Almacena el id único de cada usuario. Definido como BIGINT para manejar valores grandes y establecido como PRIMARY KEY para asegurar unicidad.
    
    count: Almacena el valor del contador asociado a cada usuario. Definido como INT NOT NULL para asegurar siempre un valor presente.

-Por último, la obtención y sustitución en el código de los tokens pertinentes para cada API y credenciales necesarias.

Para la ejecución del bot, utilizaremos el siguiente comando: python3 main.py.

Flujo del bot:
<img width="3200" alt="Untitled (1)" src="https://github.com/user-attachments/assets/aa36aae1-9ab8-4557-9749-a9c1f2655083">

