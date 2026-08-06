from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="WTI Paper Trading API")

# 1. Configuration CORS (Essentiel pour la connexion avec Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Base de données temporaire en mémoire
db = {
    "balance": 10000.0,
    "positions": []
}

# 3. Modèles de données
class OrderRequest(BaseModel):
    symbol: str = "WTI"
    side: str  # "BUY" ou "SELL"
    qty: float

class CloseRequest(BaseModel):
    position_id: int

# 4. Routes de l'API
@app.get("/")
def read_root():
    return {"status": "API WTI opérationnelle"}

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/account")
def get_account():
    return {
        "balance": db["balance"],
        "positions": db["positions"]
    }

@app.post("/order")
def place_order(order: OrderRequest):
    if order.side not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Côté invalide (BUY ou SELL)")
    
    if order.qty <= 0:
        raise HTTPException(status_code=400, detail="La quantité doit être supérieure à 0")

    position = {
        "id": len(db["positions"]),
        "symbol": order.symbol,
        "side": order.side,
        "qty": order.qty,
        "price": 75.00  # Prix simulé fixe pour l'entrée
    }
    
    db["positions"].append(position)
    return {"message": "Ordre exécuté avec succès", "position": position}

@app.post("/close")
def close_position(req: CloseRequest):
    if req.position_id < 0 or req.position_id >= len(db["positions"]):
        raise HTTPException(status_code=404, detail="Position non trouvée")
    
    closed_position = db["positions"].pop(req.position_id)
    
    # Réindexation des identifiants
    for idx, pos in enumerate(db["positions"]):
        pos["id"] = idx
        
    return {"message": "Position fermée", "closed": closed_position}
