"""Socios: altas, consulta y sanciones."""


class Socio:
    """Persona con identidad (id) y estado (sancionado hasta una fecha)."""

    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.sancionado_hasta = None


class Socios:
    def __init__(self):
        self._socios = {}
        self._siguiente = 1

    def alta(self, nombre):
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacío.")
        socio = Socio(self._siguiente, nombre)
        self._socios[socio.id] = socio
        self._siguiente += 1
        return socio.id

    def obtener(self, id):
        s = self._socios.get(id)
        if s is None:
            return None
        return {"id": s.id, "nombre": s.nombre, "sancionado_hasta": s.sancionado_hasta}

    def sancionar(self, id, hasta):
        s = self._socios[id]
        if s.sancionado_hasta is None or hasta > s.sancionado_hasta:
            s.sancionado_hasta = hasta

    def esta_sancionado(self, id, hoy):
        s = self._socios.get(id)
        return bool(s and s.sancionado_hasta and s.sancionado_hasta >= hoy)