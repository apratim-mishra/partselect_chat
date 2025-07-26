from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import asyncio
from typing import Dict, List
import os
from datetime import datetime
from dotenv import load_dotenv

from agents.parts_agent import PartsAgent
from models.schemas import ChatMessage, ChatResponse

# Load environment variables
load_dotenv()

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

# Initialize the agent
parts_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global parts_agent
    parts_agent = PartsAgent()
    yield
    # Shutdown
    pass

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "PartSelect Chat Agent API"}

@app.post("/chat")
async def chat(message: ChatMessage):
    """Handle chat messages via REST API"""
    try:
        # Add timeout to prevent frontend timeouts
        response = await asyncio.wait_for(
            parts_agent.process_message(message.message, message.conversation_id),
            timeout=25.0  # 25 seconds to stay under frontend's 30s timeout
        )
        return ChatResponse(**response)
    except asyncio.TimeoutError:
        # Return a helpful timeout response
        return ChatResponse(
            message="I'm taking longer than usual to process your request. This might be due to high system load. Please try asking a simpler question or try again later.",
            timestamp=datetime.now().isoformat(),
            agent="PartsAgent",
            error=True
        )
    except Exception as e:
        # Handle any other errors gracefully
        print(f"Error in chat endpoint: {str(e)}")
        return ChatResponse(
            message="I encountered an error processing your request. Please try again or contact support if the issue persists.",
            timestamp=datetime.now().isoformat(),
            agent="PartsAgent",
            error=True
        )

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Handle WebSocket connections for real-time chat"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message with agent
            response = await parts_agent.process_message(
                message_data["message"], 
                client_id
            )
            
            # Send response back to client
            await manager.send_message(json.dumps(response), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client {client_id} disconnected")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}