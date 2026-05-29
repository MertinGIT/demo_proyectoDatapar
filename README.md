# Chatbot

Aplicacion de chat con frontend en React y backend en FastAPI.

## Configuracion

1. Instala las dependencias del frontend en `chat-app`.
2. Instala las dependencias del backend Python, incluyendo `fastapi`, `uvicorn` y `openai`.
3. Define la variable de entorno `OPENAI_API_KEY`.
4. Opcionalmente configura:
   - `OPENAI_CHAT_MODEL` con valor por defecto `gpt-4o`
   - `OPENAI_EMBEDDING_MODEL` con valor por defecto `text-embedding-3-small`

## Backend

El backend usa OpenAI para el chat con `gpt-4o`.

Para embeddings se utiliza un modelo de embeddings de OpenAI, porque `gpt-4o` no expone embeddings directamente.

## Frontend

El frontend ya no muestra referencias a Datapar y usa una paleta oscura con acentos azules/cian.
