from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import json
from datetime import datetime
import os
import asyncio
from pathlib import Path
import shutil
from typing import Any

from openai import OpenAI
import chromadb

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
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
VECTOR_DIR = "chroma_db"
os.makedirs(VECTOR_DIR, exist_ok=True)

def load_env_file():
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

load_env_file()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Falta configurar OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
chroma_client = chromadb.PersistentClient(path=VECTOR_DIR)
documents_collection = chroma_client.get_or_create_collection(name="uploaded_documents")

# Modelos de datos
class Message(BaseModel):
    id: Optional[str] = None
    text: str
    sender: str
    timestamp: Optional[datetime] = None
    embedding: Optional[List[float]] = None

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

class DocumentResponse(BaseModel):
    id: str
    name: str
    uploaded_by: str
    uploaded_at: datetime
    file_path: str

# Almacenamiento de conversaciones en memoria
conversations: Dict[str, Conversation] = {}
documents: Dict[str, DocumentResponse] = {}

# Generar respuesta del LLM
async def generate_embedding(text: str) -> List[float]:
    response = await asyncio.to_thread(
        client.embeddings.create,
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def safe_text_from_file(file_path: str) -> str:
    try:
        return Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return ""


async def index_document(document_id: str, name: str, content: str, metadata: Dict[str, Any]):
    if not content.strip():
        content = name
    embedding = await generate_embedding(content[:8000])
    documents_collection.upsert(
        ids=[document_id],
        documents=[content],
        metadatas=[metadata],
        embeddings=[embedding],
    )


async def generate_llm_response(conversation_id: str, user_message: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "Eres un asistente conversacional claro, útil y breve."
        }
    ]

    if conversation_id in conversations:
        for msg in conversations[conversation_id].messages:
            role = "assistant" if msg.sender == "bot" else "user"
            messages.append({"role": role, "content": msg.text})

    messages.append({"role": "user", "content": user_message})

    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

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
        timestamp=now,
        embedding=await generate_embedding(request.text)
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
        timestamp=datetime.now(),
        embedding=await generate_embedding(bot_response_text)
    )
    conversations[conversation_id].messages.append(bot_message)
    conversations[conversation_id].last_message = bot_response_text[:30] + "..." if len(bot_response_text) > 30 else bot_response_text
    
    
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


@app.get("/documents", response_model=List[DocumentResponse])
async def list_documents():
    return list(documents.values())


@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    uploaded_by: str = Form("Sistema")
):
    document_id = str(uuid.uuid4())
    extension = Path(file.filename).suffix
    stored_name = f"{document_id}{extension}"
    file_path = os.path.join(UPLOADS_DIR, stored_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    content = safe_text_from_file(file_path)
    now = datetime.now()
    document = DocumentResponse(
        id=document_id,
        name=file.filename,
        uploaded_by=uploaded_by,
        uploaded_at=now,
        file_path=file_path,
    )
    documents[document_id] = document
    await index_document(
        document_id=document_id,
        name=file.filename,
        content=content or file.filename,
        metadata={
            "name": file.filename,
            "uploaded_by": uploaded_by,
            "uploaded_at": now.isoformat(),
            "file_path": file_path,
        },
    )
    return document

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
