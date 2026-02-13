from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.auth.router import auth_router      
from src.tickets.router import user_route
import uvicorn
app = FastAPI()
app.include_router(auth_router)
app.include_router(user_route)

# (we can change to specific urls in production), but for now available for all
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

    


if __name__ == "__main__":
    uvicorn.run(app=app)
