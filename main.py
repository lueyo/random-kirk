# Reagregar imports necesarios

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import datetime
import base64
from io import BytesIO

import KirkService


app = FastAPI(
    title="KirkScrapping API",
    description="API para generar y descargar imágenes procesadas por kirkify.wtf usando una imagen de thispersondoesnotexist.com.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kirkService = KirkService.KirkiFAI()


@app.get("/ping")
async def pong():
    return {"ping": "pong"}

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("favicon.png")

@app.get(
    "/",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Imagen PNG procesada por kirkify.wtf.",
        },
        400: {
            "description": "Petición inválida. El parámetro 'size' debe estar entre 1 y 1024."
        },
        502: {"description": "No se pudo obtener la imagen procesada."},
        500: {"description": "Error interno del servidor."},
    },
    summary="Obtener imagen procesada",
    description="Devuelve una imagen PNG generada y procesada por kirkify.wtf usando una imagen aleatoria. El parámetro 'size' define el tamaño cuadrado de la imagen (por defecto 248, máximo 1024).",
)
async def get(
    size: int = Query(
        248,
        ge=1,
        le=1024,
        description="Tamaño cuadrado de la imagen en píxeles (1-1024).",
    )
):
    """
    Devuelve una imagen PNG procesada por kirkify.wtf.
    - **size**: Tamaño cuadrado de la imagen en píxeles (por defecto 248, máximo 1024).
    """
    try:
        result = await kirkService.process_image(size=size)
        if "image" in result:
            image_base64 = result["image"]
            if image_base64.startswith("data:image/png;base64,"):
                image_base64 = image_base64.replace("data:image/png;base64,", "")
            image_bytes = base64.b64decode(image_base64)
            return StreamingResponse(BytesIO(image_bytes), media_type="image/png")
        else:
            # Error normalizado para el usuario
            raise HTTPException(
                status_code=502, detail="No se pudo obtener la imagen procesada."
            )
    except HTTPException as e:
        raise e
    except Exception:
        # Error normalizado para el usuario
        raise HTTPException(
            status_code=500, detail="Error interno del servidor. Inténtalo más tarde."
        )


@app.get(
    "/download",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Descarga la imagen PNG procesada por kirkify.wtf.",
        },
        400: {
            "description": "Petición inválida. El parámetro 'size' debe estar entre 1 y 1024."
        },
        502: {"description": "No se pudo obtener la imagen procesada."},
        500: {"description": "Error interno del servidor."},
    },
    summary="Descargar imagen procesada",
    description="Descarga la imagen PNG generada y procesada por kirkify.wtf usando una imagen aleatoria. El parámetro 'size' define el tamaño cuadrado de la imagen (por defecto 248, máximo 1024). El archivo tendrá el nombre kirk-lueyo-es{timestamp}.png.",
)
async def download(
    size: int = Query(
        248,
        ge=1,
        le=1024,
        description="Tamaño cuadrado de la imagen en píxeles (1-1024).",
    )
):
    """
    Descarga la imagen PNG procesada por kirkify.wtf.
    - **size**: Tamaño cuadrado de la imagen en píxeles (por defecto 248, máximo 1024).
    """
    try:
        result = await kirkService.process_image(size=size)
        if "image" in result:
            image_base64 = result["image"]
            if image_base64.startswith("data:image/png;base64,"):
                image_base64 = image_base64.replace("data:image/png;base64,", "")
            image_bytes = base64.b64decode(image_base64)
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            image_name = f"kirk-lueyo-es{timestamp}.png"
            return StreamingResponse(
                BytesIO(image_bytes),
                media_type="image/png",
                headers={"Content-Disposition": f"attachment; filename={image_name}"},
            )
        else:
            raise HTTPException(
                status_code=502, detail="No se pudo obtener la imagen procesada."
            )
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=500, detail="Error interno del servidor. Inténtalo más tarde."
        )
