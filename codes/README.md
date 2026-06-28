# VNS y PSO
## Requisitos

```bash
pip install -r requirements.txt
```

(numpy y matplotlib)

## Ejecutar

Desde la **raíz del proyecto** (la carpeta `PC5/`):

```bash
python codes/vns_tsp.py        # VNS sobre el Problema del Agente Viajero (TSP)
python codes/pso_function.py   # PSO minimizando la función Rastrigin
```

Cada script imprime el avance iteración por iteración y guarda sus figuras en
`slides/figures/`, listas para incrustarse en las diapositivas.

## ¿Qué hace cada uno?

### `vns_tsp.py` — Búsqueda de Vecindad Variable (VNS)
- **Problema:** TSP con 10 ciudades fijas (semilla reproducible).
- **Piezas clave:** `two_opt` (búsqueda local), `shake` (perturbación en la vecindad
  N_k) y `vns` (bucle de cambio de vecindad).
- **Salida:** `vns_tour_inicial.png`, `vns_tour_final.png`, `vns_convergencia.png`.
- **Paper:** Mladenović & Hansen (1997), DOI: 10.1016/S0305-0548(97)00031-2.

### `pso_function.py` — Optimización por Enjambre de Partículas (PSO)
- **Problema:** minimizar Rastrigin en 2D (mínimo global en el origen, f = 0).
- **Piezas clave:** actualización de velocidad con inercia `w` y componentes
  cognitiva/social, memoria `pbest` y mejor global `gbest`.
- **Salida:** `pso_enjambre_iter.png`, `pso_convergencia.png`.
- **Papers:** Kennedy & Eberhart (1995) DOI: 10.1109/ICNN.1995.488968;
  Poli, Kennedy & Blackwell (2007) DOI: 10.1007/s11721-007-0002-0;
  Shi & Eberhart (1998) DOI: 10.1109/ICEC.1998.699146.
