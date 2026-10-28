"""Une los tres componentes y ofrece un menú por consola."""
from datetime import date, timedelta

from catalogo import Catalogo
from socios import Socios
from prestamos import Prestamos, PrestamoError

desfase = [0]  # días simulados, para ver caducidades y sanciones


def hoy():
    return date.today() + timedelta(days=desfase[0])


def montar():
    catalogo, socios = Catalogo(), Socios()
    for titulo, autor, n in [("Don Quijote de la Mancha", "Cervantes", 3),
                             ("Cien años de soledad", "García Márquez", 2),
                             ("La sombra del viento", "Ruiz Zafón", 1),
                             ("Rimas y leyendas", "Bécquer", 2)]:
        catalogo.agregar(titulo, autor, n)
    return catalogo, socios, Prestamos(catalogo, socios, hoy)


def pedir_int(texto):
    try:
        return int(input(texto))
    except ValueError:
        return None


def main():
    catalogo, socios, prestamos = montar()
    while True:
        print(f"\n== Biblioteca del barrio · hoy {hoy():%d/%m/%Y} ==")
        print("1 Buscar libro   2 Alta de socio   3 Prestar   4 Devolver")
        print("5 Reservar       6 Mis préstamos   7 Avanzar días   0 Salir")
        op = input("> ").strip()
        try:
            if op == "1":
                for l in catalogo.buscar(input("Título: ")) or []:
                    print(f"  [{l['id']}] {l['titulo']} — {l['autor']} "
                          f"({l['disponibles']}/{l['total']} libres)")
            elif op == "2":
                print("Socio creado con id", socios.alta(input("Nombre: ")))
            elif op == "3":
                p = prestamos.prestar(pedir_int("Id socio: "), pedir_int("Id libro: "))
                print(f"Préstamo {p.id} hecho. Vence el {p.vence:%d/%m/%Y}.")
            elif op == "4":
                r = prestamos.devolver(pedir_int("Id préstamo: "))
                print("Devuelto.")
                if r["sancionado_hasta"]:
                    print(f"Con retraso: sancionado hasta el {r['sancionado_hasta']:%d/%m/%Y}.")
                if r["asignado"]:
                    print(f"Reserva atendida: préstamo {r['asignado'].id} para el socio {r['asignado'].socio_id}.")
            elif op == "5":
                prestamos.reservar(pedir_int("Id socio: "), pedir_int("Id libro: "))
                print("Reserva anotada.")
            elif op == "6":
                for p in prestamos.activos_de(pedir_int("Id socio: ")):
                    print(f"  préstamo {p.id}: libro {p.libro_id}, vence {p.vence:%d/%m/%Y}")
            elif op == "7":
                desfase[0] += pedir_int("Días: ") or 0
            elif op == "0":
                break
        except (PrestamoError, ValueError, TypeError) as e:
            print("No se pudo:", e)


if __name__ == "__main__":
    main()