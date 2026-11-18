
import io
import math
import struct
import hashlib
import wave

from pathlib import Path
from PIL import Image


MAGIC = b"SONORA01"
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
HEADER_FORMAT = ">8sHQ32s"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pack_file(filename: str, data: bytes) -> bytes:
    if len(data) > MAX_FILE_SIZE:
        raise ValueError("File exceeds the 25 MB limit.")

    name = Path(filename).name.encode("utf-8")

    if len(name) > 65535:
        raise ValueError("Filename is too long.")

    digest = hashlib.sha256(data).digest()

    header = struct.pack(
        HEADER_FORMAT,
        MAGIC,
        len(name),
        len(data),
        digest
    )

    return header + name + data


def unpack_file(blob: bytes):
    if len(blob) < HEADER_SIZE:
        raise ValueError("Carrier is too small.")

    magic, name_length, data_length, digest = struct.unpack(
        HEADER_FORMAT,
        blob[:HEADER_SIZE]
    )

    if magic != MAGIC:
        raise ValueError("This is not a SONORA carrier.")

    if data_length > MAX_FILE_SIZE:
        raise ValueError("Stored file exceeds the size limit.")

    start = HEADER_SIZE
    name_end = start + name_length
    data_end = name_end + data_length

    if data_end > len(blob):
        raise ValueError("Carrier is incomplete or corrupted.")

    filename = blob[start:name_end].decode("utf-8")
    data = blob[name_end:data_end]

    if hashlib.sha256(data).digest() != digest:
        raise ValueError("Integrity check failed.")

    return filename, data, digest.hex()


# --------------------------
# File -> WAV
# --------------------------

def encode_wav(filename: str, data: bytes) -> bytes:
    blob = pack_file(filename, data)

    # WAV 8-bit PCM samples are unsigned bytes.
    samples = blob

    output = io.BytesIO()

    with wave.open(output, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(1)
        wav.setframerate(8000)
        wav.writeframes(samples)

    return output.getvalue()


# --------------------------
# WAV -> File
# --------------------------

def decode_wav(data: bytes):
    try:
        with wave.open(io.BytesIO(data), "rb") as wav:
            if wav.getnchannels() != 1:
                raise ValueError("SONORA WAV must be mono.")

            if wav.getsampwidth() != 1:
                raise ValueError("SONORA WAV must use 8-bit PCM.")

            if wav.getcomptype() != "NONE":
                raise ValueError("Compressed WAV is not supported.")

            samples = wav.readframes(wav.getnframes())

    except wave.Error as exc:
        raise ValueError("Invalid WAV carrier.") from exc

    return unpack_file(samples)


# --------------------------
# File -> PNG
# --------------------------

def encode_png(filename: str, data: bytes) -> bytes:
    blob = pack_file(filename, data)

    pixel_count = math.ceil(len(blob) / 3)
    side = math.ceil(math.sqrt(pixel_count))

    padded_size = side * side * 3
    blob += bytes(padded_size - len(blob))

    image = Image.frombytes("RGB", (side, side), blob)

    output = io.BytesIO()
    image.save(output, format="PNG")

    return output.getvalue()


# --------------------------
# PNG -> File
# --------------------------

def decode_png(data: bytes):
    try:
        image = Image.open(io.BytesIO(data))
        image = image.convert("RGB")
        blob = image.tobytes()

    except Exception as exc:
        raise ValueError("Invalid PNG carrier.") from exc

    return unpack_file(blob)

