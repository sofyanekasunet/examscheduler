"""Lightweight log capture for Streamlit UI."""
import io

_buf = io.StringIO()

def log(msg: str):
    _buf.write(msg + "\n")

def get_log_buffer():
    return _buf

def reset_log_buffer():
    global _buf
    _buf = io.StringIO()