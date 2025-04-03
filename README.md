🚀 Versión Experimental del Sistema

Este proyecto es una versión experimental del sistema, en la cual se utiliza un LLM (Large Language Model) básico y liviano para pruebas. En este caso, usaremos Llama 2, que es adecuado para evaluaciones iniciales.

🛠 Instalación y Configuración

1️⃣ Instalar llama para gestionar los modelos

Ejecuta el siguiente comando para instalar llama:

pip install llama-cpp-python

2️⃣ Descargar el modelo Llama 2

Utilizaremos el modelo disponible en Hugging Face:🔗 [Llama 2 - 7B GGUF](https://huggingface.co/TheBloke/Llama-2-7B-GGUF/blob/main/llama-2-7b.Q2_K.gguf)

📂 Pasos para la descarga:

Crea una carpeta en C:/ llamada models:

mkdir C:/models

Descarga el archivo llama-2-7b.Q2_K.gguf y guárdalo en C:/models.

3️⃣ Levantar el Backend

Antes de ejecutar el frontend, es necesario iniciar el backend. Sigue estos pasos:

cd backend
python app.py

Esto iniciará el servidor para que el modelo pueda ser utilizado en pruebas.

🚀 Ejecutando el Modelo

Una vez que el backend esté en ejecución, puedes utilizar el modelo desde tu aplicación o mediante peticiones a la API.
