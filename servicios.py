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
