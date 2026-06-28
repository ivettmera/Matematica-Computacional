"""
Optimización por Enjambre de Partículas (PSO) para minimizar una función continua.

Metaheurística:  Particle Swarm Optimization (PSO)
Problema:        Minimizar una función benchmark (por defecto Rastrigin en 2D).
Papers base:     Kennedy, J. & Eberhart, R. (1995). "Particle swarm optimization".
                 Proc. IEEE Int. Conf. on Neural Networks, 1942-1948.
                 DOI: 10.1109/ICNN.1995.488968
                 Poli, R., Kennedy, J. & Blackwell, T. (2007). "Particle swarm
                 optimization: An overview". Swarm Intelligence, 1(1), 33-57.
                 DOI: 10.1007/s11721-007-0002-0
                 Shi, Y. & Eberhart, R. (1998). "A modified particle swarm
                 optimizer" (introduce el peso de inercia w). DOI: 10.1109/ICEC.1998.699146

Idea del algoritmo:
  Un "enjambre" de partículas vuela por el espacio de búsqueda. Cada partícula i
  tiene posición x_i y velocidad v_i, y recuerda la mejor posición que visitó
  (pbest_i). El enjambre comparte la mejor posición de todos (gbest). En cada paso:

      v_i = w * v_i  +  c1 * r1 * (pbest_i - x_i)  +  c2 * r2 * (gbest - x_i)
      x_i = x_i + v_i

  donde w = inercia, c1 = componente cognitiva (memoria propia),
  c2 = componente social (atracción al mejor global), r1, r2 ~ U(0,1).

Ejecutar:  python codes/pso_function.py
Genera:    slides/figures/pso_enjambre_iter.png
           slides/figures/pso_convergencia.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "slides", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

rng = np.random.default_rng(42)


# --------------------------------------------------------------------------- #
# 1. Función objetivo (problema a resolver)
#    Rastrigin: muy "ondulada", con muchos mínimos locales y el mínimo global
#    en el origen, donde f = 0. Es un test clásico de optimización.
# --------------------------------------------------------------------------- #
def rastrigin(X):
    X = np.atleast_2d(X)
    A = 10.0
    return A * X.shape[1] + np.sum(X ** 2 - A * np.cos(2 * np.pi * X), axis=1)


BOUNDS = (-5.12, 5.12)   # dominio típico de Rastrigin
DIM = 2                  # 2D para poder dibujar el enjambre


# --------------------------------------------------------------------------- #
# 2. PSO
# --------------------------------------------------------------------------- #
def pso(func, n_part=30, n_iter=60, w_start=0.9, w_end=0.4, c1=1.5, c2=1.5,
        bounds=BOUNDS, dim=DIM, snap_iters=(0, 5, 20, 59), verbose=True):
    # Peso de inercia DECRECIENTE (Shi & Eberhart, 1998): empieza alto para
    # explorar mucho y baja para afinar al final. Evita la convergencia prematura.
    lo, hi = bounds
    v_max = 0.2 * (hi - lo)

    # Inicialización aleatoria de posiciones y velocidades.
    x = rng.uniform(lo, hi, size=(n_part, dim))
    v = rng.uniform(-v_max, v_max, size=(n_part, dim))

    pbest = x.copy()
    pbest_val = func(x)
    g_idx = np.argmin(pbest_val)
    gbest = pbest[g_idx].copy()
    gbest_val = pbest_val[g_idx]

    historia = [gbest_val]
    snapshots = {}   # guardamos posiciones del enjambre en ciertas iteraciones

    if verbose:
        print(f"{'iter':>4} {'gbest_x':>22} {'f(gbest)':>12}")
        print("-" * 42)

    for t in range(n_iter):
        # Inercia que decrece linealmente de w_start a w_end.
        w = w_start - (w_start - w_end) * t / (n_iter - 1)
        r1 = rng.random(size=(n_part, dim))
        r2 = rng.random(size=(n_part, dim))

        # Actualización de velocidad y posición.
        v = w * v + c1 * r1 * (pbest - x) + c2 * r2 * (gbest - x)
        v = np.clip(v, -v_max, v_max)
        x = np.clip(x + v, lo, hi)

        # Actualización de pbest y gbest.
        val = func(x)
        mejora = val < pbest_val
        pbest[mejora] = x[mejora]
        pbest_val[mejora] = val[mejora]
        g_idx = np.argmin(pbest_val)
        if pbest_val[g_idx] < gbest_val:
            gbest = pbest[g_idx].copy()
            gbest_val = pbest_val[g_idx]

        historia.append(gbest_val)
        if t in snap_iters:
            snapshots[t] = x.copy()

        if verbose and (t in snap_iters or t < 5):
            coord = "(" + ", ".join(f"{c:+.3f}" for c in gbest) + ")"
            print(f"{t:>4} {coord:>22} {gbest_val:>12.5f}")

    if verbose:
        print("\nMejor solución encontrada:")
        print("  x* =", np.round(gbest, 5), "  f(x*) =", round(float(gbest_val), 6))
        print("  (el óptimo real es x=(0,0) con f=0)")

    return gbest, gbest_val, historia, snapshots


# --------------------------------------------------------------------------- #
# 3. Gráficas
# --------------------------------------------------------------------------- #
def plot_snapshots(func, snapshots, archivo, bounds=BOUNDS):
    lo, hi = bounds
    gx = np.linspace(lo, hi, 200)
    XX, YY = np.meshgrid(gx, gx)
    ZZ = func(np.column_stack([XX.ravel(), YY.ravel()])).reshape(XX.shape)

    iters = sorted(snapshots)
    fig, axes = plt.subplots(1, len(iters), figsize=(4 * len(iters), 4))
    if len(iters) == 1:
        axes = [axes]
    for ax, t in zip(axes, iters):
        ax.contourf(XX, YY, ZZ, levels=30, cmap="viridis")
        pts = snapshots[t]
        ax.scatter(pts[:, 0], pts[:, 1], c="red", s=18, edgecolors="white")
        ax.scatter([0], [0], marker="*", c="white", s=160, edgecolors="black")
        ax.set_title(f"iteración {t}")
        ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    fig.suptitle("Enjambre de partículas convergiendo al mínimo (Rastrigin)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, archivo), dpi=130)
    plt.close(fig)


def plot_convergencia(historia, archivo):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(historia, color="#2c7fb8")
    ax.set_title("Convergencia de PSO")
    ax.set_xlabel("iteración"); ax.set_ylabel("mejor f(gbest)")
    ax.set_yscale("symlog")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, archivo), dpi=130)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 4. Programa principal
# --------------------------------------------------------------------------- #
def main():
    print("=" * 60)
    print(" PSO minimizando la función Rastrigin (2D)  -  paso a paso")
    print("=" * 60)

    gbest, gbest_val, historia, snapshots = pso(rastrigin)

    plot_snapshots(rastrigin, snapshots, "pso_enjambre_iter.png")
    plot_convergencia(historia, "pso_convergencia.png")

    print(f"\nFiguras guardadas en: {os.path.abspath(FIG_DIR)}")


if __name__ == "__main__":
    main()
