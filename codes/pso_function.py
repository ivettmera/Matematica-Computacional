"""
Optimización por Enjambre de Partículas (PSO) para el DISEÑO DE UN RESORTE
de tensión/compresión (problema clásico de optimización en ingeniería).

Metaheurística:  Particle Swarm Optimization (PSO)
Problema:        Diseño de resorte de tensión/compresión -> minimizar su PESO
                 sujeto a restricciones mecánicas.
Paper de aplicación:
                 He, Q. & Wang, L. (2007). "An effective co-evolutionary particle
                 swarm optimization for constrained engineering design problems".
                 Engineering Applications of Artificial Intelligence, 20(1), 89-99.
                 DOI: 10.1016/j.engappai.2006.03.003
Papers base del método:
                 Kennedy & Eberhart (1995), DOI: 10.1109/ICNN.1995.488968
                 Poli, Kennedy & Blackwell (2007), DOI: 10.1007/s11721-007-0002-0
                 Shi & Eberhart (1998), DOI: 10.1109/ICEC.1998.699146

El problema (3 variables de diseño):
    x1 = d : diámetro del alambre            (0.05 .. 2.00)
    x2 = D : diámetro medio de la espira      (0.25 .. 1.30)
    x3 = N : número de espiras activas        (2.00 .. 15.00)

    Minimizar  f(x) = (x3 + 2) * x2 * x1^2          (peso del resorte)

    sujeto a 4 restricciones g_i(x) <= 0 (deflexión, esfuerzo, frecuencia,
    diámetro exterior). El mejor valor conocido es f ≈ 0.012665.

Manejo de restricciones: PSO no las trata directamente, así que usamos una
FUNCIÓN DE PENALIZACIÓN: a las soluciones que violan restricciones les sumamos
un castigo grande, de modo que el enjambre las evite y busque soluciones válidas.

Ejecutar:  python codes/pso_function.py
Genera:    slides/figures/pso_convergencia.png
           slides/figures/pso_variables.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "slides", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

rng = np.random.default_rng(42)

# Límites de cada variable de diseño  [d, D, N]
LO = np.array([0.05, 0.25, 2.0])
HI = np.array([2.00, 1.30, 15.0])
DIM = 3
PENALTY = 1.0e6          # castigo por violar restricciones
OPTIMO_CONOCIDO = 0.012665


# --------------------------------------------------------------------------- #
# 1. El problema: peso del resorte y sus restricciones
# --------------------------------------------------------------------------- #
def peso(x):
    """Función objetivo: peso del resorte (queremos minimizarlo)."""
    d, D, N = x[..., 0], x[..., 1], x[..., 2]
    return (N + 2) * D * d ** 2


def restricciones(x):
    """Devuelve las 4 restricciones g_i(x); son válidas cuando g_i <= 0."""
    d, D, N = x[..., 0], x[..., 1], x[..., 2]
    g1 = 1 - (D ** 3 * N) / (71785 * d ** 4)
    g2 = (4 * D ** 2 - d * D) / (12566 * (D * d ** 3 - d ** 4)) \
        + 1 / (5108 * d ** 2) - 1
    g3 = 1 - 140.45 * d / (D ** 2 * N)
    g4 = (d + D) / 1.5 - 1
    return np.stack([g1, g2, g3, g4], axis=-1)


def es_factible(x):
    """True si la solución cumple TODAS las restricciones."""
    return np.all(restricciones(x) <= 0, axis=-1)


def fitness(x):
    """Peso + penalización por cada restricción violada (la guía del PSO)."""
    g = restricciones(x)
    violacion = np.sum(np.maximum(0.0, g) ** 2, axis=-1)
    return peso(x) + PENALTY * violacion


# --------------------------------------------------------------------------- #
# 2. PSO con peso de inercia decreciente (Shi & Eberhart)
# --------------------------------------------------------------------------- #
def pso(n_part=40, n_iter=100, w_start=0.9, w_end=0.4, c1=1.5, c2=1.5,
        log_iters=(0, 1, 2, 5, 10, 25, 50, 99), verbose=True):
    v_max = 0.2 * (HI - LO)

    x = rng.uniform(LO, HI, size=(n_part, DIM))
    v = rng.uniform(-v_max, v_max, size=(n_part, DIM))

    pbest = x.copy()
    pbest_fit = fitness(x)
    g_idx = np.argmin(pbest_fit)
    gbest = pbest[g_idx].copy()
    gbest_fit = pbest_fit[g_idx]

    # Historia del mejor peso FACTIBLE encontrado (para graficar algo con sentido).
    hist_peso = []
    hist_vars = []

    if verbose:
        print(f"{'iter':>4} {'d':>9} {'D':>9} {'N':>9} {'peso':>11} {'¿válido?':>9}")
        print("-" * 54)

    for t in range(n_iter):
        w = w_start - (w_start - w_end) * t / (n_iter - 1)
        r1 = rng.random(size=(n_part, DIM))
        r2 = rng.random(size=(n_part, DIM))

        v = w * v + c1 * r1 * (pbest - x) + c2 * r2 * (gbest - x)
        v = np.clip(v, -v_max, v_max)
        x = np.clip(x + v, LO, HI)

        fit = fitness(x)
        mejora = fit < pbest_fit
        pbest[mejora] = x[mejora]
        pbest_fit[mejora] = fit[mejora]
        g_idx = np.argmin(pbest_fit)
        if pbest_fit[g_idx] < gbest_fit:
            gbest = pbest[g_idx].copy()
            gbest_fit = pbest_fit[g_idx]

        factible = es_factible(gbest)
        hist_peso.append(peso(gbest) if factible else np.nan)
        hist_vars.append(gbest.copy())

        if verbose and t in log_iters:
            d, D, N = gbest
            ok = "sí" if factible else "no"
            print(f"{t:>4} {d:>9.4f} {D:>9.4f} {N:>9.4f} "
                  f"{peso(gbest):>11.6f} {ok:>9}")

    if verbose:
        print("\nMejor diseño encontrado:")
        print(f"  d = {gbest[0]:.5f},  D = {gbest[1]:.5f},  N = {gbest[2]:.4f}")
        print(f"  peso = {peso(gbest):.6f}   (¿válido? "
              f"{'sí' if es_factible(gbest) else 'no'})")
        print(f"  óptimo conocido del paper ≈ {OPTIMO_CONOCIDO}")

    return gbest, np.array(hist_peso), np.array(hist_vars)


# --------------------------------------------------------------------------- #
# 3. Gráficas
# --------------------------------------------------------------------------- #
def plot_convergencia(hist_peso, archivo):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(hist_peso, color="#2c7fb8", lw=2)
    ax.axhline(OPTIMO_CONOCIDO, color="green", ls="--",
               label=f"óptimo conocido ≈ {OPTIMO_CONOCIDO}")
    ax.set_title("Convergencia de PSO — peso del resorte")
    ax.set_xlabel("iteración"); ax.set_ylabel("mejor peso factible")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, archivo), dpi=130)
    plt.close(fig)


def plot_variables(hist_vars, archivo):
    nombres = ["d  (diám. alambre)", "D  (diám. espira)", "N  (nº espiras)"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    for i, ax in enumerate(axes):
        ax.plot(hist_vars[:, i], color="#d95f0e", lw=2)
        ax.set_title(nombres[i])
        ax.set_xlabel("iteración"); ax.grid(alpha=0.3)
    fig.suptitle("Las 3 variables de diseño se estabilizan en el óptimo")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, archivo), dpi=130)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 4. Programa principal
# --------------------------------------------------------------------------- #
def main():
    print("=" * 60)
    print(" PSO — Diseño de un resorte de tensión/compresión (paso a paso)")
    print("=" * 60)

    gbest, hist_peso, hist_vars = pso()

    plot_convergencia(hist_peso, "pso_convergencia.png")
    plot_variables(hist_vars, "pso_variables.png")

    print(f"\nFiguras guardadas en: {os.path.abspath(FIG_DIR)}")


if __name__ == "__main__":
    main()
