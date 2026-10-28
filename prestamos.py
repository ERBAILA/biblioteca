"""Préstamos: aplica las reglas. Solo usa las funciones públicas de Catalogo y Socios."""
from datetime import date, timedelta

MAX_LIBROS = 2
DIAS_PRESTAMO = 7


class PrestamoError(Exception):
    pass


class Prestamo:
    def __init__(self, id, socio_id, libro_id, ejemplar_id, desde):
        self.id = id
        self.socio_id = socio_id
        self.libro_id = libro_id
        self.ejemplar_id = ejemplar_id
        self.desde = desde
        self.vence = desde + timedelta(days=DIAS_PRESTAMO)
        self.devuelto = None

    @property
    def activo(self):
        return self.devuelto is None


class Prestamos:
    def __init__(self, catalogo, socios, hoy=date.today):
        self._catalogo = catalogo
        self._socios = socios
        self._hoy = hoy              # reloj inyectable, útil para probar caducidades
        self._prestamos = {}
        self._reservas = []          # cola de (socio_id, libro_id)
        self._siguiente = 1

    def activos_de(self, socio_id):
        return [p for p in self._prestamos.values() if p.socio_id == socio_id and p.activo]

    def _validar_socio(self, socio_id):
        if self._socios.obtener(socio_id) is None:
            raise PrestamoError("El socio no existe.")
        if self._socios.esta_sancionado(socio_id, self._hoy()):
            raise PrestamoError("El socio está sancionado y no puede pedir libros.")

    def prestar(self, socio_id, libro_id):
        self._validar_socio(socio_id)
        if self._catalogo.obtener(libro_id) is None:
            raise PrestamoError("El libro no existe.")
        activos = self.activos_de(socio_id)
        if len(activos) >= MAX_LIBROS:
            raise PrestamoError(f"Un socio no puede tener más de {MAX_LIBROS} libros a la vez.")
        if any(p.libro_id == libro_id for p in activos):
            raise PrestamoError("El socio ya tiene un ejemplar de ese título.")
        ejemplar = self._catalogo.marcar_prestado(libro_id)
        if ejemplar is None:
            raise PrestamoError("No quedan ejemplares libres. Puedes reservarlo.")
        p = Prestamo(self._siguiente, socio_id, libro_id, ejemplar, self._hoy())
        self._prestamos[p.id] = p
        self._siguiente += 1
        return p

    def reservar(self, socio_id, libro_id):
        self._validar_socio(socio_id)
        libro = self._catalogo.obtener(libro_id)
        if libro is None:
            raise PrestamoError("El libro no existe.")
        if libro["disponibles"] > 0:
            raise PrestamoError("Hay ejemplares libres: pídelo prestado directamente.")
        if (socio_id, libro_id) in self._reservas:
            raise PrestamoError("Ya tienes una reserva de ese título.")
        self._reservas.append((socio_id, libro_id))

    def devolver(self, prestamo_id):
        """Devuelve un préstamo. Sanciona si hay retraso y atiende la cola de reservas."""
        p = self._prestamos.get(prestamo_id)
        if p is None or not p.activo:
            raise PrestamoError("Ese préstamo no existe o ya está devuelto.")
        hoy = self._hoy()
        p.devuelto = hoy
        self._catalogo.marcar_devuelto(p.ejemplar_id)
        sancion = None
        if hoy > p.vence:   # un día de sanción por cada día de retraso
            sancion = hoy + timedelta(days=(hoy - p.vence).days)
            self._socios.sancionar(p.socio_id, sancion)
        return {"sancionado_hasta": sancion, "asignado": self._atender_reservas(p.libro_id)}

    def _atender_reservas(self, libro_id):
        for reserva in [r for r in self._reservas if r[1] == libro_id]:
            self._reservas.remove(reserva)
            try:
                return self.prestar(*reserva)   # primera reserva que cumpla las reglas
            except PrestamoError:
                continue                        # si no puede (sancionado, 2 libros) pierde su turno
        return None