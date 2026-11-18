

import hashlib
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import os
print("CURRENT DIRECTORY:", os.getcwd())
print("FILES HERE:", os.listdir("."))
from sonora import (
    encode_wav,
    decode_wav,
    encode_png,
    decode_png,
    sha256,
    MAX_FILE_SIZE
)

app = FastAPI(
    title="SONORA",
    description="Reversible file storage through image and audio carriers.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_SIZE = MAX_FILE_SIZE + 1024 * 1024


async def read_upload(file: UploadFile) -> bytes:
    data = await file.read(MAX_UPLOAD_SIZE + 1)

    if len(data) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Upload too large.")

    if not data:
        raise HTTPException(status_code=400, detail="Empty file.")

    return data


def carrier_response(data: bytes, filename: str, media_type: str):
    return Response(
        content=data,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-SONORA-SHA256": sha256(data),
        },
    )


def recovered_response(result):
    filename, data, digest = result

    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": 'attachment; filename="recovered.bin"',
            "X-SONORA-Filename": filename,
            "X-SONORA-SHA256": digest,
        },
    )


@app.get("/")
def home():
    return {
        "name": "SONORA",
        "version": "1.0.0",
        "status": "online",
        "message": "Reversible file storage through image and audio carriers."
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/encode/wav")
async def file_to_wav(file: UploadFile = File(...)):
    data = await read_upload(file)

    try:
        result = encode_wav(file.filename or "file.bin", data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return carrier_response(result, "sonora.wav", "audio/wav")


@app.post("/encode/png")
async def file_to_png(file: UploadFile = File(...)):
    data = await read_upload(file)

    try:
        result = encode_png(file.filename or "file.bin", data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return carrier_response(result, "sonora.png", "image/png")


@app.post("/decode/wav")
async def wav_to_file(file: UploadFile = File(...)):
    data = await read_upload(file)

    try:
        result = decode_wav(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return recovered_response(result)


@app.post("/decode/png")
async def png_to_file(file: UploadFile = File(...)):
    data = await read_upload(file)

    try:
        result = decode_png(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return recovered_response(result)


@app.post("/verify")
async def verify_files(
    original: UploadFile = File(...),
    recovered: UploadFile = File(...)
):
    original_data = await read_upload(original)
    recovered_data = await read_upload(recovered)

    original_hash = sha256(original_data)
    recovered_hash = sha256(recovered_data)

    return {
        "match": original_hash == recovered_hash,
        "original_sha256": original_hash,
        "recovered_sha256": recovered_hash,
        "original_size": len(original_data),
        "recovered_size": len(recovered_data)
    }
