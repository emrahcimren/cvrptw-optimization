Capacitated Vehicle Routing Problem with Time Windows (CVRPTW) Optimization Models
====================================================

Repo for CVRPTW optimization models.

Prerequisites
-------------

Install requirements.txt for prerequisites.

```
conda create --name cvrptw_optimization --file requirements.txt
```

Install environment.yml for prerequisites.

```
conda env create -f environment.yml
```

To recreate environment.yml

```
conda env export > environment.yml
```

To create requirements.txt from environment.yml

```
pip freeze > requirements.txt
```

Installation
------------

```
pip install cimren-cvrptw-optimization
```

Inputs
------

Data
----
Package has a sample data set


How to use
----------


Models
------

**Descrochers et al.1988**

    Desrochers, M., Lenstra, J.K., Savelsbergh, M.W.P., Soumis, F. (1988).
    Vehicle routing with time windows: Optimization and approximation.
    In: Golden, B.L., Assad, A.A. (Eds.), Vehicle Routing: Methods and Studies. North-Holland, Amsterdam, pp. 65–84.

*Sets and Parameters*

Define a directed graph $G(N, A)$ where $|V|=n+2$
- Depot represents two vertices 0 and $n+1$

$$N:$$ Set of nodes

$A:$ Set of arcs

$K:$ Set of vehicles

$s_i:$ Service time at location $i \in N$

$t_{ij}:$ Travel time from $i$ to $j$, $(i,j)\in A$

$[a_i, b_i]:$ Time windows for $i\in N$

$a_0 = \min_{i\in N}\{a_i - t_{0i}\}$

$b_0 = \max_{i\in N}\{b_i - t_{0i}\}$

$a_{n+1} = \min_{i\in N} \{a_i + s_i+ t_{in+1}\}$

$b_{n+1} = \max_{i\in N} \{b_i + s_i+ t_{in+1}\}$


### Variables 

$x_{ijk}$ = 1 if $(i,j)$ is covered by vehicle $k$; 0 otherwise

$w_{ik}$ = Time when vehicle $k$ starts servicing at node $i\in N$