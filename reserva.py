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
