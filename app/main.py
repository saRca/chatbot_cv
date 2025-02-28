from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Dict
from loguru import logger

from app.services.chat_service import ChatService
from app.models.chat import ChatSession, Message

app = FastAPI(
    title="CV ATS-Friendly Generator",
    description="API para generar hojas de vida optimizadas para sistemas ATS",
    version="1.0.0"
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia global del servicio de chat
chat_service = ChatService()

# Diccionario para almacenar las sesiones activas
active_sessions = {}

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/chat/start")
async def start_chat():
    """Inicia una nueva sesión de chat"""
    try:
        session = ChatSession()
        session_id = session.session_id
        active_sessions[session_id] = session
        logger.info(f"Nueva sesión iniciada: {session_id}")
        return {
            "response": "¡Hola! Soy tu asistente para crear un CV optimizado para ATS. Por favor escribe tu nombre para comenzar.",
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error al iniciar sesión: {str(e)}")
        return {"error": "Error al iniciar la sesión de chat"}

@app.post("/chat/message")
async def chat_message(message: dict):
    try:
        if not message or "message" not in message or "session_id" not in message:
            raise ValueError("Mensaje o session_id inválido")
            
        session_id = message["session_id"]
        logger.info(f"Recibido mensaje para sesión {session_id}: {message['message']}")
        
        session = active_sessions.get(session_id)
        if not session:
            logger.info(f"Creando nueva sesión para ID {session_id}")
            session = ChatSession()
            session.session_id = session_id  # Asignar el session_id existente
            active_sessions[session_id] = session
        
        # Agregar el mensaje del usuario a la sesión
        user_message = Message(role="user", content=message["message"])
        session.messages.append(user_message)
        
        # Procesar el mensaje y obtener la respuesta
        response = chat_service.process_message(session, message["message"])
        logger.info(f"Respuesta generada: {response}")
        
        if not response:
            raise ValueError("Respuesta vacía del servicio de chat")
            
        return {
            "response": response,
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error en el chat: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
