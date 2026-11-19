"""Clase abstracta base y Cliente (con encapsulación y validaciones)."""
import re
from abc import ABC, abstractmethod

from excepciones import ClienteInvalidoError, ParametroFaltanteError

_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


class EntidadBase(ABC):
    """Abstracción de cualquier entidad general del sistema."""

    _contador = 0

    def __init__(self):
        EntidadBase._contador += 1
        self._id = EntidadBase._contador

    @property
    def id(self) -> int:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        ...

    def __str__(self):
        return self.describir()


class Cliente(EntidadBase):
    def __init__(self, nombre=None, documento=None, email=None, telefono=None):
        super().__init__()
        if nombre is None or documento is None or email is None:
            raise ParametroFaltanteError("Nombre, documento y email son obligatorios.")
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.telefono = telefono

    # --- propiedades con validación (encapsulación) ---
    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, v):
        if not isinstance(v, str) or len(v.strip()) < 3 or any(c.isdigit() for c in v):
            raise ClienteInvalidoError(f"Nombre inválido: {v!r}")
        self.__nombre = v.strip().title()

    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, v):
        if not str(v).isdigit() or not 6 <= len(str(v)) <= 12:
            raise ClienteInvalidoError(f"Documento inválido: {v!r}")
        self.__documento = str(v)

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, v):
        if not isinstance(v, str) or not _EMAIL.match(v):
            raise ClienteInvalidoError(f"Email inválido: {v!r}")
        self.__email = v.lower()

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, v):
        if v is not None and (not str(v).isdigit() or len(str(v)) != 10):
            raise ClienteInvalidoError(f"Teléfono inválido (10 dígitos): {v!r}")
        self.__telefono = None if v is None else str(v)

    def describir(self):
        return f"Cliente #{self.id}: {self.nombre} (CC {self.documento}, {self.email})"

