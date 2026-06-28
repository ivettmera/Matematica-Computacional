// ============================================================
// PC5 — Búsqueda de Vecindad Variable (VNS) y PSO
// Matemática Computacional — UNI, Facultad de Ciencias
// Compilar:  typst compile slides/main.typ slides/main.pdf
// Las figuras las generan los scripts de codes/ (ver README).
// ============================================================

#import "@preview/clari-docs:0.1.0": *

// ── Presentation Setup ──────────────────────────────────────
// category: "simple" | "math" | "professional" | "allrounder"
// theme: "ocean" | "midnight" | "forest" | "teal" | "sunset"
//        "amber" | "rose" | "lavender" | "slate" | "charcoal"
//        or any rgb() color value
#show: clari-docs.with(
  category:          "allrounder",
  theme:             "ocean",
  font:              "Fira Sans",
  font-size:         20pt,
  show-page-numbers: true,
  show-progress:     true,
  back-color:        white,
)

// ── Cover Slide ─────────────────────────────────────────────

#title-slide(
  title:       "Búsqueda de Vecindad Variable y  PSO — Optimización de Enjambre",
  subtitle:    [Práctica Calificada 5],
  author:      "Integrantes:
  - Canto Gamboa, Amir Abants
  - Mera Amado, Ivett Marinella
  - Valverde Gonzales, Yoshua Natanael
  ",
  date:        datetime.today(),
  institution: "Universidad Nacional de Ingeniería
  Facultad de Ciencias",
)

// ── Table of Contents ───────────────────────────────────────
#overview-slide()

// ============================================================
// Sección 1 — Metaheurísticas
// ============================================================
#section-slide[¿Qué es una metaheurística?]

#slide(title: "La idea en una frase", outlined: true)[
  Muchos problemas reales (rutas, horarios, diseño) tienen *tantas soluciones
  posibles* que es imposible probarlas todas con una computadora.

  #definition(
    "Metaheurística",
    [Una receta general e inteligente para *buscar buenas soluciones* en un tiempo
    razonable, aunque no garantice encontrar la óptima exacta.],
  )

  Toda metaheurística equilibra dos fuerzas opuestas:

  #cols[
    #info-v(title: "Exploración")[
      Saltar a zonas nuevas del espacio de búsqueda para *no quedarse atrapado*
      en una mala solución.
    ]
  ][
    #info-v(title: "Explotación")[
      Afinar y mejorar la *solución que ya tenemos* mirando a su alrededor.
    ]
  ]
]

#slide(title: "Las dos que nos tocaron")[
  #comparison(
    left-title:  "VNS — Vecindad Variable",
    right-title: "PSO — Enjambre de Partículas",
    [
      - Trabaja con *una* solución y la mejora.
      - Cambia *el tamaño del salto* cuando se atasca.
      - Para problemas *combinatorios*.
      - La probamos en el *TSP* (Agente Viajero).
    ],
    [
      - Trabaja con *muchas* soluciones a la vez.
      - Se inspira en *bandadas de aves*.
      - Para *funciones continuas*.
      - La probamos en la *función Rastrigin*.
    ],
  )
]

// ============================================================
// Sección 2 — VNS
// ============================================================
#section-slide[VNS — Búsqueda de Vecindad Variable]

#slide(title: "El paper que resumimos", outlined: true)[
  #info-h(title: "Referencia [1]")[
    Mladenović, N. & Hansen, P. (1997). _Variable neighborhood search_.
    Computers & Operations Research, 24(11), 1097–1100. \
    DOI: 10.1016/S0305-0548(97)00031-2
  ]

  *De qué trata, en simple:* la *búsqueda local* clásica mejora una solución mirando
  solo vecinos cercanos, y por eso se queda atrapada en *óptimos locales*. La idea de
  los autores es sencilla y poderosa: cuando te atascas, *cambia la definición de
  "vecino"* a una más amplia y vuelve a buscar. Así lograron mejorar las soluciones
  del TSP (mejoraron el algoritmo GENIUS).

  #callout(type: "note")[
    Apoyo teórico [2]: Hansen & Mladenović (2001), _EJOR_ 130(3), 449–467.
    DOI: 10.1016/S0377-2217(00)00100-4
  ]
]

#slide(title: "El problema: TSP (Agente Viajero)")[
  *Problematización.* Un viajero debe visitar $n$ ciudades *exactamente una vez* y
  volver al inicio, recorriendo *la menor distancia total* posible.

  #cols(columns: (1.3fr, 1fr))[
    - El número de rutas posibles es $(n-1)! / 2$.
    - Con solo *20 ciudades* hay más de $10^16$ rutas: ni la computadora más rápida
      las prueba todas.
    - El TSP es *NP-difícil*: no se conoce ningún método exacto y rápido.
    - Por eso usamos metaheurísticas: hallan rutas *muy buenas* sin revisarlas todas.
  ][
    #callout(type: "tip")[
      Es un problema central en *computación*: logística, fabricación de chips,
      secuenciación de ADN, ruteo de drones.
    ]
  ]
]

#slide(title: "Marco teórico: las piezas de VNS")[
  #step-list(
    [*Familia de vecindades* $N_1, N_2, dots, N_(k_max)$, de menor a mayor. En
     nuestro código $N_k$ = "aplicar $k$ intercambios aleatorios de ciudades".],
    [*Shaking (sacudida):* elegir un punto *al azar* dentro de $N_k$ para salir del
     óptimo local. → es la *exploración*.],
    [*Búsqueda local (2-opt):* desde ese punto, bajar al óptimo local más cercano
     desarmando y reconectando aristas del tour. → es la *explotación*.],
  )
]

#slide(title: "Marco teórico: el pseudocódigo")[
  #code-block(title: "VNS básico")[
```text
VNS(solución inicial x, k_max):
    x ← BúsquedaLocal(x)              // 2-opt
    repetir hasta criterio de parada:
        k ← 1
        mientras k ≤ k_max:
            x'  ← Shaking(x, k)       // salto aleatorio en N_k  (explora)
            x'' ← BúsquedaLocal(x')   // 2-opt                   (explota)
            si long(x'') < long(x):   // ¿mejoró?
                x ← x'' ;  k ← 1      //   sí: nos movemos y k vuelve a 1
            sino:
                k ← k + 1             //   no: agrandamos la vecindad
    devolver x
```
  ]
  #callout(type: "important")[
    Mientras mejora, intensifica cerca ($k=1$); cuando se atasca, diversifica
    agrandando $k$.
  ]
]

#img-left("figures/vns_tour_inicial.png")[
  *Punto de partida*

  Arrancamos con una ruta *aleatoria*: larga y con cruces.

  VNS la irá *desenredando* poco a poco hasta dejarla corta y limpia.
]

#slide(title: "Cómo VNS resuelve el TSP — log paso a paso")[
  Cada línea es una iteración: vemos la vecindad $k$, la longitud del candidato y si
  lo aceptamos. Al aceptar, $k$ vuelve a 1; al fallar, $k$ crece.

  #code-block(title: "salida de python codes/vns_tsp.py")[
```text
Tour inicial (tras 2-opt): longitud 3.8153
iter  k     cand.  ¿mejora?
------------------------------
   1  1    4.0749   no, k+1
   2  2    3.8886   no, k+1
   3  3    3.7778  SÍ -> k=1
   5  2    3.6816  SÍ -> k=1
   7  2    3.6216  SÍ -> k=1
  10  3    3.6007  SÍ -> k=1
  17  2    3.5994  SÍ -> k=1
  20  3    3.5759  SÍ -> k=1
  25  5    3.5073  SÍ -> k=1   <- mejor encontrado
   ...
Longitud final: 3.5073
```
  ]
]

#slide(title: "Cómo VNS resuelve el TSP — resultado")[
  #cols[
    #image("figures/vns_tour_final.png", width: 100%)
  ][
    #image("figures/vns_convergencia.png", width: 100%)
  ]
  #align(center)[#text(size: 16pt)[
    El tour final no tiene cruces y es mucho más corto: de $6.01$ (ruta aleatoria) a
    $3.51$, un $42%$ menos. La longitud baja *a saltos* en cada mejora.
  ]]
]

// ============================================================
// Sección 3 — PSO
// ============================================================
#section-slide[PSO — Optimización por Enjambre de Partículas]

#slide(title: "El paper que resumimos", outlined: true)[
  #info-h(title: "Referencia [4]")[
    Poli, R., Kennedy, J. & Blackwell, T. (2007). _Particle swarm optimization: An
    overview_. Swarm Intelligence, 1(1), 33–57. \
    DOI: 10.1007/s11721-007-0002-0
  ]

  *De qué trata, en simple:* es un artículo de revista que repasa el PSO, propuesto
  por Kennedy y Eberhart en 1995. La inspiración es una *bandada de aves* buscando
  comida: ninguna sabe dónde está, pero cada una se guía por *su mejor hallazgo* y por
  *el mejor del grupo*. Juntas terminan convergiendo al objetivo.

  #callout(type: "note")[
    Original [3]: Kennedy & Eberhart (1995), DOI: 10.1109/ICNN.1995.488968.
    Peso de inercia [5]: Shi & Eberhart (1998), DOI: 10.1109/ICEC.1998.699146.
  ]
]

#slide(title: "El problema: minimizar una función")[
  *Problematización.* En computación, muchísimas tareas se reducen a *minimizar una
  función* $f(x)$: ajustar pesos de una red neuronal, calibrar un modelo, diseñar una
  pieza. Buscamos el $x$ que da el valor más bajo.

  #math-eq(numbered: true)[
    $ f(x) = 10 n + sum_(i=1)^n (x_i^2 - 10 cos(2 pi x_i)) $
  ]

  #cols[
    Usamos la *función Rastrigin*: está llena de *mínimos locales* (es "ondulada") y
    su *mínimo global* está en el origen $x = (0,0)$, donde $f = 0$.
  ][
    #callout(type: "tip")[
      Es el test ideal: si la metaheurística no se deja engañar por Rastrigin, sirve
      para problemas reales difíciles.
    ]
  ]
]

#slide(title: "Marco teórico: las piezas de PSO")[
  Cada *partícula* $i$ es una solución con *posición* $x_i$ y *velocidad* $v_i$.
  El enjambre recuerda dos cosas:

  #cols[
    #info-v(title: "pbest")[
      $p_i$: la mejor posición que la partícula $i$ visitó. → *memoria propia*.
    ]
  ][
    #info-v(title: "gbest")[
      $g$: la mejor posición de *todo* el enjambre. → *conocimiento social*.
    ]
  ]

  En cada paso, la velocidad mezcla tres impulsos:

  #pin-eq(
    [$ v_i <- w v_i + c_1 r_1 (p_i - x_i) + c_2 r_2 (g - x_i) $],
    [$w v_i$ — inercia: la partícula sigue su rumbo (explora)],
    [$c_1 r_1 (p_i - x_i)$ — cognitivo: la atrae hacia su mejor personal],
    [$c_2 r_2 (g - x_i)$ — social: la atrae hacia el mejor global],
  )
]

#slide(title: "Marco teórico: el pseudocódigo")[
  #code-block(title: "PSO")[
```text
PSO(función f, N partículas, T iteraciones):
    inicializar posiciones x_i y velocidades v_i al azar
    p_i ← x_i ;  g ← mejor de todos los p_i
    repetir T veces:
        para cada partícula i:
            v_i ← w·v_i + c1·r1·(p_i − x_i) + c2·r2·(g − x_i)
            x_i ← x_i + v_i
            si f(x_i) < f(p_i):  p_i ← x_i     // mejor personal
            si f(x_i) < f(g):    g  ← x_i      // mejor global
    devolver g
```
  ]
  #callout(type: "important")[
    La inercia explora; la atracción a $p_i$ y $g$ explota. El enjambre se concentra
    solo donde hay buenas soluciones.
  ]
]

#slide(title: "Cómo PSO resuelve el problema — log paso a paso")[
  El mejor global (`gbest`) se acerca al origen y su valor cae hacia 0:

  #code-block(title: "salida de python codes/pso_function.py")[
```text
iter              gbest_x      f(gbest)
------------------------------------------
   0   (+2.051, -1.921)       9.59640
   1   (+2.136, -0.975)       9.08227
   2   (+1.087, -1.058)       4.43517
   5   (+0.921, -1.060)       3.90015
  20   (+1.030, +0.014)       1.28171
  59   (-0.000, -0.000)       0.00000   <- óptimo global
```
  ]
]

#slide(title: "Cómo PSO resuelve el problema — el enjambre en acción")[
  #image("figures/pso_enjambre_iter.png", width: 100%)
  #align(center)[#text(size: 16pt)[
    Las partículas (rojo) parten dispersas y se concentran en el mínimo global
    (estrella blanca) conforme avanzan las iteraciones.
  ]]
]

#img-right("figures/pso_convergencia.png")[
  *Convergencia*

  El valor del mejor global desciende rápidamente hacia 0, el mínimo de Rastrigin.

  PSO atravesó los muchos mínimos locales sin quedarse atrapado, gracias a que el
  enjambre comparte información.
]

// ============================================================
// Sección 4 — Cierre
// ============================================================
#section-slide[Conclusiones]

#slide(title: "Conclusiones", outlined: true)[
  #step-list(
    [Las *metaheurísticas* atacan problemas sin solución exacta rápida, equilibrando
     *exploración* y *explotación*.],
    [*VNS* (una solución, vecindades que crecen) desenredó el *TSP*: de una ruta
     aleatoria con cruces a una corta y limpia, cambiando de vecindad al atascarse.],
    [*PSO* (un enjambre que comparte información) minimizó la *Rastrigin* pese a sus
     muchos mínimos locales, llegando al óptimo global.],
    [Nacen de ideas muy distintas —*sistemática* vs. *colectiva*— pero ambas son
     simples de programar y sorprendentemente efectivas.],
  )
]

#slide(title: "Referencias")[
  #set text(size: 15pt)
  + Mladenović, N. & Hansen, P. (1997). Variable neighborhood search.
    _Computers & Operations Research_, 24(11), 1097–1100.
    DOI: 10.1016/S0305-0548(97)00031-2

  + Hansen, P. & Mladenović, N. (2001). Variable neighborhood search: Principles and
    applications. _European Journal of Operational Research_, 130(3), 449–467.
    DOI: 10.1016/S0377-2217(00)00100-4

  + Kennedy, J. & Eberhart, R. (1995). Particle swarm optimization. _Proc. IEEE Int.
    Conf. on Neural Networks_, 1942–1948. DOI: 10.1109/ICNN.1995.488968

  + Poli, R., Kennedy, J. & Blackwell, T. (2007). Particle swarm optimization: An
    overview. _Swarm Intelligence_, 1(1), 33–57. DOI: 10.1007/s11721-007-0002-0

  + Shi, Y. & Eberhart, R. (1998). A modified particle swarm optimizer.
    _Proc. IEEE ICEC_, 69–73. DOI: 10.1109/ICEC.1998.699146
]

// ── End Slide ───────────────────────────────────────────────
#end-slide(title: "¡Gracias!")[
  Código y figuras: `codes/vns_tsp.py` · `codes/pso_function.py`
]
