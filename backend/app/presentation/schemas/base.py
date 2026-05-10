from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Schema base para todos los DTOs de I/O del proyecto.
    `extra="forbid"` rechaza campos no declarados (anti spec drift).
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
