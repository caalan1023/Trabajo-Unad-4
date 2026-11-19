"""Excepciones personalizadas de Software FJ."""


class ErrorSoftwareFJ(Exception):
    """Excepción base de todo el sistema."""


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Falta un parámetro obligatorio."""


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Datos de cliente inválidos."""


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Parámetros de servicio inválidos."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """El servicio no está disponible."""


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Intento de reserva incorrecto."""


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Operación no permitida en el estado actual."""


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Cálculo de costos con resultado inconsistente."""

"""Configuración del archivo de logs (única persistencia permitida)."""
import logging
import os

RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "software_fj.log")


def obtener_logger() -> logging.Logger:
    logger = logging.getLogger("SoftwareFJ")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        h = logging.FileHandler(RUTA_LOG, mode="w", encoding="utf-8")
        h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
        logger.addHandler(h)
    return logger


log = obtener_logger()

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

    """Servicio abstracto y tres servicios especializados."""
from abc import abstractmethod

from entidades import EntidadBase
from excepciones import (CalculoInconsistenteError, ServicioInvalidoError,
                         ServicioNoDisponibleError)

IVA = 0.19


class Servicio(EntidadBase):
    def __init__(self, nombre: str, tarifa_hora: float):
        super().__init__()
        if not isinstance(nombre, str) or not nombre.strip():
            raise ServicioInvalidoError("El servicio requiere un nombre.")
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise ServicioInvalidoError(f"Tarifa inválida: {tarifa_hora!r}")
        self._nombre = nombre
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = True

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    def deshabilitar(self):
        self._disponible = False

    def habilitar(self):
        self._disponible = True

    # --- métodos abstractos (polimorfismo) ---
    @abstractmethod
    def validar_parametros(self, duracion: float) -> None: ...

    @abstractmethod
    def calcular_costo_base(self, duracion: float) -> float: ...

    @abstractmethod
    def describir(self) -> str: ...

    # --- "sobrecarga" de calcular_costo mediante parámetros opcionales ---
    def calcular_costo(self, duracion: float, impuesto: float = 0.0,
                       descuento: float = 0.0) -> float:
        """Variantes:
        calcular_costo(h)                     -> costo base
        calcular_costo(h, impuesto=0.19)      -> con impuesto
        calcular_costo(h, descuento=0.1)      -> con descuento
        calcular_costo(h, 0.19, 0.1)          -> con ambos
        """
        self.validar_parametros(duracion)
        if not 0 <= impuesto <= 1 or not 0 <= descuento < 1:
            raise CalculoInconsistenteError(
                f"Impuesto/descuento fuera de rango: {impuesto}, {descuento}")
        total = self.calcular_costo_base(duracion) * (1 - descuento) * (1 + impuesto)
        if total <= 0:
            raise CalculoInconsistenteError("El costo calculado no es positivo.")
        return round(total, 2)

    def calcular_costo_con_iva(self, duracion: float) -> float:
        return self.calcular_costo(duracion, impuesto=IVA)

    def verificar_disponibilidad(self):
        if not self._disponible:
            raise ServicioNoDisponibleError(f"'{self._nombre}' no está disponible.")


class ReservaSala(Servicio):
    def __init__(self, nombre, capacidad, tarifa_hora=50000):
        super().__init__(nombre, tarifa_hora)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}")
        self._capacidad = capacidad

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or not 1 <= duracion <= 12:
            raise ServicioInvalidoError("Una sala se reserva entre 1 y 12 horas.")

    def calcular_costo_base(self, duracion):
        return self._tarifa_hora * duracion

    def describir(self):
        return f"Sala '{self._nombre}' (cap. {self._capacidad}) - ${self._tarifa_hora:,.0f}/h"


class AlquilerEquipo(Servicio):
    def __init__(self, nombre, unidades, tarifa_hora=20000):
        super().__init__(nombre, tarifa_hora)
        if not isinstance(unidades, int) or unidades <= 0:
            raise ServicioInvalidoError(f"Unidades inválidas: {unidades!r}")
        self._unidades = unidades

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or not 1 <= duracion <= 72:
            raise ServicioInvalidoError("El alquiler es de 1 a 72 horas.")

    def calcular_costo_base(self, duracion):
        recargo = 1.10 if duracion > 24 else 1.0  # recargo por larga duración
        return self._tarifa_hora * duracion * recargo

    def describir(self):
        return f"Equipo '{self._nombre}' ({self._unidades} u.) - ${self._tarifa_hora:,.0f}/h"


class Asesoria(Servicio):
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, nivel="junior", tarifa_hora=80000):
        super().__init__(nombre, tarifa_hora)
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(f"Nivel inválido: {nivel!r}")
        self._nivel = nivel

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or not 0.5 <= duracion <= 8:
            raise ServicioInvalidoError("La asesoría dura entre 0.5 y 8 horas.")

    def calcular_costo_base(self, duracion):
        return self._tarifa_hora * self.NIVELES[self._nivel] * duracion

    def describir(self):
        return f"Asesoría '{self._nombre}' nivel {self._nivel} - ${self._tarifa_hora:,.0f}/h"


    """Clase Reserva: integra cliente, servicio, duración y estado."""
from entidades import Cliente, EntidadBase
from excepciones import (ErrorSoftwareFJ, OperacionNoPermitidaError,
                         ReservaInvalidaError)
from registro import log
from servicios import IVA, Servicio


class Reserva(EntidadBase):
    PENDIENTE, CONFIRMADA, CANCELADA, PROCESADA = (
        "PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA")

    def __init__(self, cliente, servicio, duracion):
        super().__init__()
        try:
            if not isinstance(cliente, Cliente):
                raise TypeError("cliente debe ser instancia de Cliente")
            if not isinstance(servicio, Servicio):
                raise TypeError("servicio debe ser instancia de Servicio")
            servicio.verificar_disponibilidad()
            servicio.validar_parametros(duracion)
        except (TypeError, ErrorSoftwareFJ) as e:
            # Encadenamiento de excepciones
            raise ReservaInvalidaError(f"No se pudo crear la reserva: {e}") from e
        self._cliente, self._servicio, self._duracion = cliente, servicio, duracion
        self._estado = self.PENDIENTE
        self._costo = None

    @property
    def estado(self):
        return self._estado

    @property
    def costo(self):
        return self._costo

    def confirmar(self):
        if self._estado != self.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"Solo se confirma una reserva PENDIENTE (actual: {self._estado}).")
        self._servicio.verificar_disponibilidad()
        self._estado = self.CONFIRMADA
        log.info(f"Reserva #{self.id} CONFIRMADA")

    def cancelar(self):
        if self._estado in (self.CANCELADA, self.PROCESADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva {self._estado}.")
        self._estado = self.CANCELADA
        log.info(f"Reserva #{self.id} CANCELADA")

    def procesar(self, descuento: float = 0.0):
        """Calcula el costo final; demuestra try/except/else/finally."""
        try:
            if self._estado != self.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"Debe estar CONFIRMADA para procesar (actual: {self._estado}).")
            costo = self._servicio.calcular_costo(self._duracion, IVA, descuento)
        except ErrorSoftwareFJ as e:
            log.error(f"Reserva #{self.id} no procesada: {e}")
            raise
        else:
            self._costo = costo
            self._estado = self.PROCESADA
            log.info(f"Reserva #{self.id} PROCESADA. Total: ${costo:,.2f}")
            return costo
        finally:
            log.debug(f"Fin de procesamiento de reserva #{self.id} "
                      f"(estado: {self._estado})")

    def describir(self):
        return (f"Reserva #{self.id} [{self._estado}] {self._cliente.nombre} -> "
                f"{self._servicio.nombre} x {self._duracion}h")

"""Software FJ - Simulación de 12 operaciones (válidas e inválidas).
Ejecutar:  python main.py   (se genera software_fj.log)
"""
from entidades import Cliente
from excepciones import ErrorSoftwareFJ
from registro import log
from reserva import Reserva
from servicios import Asesoria, AlquilerEquipo, ReservaSala


class GestorFJ:
    """Gestiona clientes, servicios y reservas en listas internas."""

    def __init__(self):
        self.clientes, self.servicios, self.reservas = [], [], []

    def _intentar(self, titulo, funcion, lista=None):
        """Ejecuta una operación; si falla registra el error y continúa."""
        print(f"\n▶ {titulo}")
        log.info(f"OPERACIÓN: {titulo}")
        try:
            obj = funcion()
        except ErrorSoftwareFJ as e:
            log.error(f"{titulo} -> {type(e).__name__}: {e}"
                      + (f" | causa: {e.__cause__!r}" if e.__cause__ else ""))
            print(f"   ✖ {type(e).__name__}: {e}")
            return None
        except Exception as e:  # error inesperado: el sistema sigue vivo
            log.critical(f"{titulo} -> ERROR INESPERADO {type(e).__name__}: {e}")
            print(f"   ✖ Error inesperado controlado: {e}")
            return None
        else:
            if lista is not None:
                lista.append(obj)
            print(f"   ✔ {obj}")
            return obj
        finally:
            log.debug(f"Fin de operación: {titulo}")


def main():
    g = GestorFJ()

    # 1-3 Clientes
    ana = g._intentar("1. Registrar cliente válido (Ana)",
                      lambda: Cliente("ana gómez", "1012345678", "ana@mail.com", "3001234567"),
                      g.clientes)
    g._intentar("2. Registrar cliente con email inválido",
                lambda: Cliente("Luis Pérez", "98765432", "luis@@mail"), g.clientes)
    g._intentar("3. Registrar cliente sin documento (parámetro faltante)",
                lambda: Cliente("Pedro Ruiz", None, "pedro@mail.com"), g.clientes)
    carlos = g._intentar("4. Registrar cliente válido (Carlos)",
                         lambda: Cliente("Carlos Díaz", "80123456", "carlos@mail.com"),
                         g.clientes)

    # 5-7 Servicios
    sala = g._intentar("5. Crear sala válida",
                       lambda: ReservaSala("Sala Innovación", 12), g.servicios)
    g._intentar("6. Crear equipo con unidades inválidas",
                lambda: AlquilerEquipo("Proyector", -3), g.servicios)
    equipo = g._intentar("7. Crear alquiler de equipo válido",
                         lambda: AlquilerEquipo("Portátil Gamer", 5), g.servicios)
    asesoria = g._intentar("8. Crear asesoría válida (senior)",
                           lambda: Asesoria("Arquitectura de software", "senior"),
                           g.servicios)

    # Polimorfismo
    print("\n── Catálogo (polimorfismo) ──")
    for s in g.servicios:
        print("  •", s.describir(), "| 2h c/IVA:", f"${s.calcular_costo_con_iva(2):,.2f}")

    # 9-12 Reservas
    r1 = g._intentar("9. Reserva exitosa: Ana + sala 3h",
                     lambda: Reserva(ana, sala, 3), g.reservas)
    if r1:
        g._intentar("   9a. Confirmar", lambda: (r1.confirmar(), r1)[1])
        g._intentar("   9b. Procesar con 10% de descuento",
                    lambda: f"Total ${r1.procesar(descuento=0.10):,.2f}")
        g._intentar("   9c. Cancelar reserva ya procesada (no permitido)",
                    lambda: r1.cancelar())

    g._intentar("10. Reserva con duración inválida (sala 20h)",
                lambda: Reserva(ana, sala, 20), g.reservas)

    equipo.deshabilitar()
    g._intentar("11. Reserva de servicio no disponible",
                lambda: Reserva(carlos, equipo, 5), g.reservas)
    equipo.habilitar()

    r4 = g._intentar("12. Reserva Carlos + asesoría 2h",
                     lambda: Reserva(carlos, asesoria, 2), g.reservas)
    if r4:
        g._intentar("   12a. Procesar sin confirmar (no permitido)",
                    lambda: r4.procesar())
        g._intentar("   12b. Cancelar", lambda: r4.cancelar())

    g._intentar("13. Reserva con cliente nulo (encadenamiento)",
                lambda: Reserva(None, sala, 2), g.reservas)
    g._intentar("14. Costo con descuento inconsistente (150%)",
                lambda: sala.calcular_costo(2, 0.19, 1.5))

    print("\n── Resumen ──")
    print(f"Clientes: {len(g.clientes)} | Servicios: {len(g.servicios)} | "
          f"Reservas: {len(g.reservas)}")
    for r in g.reservas:
        print("  •", r.describir())
    print("\nEl sistema terminó sin interrupciones. Revise software_fj.log")


if __name__ == "__main__":
    main()

