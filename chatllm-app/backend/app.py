# app.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import json
from datetime import datetime
import os
import asyncio

# Importa la biblioteca para tu LLM local
# Por ejemplo, para usar llama-cpp-python:
from llama_cpp import Llama

app = FastAPI()

# Configurar CORS para permitir peticiones desde tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Ajusta según donde se ejecute tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta donde se guardarán las conversaciones
CONVERSATIONS_DIR = "conversations"
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

# Inicializar el modelo LLM (ajusta según tu modelo específico)
# Ejemplo con llama.cpp
MODEL_PATH = "C:/models/llama-2-7b.Q2_K.gguf"

 # Cambia esto a la ruta de tu modelo
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,  # Tamaño de contexto
    n_threads=4  # Número de hilos para inferencia
)

# Modelos de datos
class Message(BaseModel):
    id: Optional[str] = None
    text: str
    sender: str
    timestamp: Optional[datetime] = None

class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Message]
    timestamp: datetime
    last_message: str

class MessageRequest(BaseModel):
    conversation_id: Optional[str] = None
    text: str

class ConversationResponse(BaseModel):
    id: str
    title: str
    preview: str
    timestamp: datetime

# Almacenamiento de conversaciones en memoria
conversations: Dict[str, Conversation] = {}

# Generar respuesta del LLM
async def generate_llm_response(conversation_id: str, user_message: str) -> str:
    # Construir el historial de la conversación para dar contexto al modelo
    conversation_history = ""
    if conversation_id in conversations:
        for msg in conversations[conversation_id].messages:
            prefix = "User: " if msg.sender == "user" else "Assistant: "
            conversation_history += f"{prefix}{msg.text}\n"
    
    # Agregar el mensaje actual
    prompt = f"{conversation_history}User: {user_message}\nAssistant:"
    
    # Generar respuesta del modelo
    response = llm(
        prompt=prompt,
        max_tokens=512,
        stop=["User:", "\n\n"],
        echo=False
    )
    
    # Extraer y limpiar la respuesta
    return response['choices'][0]['text'].strip()

# Guardar conversación en disco
def save_conversation(conversation_id: str):
    conv = conversations[conversation_id]
    file_path = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
    
    with open(file_path, "w") as f:
        # Convertir objetos datetime a strings para serialización JSON
        conv_dict = conv.dict()
        conv_dict["timestamp"] = conv_dict["timestamp"].isoformat()
        
        # Convertir mensajes
        for msg in conv_dict["messages"]:
            if msg["timestamp"]:
                msg["timestamp"] = msg["timestamp"].isoformat()
        
        json.dump(conv_dict, f)

# Cargar todas las conversaciones al iniciar
def load_conversations():
    if not os.path.exists(CONVERSATIONS_DIR):
        return
    
    for filename in os.listdir(CONVERSATIONS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(CONVERSATIONS_DIR, filename)
            with open(file_path, "r") as f:
                conv_data = json.load(f)
                
                # Convertir strings a datetime
                conv_data["timestamp"] = datetime.fromisoformat(conv_data["timestamp"])
                
                # Convertir mensajes
                for msg in conv_data["messages"]:
                    if msg["timestamp"]:
                        msg["timestamp"] = datetime.fromisoformat(msg["timestamp"])
                
                conversation = Conversation(**conv_data)
                conversations[conversation.id] = conversation

@app.on_event("startup")
async def startup_event():
    load_conversations()

# Rutas API

@app.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations():
    """Obtener lista de todas las conversaciones"""
    result = []
    for conv_id, conv in sorted(
        conversations.items(), 
        key=lambda x: x[1].timestamp, 
        reverse=True
    ):
        result.append(ConversationResponse(
            id=conv_id,
            title=conv.title,
            preview=conv.last_message,
            timestamp=conv.timestamp
        ))
    return result

@app.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """Obtener una conversación específica por ID"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return conversations[conversation_id]

@app.post("/messages", response_model=Message)
async def send_message(request: MessageRequest):
    """Enviar un mensaje y obtener respuesta del LLM"""
    now = datetime.now()
    
    # Crear nueva conversación si no se proporciona ID
    if not request.conversation_id:
        conversation_id = str(uuid.uuid4())
        conversations[conversation_id] = Conversation(
            id=conversation_id,
            title=f"Conversación {len(conversations) + 1}",
            messages=[],
            timestamp=now,
            last_message=request.text[:30] + "..." if len(request.text) > 30 else request.text
        )
    else:
        conversation_id = request.conversation_id
        if conversation_id not in conversations:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Agregar mensaje del usuario
    user_message = Message(
        id=str(uuid.uuid4()),
        text=request.text,
        sender="user",
        timestamp=now
    )
    conversations[conversation_id].messages.append(user_message)
    conversations[conversation_id].last_message = request.text[:30] + "..." if len(request.text) > 30 else request.text
    conversations[conversation_id].timestamp = now
    
    # Generar respuesta del LLM
    bot_response_text = await generate_llm_response(conversation_id, request.text)
    
    # Agregar respuesta del bot
    bot_message = Message(
        id=str(uuid.uuid4()),
        text=bot_response_text,
        sender="bot",
        timestamp=datetime.now()
    )
    conversations[conversation_id].messages.append(bot_message)
    conversations[conversation_id].last_message = bot_response_text[:30] + "..." if len(bot_response_text) > 30 else bot_response_text
    
    # Guardar conversación
    save_conversation(conversation_id)
    
    return bot_message

@app.put("/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(conversation_id: str, title: str):
    """Actualizar el título de una conversación"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    conversations[conversation_id].title = title
    save_conversation(conversation_id)
    
    return conversations[conversation_id]

@app.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: str):
    """Eliminar una conversación"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Eliminar del diccionario en memoria
    del conversations[conversation_id]
    
    # Eliminar archivo
    file_path = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)