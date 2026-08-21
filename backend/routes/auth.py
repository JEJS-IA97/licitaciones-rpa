from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import os
import bcrypt
from config.database import get_db

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mi_clave_super_secreta_cambia_esto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 día

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Error de conexión a MongoDB")

    # Buscar usuario por email
    user = db.users.find_one({"email": request.email})

    if not user:
        # Crear usuario con las credenciales proporcionadas
        hashed = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
        db.users.insert_one({
            "email": request.email,
            "password": hashed,
            "nombre": "Usuario",
            "rol": "user"
        })
        # Volver a buscar
        user = db.users.find_one({"email": request.email})
        if not user:
            raise HTTPException(status_code=500, detail="Error al crear usuario")

    # Verificar contraseña
    if "password" not in user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not bcrypt.checkpw(request.password.encode('utf-8'), user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Generar token JWT
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "nombre": user.get("nombre", ""),
            "rol": user.get("rol", "user")
        }
    }