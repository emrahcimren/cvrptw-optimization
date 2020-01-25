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

Inputs
------


Data
----
Package has a sample data set

```
from cvrptw_optimization.src import data
data.depot
data.locations
data.transportation_matrix
data.vehicles
```

How to use
----------

```
from cvrptw_optimization import desrochers_et_all_1988 as d
d.run_desrochers_et_all_1988(depot, locations, transportation_matrix,
                             vehicles, maximum_travel_hours,
                             solver_time_limit_mins,
                             solver='ortools')
```
