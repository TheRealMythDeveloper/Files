
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from sonora import (
    encode_wav,
    encode_png,
    decode_wav,
    decode_png,
    sha256,
    MAX_FILE_SIZE,
)

app = FastAPI(title="SONORA API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this to our frontend later
    allow_methods=["*"],
    allow_headers=["*"],
)


async def read_upload(file: UploadFile) -> bytes:
    data = await file.read(MAX_FILE_SIZE + 1)

    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 25 MB limit."
        )

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Empty files are not supported."
        )

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
        "version": "0.1.0",
        "status": "online",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# Any file -> WAV carrier
@app.post("/encode/wav")
async def to_wav(file: UploadFile = File(...)):
    data = await read_upload(file)

    try:
        result = encode_wav(file.filename or "file.bin", data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return carrier_response(
        result,
        "sonora-carrier.wav",
        "audio/wav",
    )


# Any file -> PNG carrier
@app.post("/encode/png")
async def to_png(file: UploadFile = File(...)):
    data = await read_upload(file)

    try:
        result = encode_png(file.filename or "file.bin", data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return carrier_response(
        result,
        "sonora-carrier.png",
        "image/png",
    )


# SONORA WAV -> original file
@app.post("/decode/wav")
async def from_wav(file: UploadFile = File(...)):
    data = await read_upload(file)

    try:
        result = decode_wav(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return recovered_response(result)


# SONORA PNG -> original file
@app.post("/decode/png")
async def from_png(file: UploadFile = File(...)):
    data = await read_upload(file)

    try:
        result = decode_png(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return recovered_response(result)


# Verify arbitrary files by comparing SHA-256 hashes
@app.post("/verify")
async def verify(
    original: UploadFile = File(...),
    recovered: UploadFile = File(...),
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
        "recovered_size": len(recovered_data),
    }
