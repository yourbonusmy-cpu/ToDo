# myapp/crypto.py

import os
import ctypes
import base64

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LIB_PATH = os.path.join(BASE_DIR, "libs", "libdes.so")

lib = ctypes.CDLL(LIB_PATH)

lib.encrypt.argtypes = [
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_int,
]

lib.decrypt.argtypes = [
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_int,
]


def encrypt_text(text: str, password: str) -> str:
    text_bytes = text.encode("utf-8")
    out = (ctypes.c_uint8 * len(text_bytes))()
    lib.encrypt(text_bytes, password.encode(), out, len(text_bytes))
    return base64.b64encode(bytes(out)).decode()


def decrypt_text(cipher_b64: str, password: str) -> str | None:
    try:
        cipher = base64.b64decode(cipher_b64)
    except Exception:
        return None

    cipher_buf = (ctypes.c_uint8 * len(cipher)).from_buffer_copy(cipher)
    out = ctypes.create_string_buffer(len(cipher) + 1)

    lib.decrypt(cipher_buf, password.encode(), out, len(cipher))

    try:
        return out.value.decode("utf-8")
    except UnicodeDecodeError:
        return None
