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
python codes/pso_function.py   # PSO para el diseño de un resorte de tensión/compresión
```

Cada script imprime el avance iteración por iteración y guarda sus figuras en
`slides/figures/`, listas para incrustarse en las diapositivas.

## ¿Qué hace cada uno?

### `vns_tsp.py` — Búsqueda de Vecindad Variable (VNS)
- **Problema:** TSP con 10 ciudades fijas (semilla reproducible).
- **Piezas clave:** `two_opt` (búsqueda local), `shake` (perturbación en la vecindad
  N_k) y `vns` (bucle de cambio de vecindad).
- **Salida:** `vns_tour_inicial.png`, `vns_tour_final.png`, `vns_convergencia.png`.
- **Paper de aplicación:** Hore, Chatterjee & Dewanji (2018), *Improving variable
  neighborhood search to solve the traveling salesman problem*, Applied Soft
  Computing, DOI: 10.1016/j.asoc.2018.03.048.
- **Paper del método:** Mladenović & Hansen (1997), DOI: 10.1016/S0305-0548(97)00031-2.

### `pso_function.py` — Optimización por Enjambre de Partículas (PSO)
- **Problema:** diseño de un resorte de tensión/compresión — minimizar su peso
  `f = (N+2)·D·d²` sujeto a 4 restricciones mecánicas (óptimo conocido ≈ 0.012665).
  Las restricciones se manejan con una **función de penalización**.
- **Piezas clave:** actualización de velocidad con inercia decreciente y componentes
  cognitiva/social, memoria `pbest` y mejor global `gbest`.
- **Salida:** `pso_convergencia.png`, `pso_variables.png`.
- **Paper de aplicación:** He & Wang (2007), *An effective co-evolutionary particle
  swarm optimization for constrained engineering design problems*, Engineering
  Applications of Artificial Intelligence, DOI: 10.1016/j.engappai.2006.03.003.
- **Papers del método:** Kennedy & Eberhart (1995) DOI: 10.1109/ICNN.1995.488968;
  Poli, Kennedy & Blackwell (2007) DOI: 10.1007/s11721-007-0002-0;
  Shi & Eberhart (1998) DOI: 10.1109/ICEC.1998.699146.
