from fastapi import FastAPI, UploadFile, File, HTTPException
import cv2
import numpy as np

from measure_object_size import analisar_imagem


app = FastAPI()


@app.post("/analisar")
async def analisar(file: UploadFile = File(...)):

    imagem_bytes = await file.read()

    imagem_array = np.frombuffer(imagem_bytes, np.uint8)

    imagem = cv2.imdecode(
        imagem_array,
        cv2.IMREAD_COLOR
    )

    if imagem is None:
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado não é uma imagem válida."
        )

    resultado = analisar_imagem(imagem)

    return resultado