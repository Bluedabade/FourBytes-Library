def fix_str(text, length):
    """Convert string to fixed-length bytes (UTF-8, padded with 0x00)."""
    return text.encode("utf-8")[:length].ljust(length, b"\x00")

def from_str(b):
    """Convert fixed-length bytes to string (strip 0x00 and spaces)."""
    return b.decode("utf-8").strip("\x00 ")

def to_i32(n: int) -> bytes:
    return int(n).to_bytes(4, "little", signed=False)

def from_i32(b: bytes) -> int:
    return int.from_bytes(b, "little", signed=False)
