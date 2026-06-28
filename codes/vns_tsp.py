"""
Búsqueda de Vecindad Variable (VNS) aplicada al Problema del Agente Viajero (TSP).

Metaheurística:  Variable Neighborhood Search (VNS)
Problema:        Traveling Salesman Problem (TSP)
Paper base:      Mladenović, N. & Hansen, P. (1997). "Variable neighborhood search".
                 Computers & Operations Research, 24(11), 1097-1100.
                 DOI: 10.1016/S0305-0548(97)00031-2

Idea del algoritmo (VNS básico):
  1. Partimos de una solución (un tour cualquiera) y le aplicamos búsqueda local.
  2. Definimos una familia de vecindades N_1, N_2, ..., N_kmax cada vez "más grandes".
  3. En cada paso:
        - SHAKING: saltamos a un punto aleatorio de la vecindad N_k (perturbación).
        - BÚSQUEDA LOCAL: bajamos al óptimo local más cercano con 2-opt.
        - CAMBIO DE VECINDAD: si mejoramos, nos movemos y reiniciamos k=1;
          si no, agrandamos la vecindad (k = k+1).
  Así combinamos exploración (shaking) y explotación (búsqueda local).

Ejecutar:  python codes/vns_tsp.py
Genera:    slides/figures/vns_tour_inicial.png
           slides/figures/vns_tour_final.png
           slides/figures/vns_convergencia.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend sin ventana, para guardar PNG
import matplotlib.pyplot as plt

# Carpeta donde guardamos las figuras (relativa a este archivo -> ../slides/figures)
FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "slides", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Semilla fija para que el ejemplo sea siempre reproducible.
rng = np.random.default_rng(7)


# --------------------------------------------------------------------------- #
# 1. Instancia del problema: 10 ciudades con coordenadas fijas
# --------------------------------------------------------------------------- #
CITIES = np.array([
    [0.10, 0.20], [0.90, 0.10], [0.60, 0.30], [0.40, 0.70], [0.10, 0.90],
    [0.85, 0.85], [0.50, 0.50], [0.20, 0.55], [0.75, 0.45], [0.35, 0.15],
])
N = len(CITIES)


def distance_matrix(cities):
    """Matriz de distancias euclídeas entre todas las ciudades."""
    diff = cities[:, None, :] - cities[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=2))


D = distance_matrix(CITIES)


def tour_length(tour):
    """Longitud total del ciclo cerrado que visita las ciudades en ese orden."""
    return sum(D[tour[i], tour[(i + 1) % len(tour)]] for i in range(len(tour)))


# --------------------------------------------------------------------------- #
# 2. Búsqueda local: 2-opt
#    Quita dos aristas y reconecta el tour al revés en un tramo; se queda con
#    cada mejora hasta llegar a un óptimo local.
# --------------------------------------------------------------------------- #
def two_opt(tour):
    tour = list(tour)
    mejorado = True
    while mejorado:
        mejorado = False
        for i in range(1, len(tour) - 1):
            for j in range(i + 1, len(tour)):
                if j - i == 1:
                    continue
                nuevo = tour[:i] + tour[i:j][::-1] + tour[j:]
                if tour_length(nuevo) < tour_length(tour) - 1e-12:
                    tour = nuevo
                    mejorado = True
    return tour


# --------------------------------------------------------------------------- #
# 3. Shaking: perturbación aleatoria en la vecindad N_k
#    N_k = aplicar k intercambios aleatorios de pares de ciudades.
#    A mayor k, el salto es más grande (vecindad más amplia).
# --------------------------------------------------------------------------- #
def shake(tour, k):
    nuevo = list(tour)
    for _ in range(k):
        a, b = rng.integers(0, len(nuevo), size=2)
        nuevo[a], nuevo[b] = nuevo[b], nuevo[a]
    return nuevo


# --------------------------------------------------------------------------- #
# 4. VNS básico
# --------------------------------------------------------------------------- #
def vns(tour_inicial, k_max=5, max_iter=60, verbose=True):
    # Solución actual = óptimo local de la solución inicial.
    actual = two_opt(tour_inicial)
    mejor_long = tour_length(actual)
    historia = [mejor_long]

    if verbose:
        print(f"Tour inicial (tras 2-opt): {actual}")
        print(f"Longitud inicial: {mejor_long:.4f}\n")
        print(f"{'iter':>4} {'k':>2} {'cand.':>9} {'¿mejora?':>9}")
        print("-" * 30)

    it = 0
    while it < max_iter:
        k = 1
        while k <= k_max:
            it += 1
            candidato = shake(actual, k)            # exploración
            candidato = two_opt(candidato)          # explotación
            long_cand = tour_length(candidato)

            if long_cand < mejor_long - 1e-12:      # cambio de vecindad
                actual, mejor_long = candidato, long_cand
                historia.append(mejor_long)
                if verbose:
                    print(f"{it:>4} {k:>2} {long_cand:>9.4f} {'SÍ -> k=1':>9}")
                k = 1                               # volvemos a la vecindad más chica
            else:
                historia.append(mejor_long)
                if verbose:
                    print(f"{it:>4} {k:>2} {long_cand:>9.4f} {'no, k+1':>9}")
                k += 1                              # agrandamos la vecindad
            if it >= max_iter:
                break

    if verbose:
        print("\nTour final:", actual)
        print(f"Longitud final: {mejor_long:.4f}")
    return actual, mejor_long, historia


# --------------------------------------------------------------------------- #
# 5. Gráficas
# --------------------------------------------------------------------------- #
def plot_tour(tour, titulo, archivo):
    fig, ax = plt.subplots(figsize=(5, 5))
    orden = tour + [tour[0]]
    xs, ys = CITIES[orden, 0], CITIES[orden, 1]
    ax.plot(xs, ys, "-o", color="#2c7fb8", zorder=1)
    for idx, (x, y) in enumerate(CITIES):
        ax.annotate(str(idx), (x, y), textcoords="offset points",
                    xytext=(6, 6), fontsize=10, weight="bold")
    ax.set_title(f"{titulo}\nlongitud = {tour_length(tour):.4f}")
    ax.set_xlabel("x"); ax.set_ylabel("y")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, archivo), dpi=130)
    plt.close(fig)


def plot_convergencia(historia, archivo):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(historia, color="#d95f0e")
    ax.set_title("Convergencia de VNS")
    ax.set_xlabel("iteración"); ax.set_ylabel("mejor longitud")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, archivo), dpi=130)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 6. Programa principal
# --------------------------------------------------------------------------- #
def main():
    print("=" * 60)
    print(" VNS aplicado al TSP  -  ejemplo paso a paso")
    print("=" * 60)

    tour_inicial = list(rng.permutation(N))
    print(f"Tour aleatorio de partida: {tour_inicial}")
    print(f"Longitud de partida: {tour_length(tour_inicial):.4f}\n")

    plot_tour(tour_inicial, "Tour inicial (aleatorio)", "vns_tour_inicial.png")

    final, long_final, historia = vns(tour_inicial)

    plot_tour(final, "Tour final (VNS)", "vns_tour_final.png")
    plot_convergencia(historia, "vns_convergencia.png")

    mejora = 100 * (tour_length(tour_inicial) - long_final) / tour_length(tour_inicial)
    print(f"\nMejora respecto al tour de partida: {mejora:.1f} %")
    print(f"Figuras guardadas en: {os.path.abspath(FIG_DIR)}")


if __name__ == "__main__":
    main()
