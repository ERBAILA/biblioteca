"""Catálogo: guarda libros y sus ejemplares. Solo se accede por funciones públicas."""


class Ejemplar:
    """Copia física de un libro, con identidad y estado propios."""

    def __init__(self, id, libro_id):
        self.id = id
        self.libro_id = libro_id
        self.prestado = False


class Libro:
    """Un título con identidad; su estado son sus ejemplares."""

    def __init__(self, id, titulo, autor):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.ejemplares = []

    def ejemplar_libre(self):
        return next((e for e in self.ejemplares if not e.prestado), None)


class Catalogo:
    def __init__(self):
        self._libros = {}      # privado: nadie fuera de este fichero lo toca
        self._siguiente_libro = 1
        self._siguiente_ejemplar = 1

    def agregar(self, titulo, autor, ejemplares=1):
        libro = Libro(self._siguiente_libro, titulo, autor)
        self._siguiente_libro += 1
        for _ in range(ejemplares):
            libro.ejemplares.append(Ejemplar(self._siguiente_ejemplar, libro.id))
            self._siguiente_ejemplar += 1
        self._libros[libro.id] = libro
        return libro.id

    def buscar(self, titulo):
        """Devuelve vistas (diccionarios) de los libros cuyo título contiene el texto."""
        t = titulo.strip().lower()
        return [self._vista(l) for l in self._libros.values() if t in l.titulo.lower()]

    def obtener(self, id):
        libro = self._libros.get(id)
        return self._vista(libro) if libro else None

    def marcar_prestado(self, id):
        """Reserva un ejemplar libre del libro `id`. Devuelve su id, o None si no hay."""
        libro = self._libros.get(id)
        ejemplar = libro.ejemplar_libre() if libro else None
        if ejemplar is None:
            return None
        ejemplar.prestado = True
        return ejemplar.id

    def marcar_devuelto(self, id_ejemplar):
        for libro in self._libros.values():
            for e in libro.ejemplares:
                if e.id == id_ejemplar:
                    e.prestado = False
                    return libro.id
        return None

    @staticmethod
    def _vista(libro):
        libres = sum(1 for e in libro.ejemplares if not e.prestado)
        return {"id": libro.id, "titulo": libro.titulo, "autor": libro.autor,
                "total": len(libro.ejemplares), "disponibles": libres}