# bot/models/_types.py
from sqlalchemy.dialects.postgresql import ENUM

# Wrapper to reuse existing DB enum without recreating it

def pg_enum(py_enum_cls, name: str):
    return ENUM(  # noqa: S603 – server‑side enum
        *[member.value for member in py_enum_cls],
        name=name,
        create_type=False,
        native_enum=True,
    )