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

Models
------

**Descrochers et al.1988**

    Desrochers, M., Lenstra, J.K., Savelsbergh, M.W.P., Soumis, F. (1988).
    Vehicle routing with time windows: Optimization and approximation.
    In: Golden, B.L., Assad, A.A. (Eds.), Vehicle Routing: Methods and Studies. North-Holland, Amsterdam, pp. 65–84.

Inputs
------

#### Depot

Data frame for inputs.

| LOCATION_NAME   |   LATITUDE |   LONGITUDE |
|:----------------|-----------:|------------:|
| Depot           |    36.1627 |    -86.7816 |

#### Locations

Data frame of locations for routing.

| LOCATION_NAME   |   LATITUDE |   LONGITUDE |   TW_START_MINUTES |   TW_END_MINUTES |   STOP_TIME_WH_HELPER |   STOP_TIME_W_HELPER |   DEMAND |
|:----------------|-----------:|------------:|-------------------:|-----------------:|----------------------:|---------------------:|---------:|
| Loc 1           |    35.9021 |    -84.1508 |                960 |             1950 |                    27 |                   21 |        1 |
| Loc 2           |    35.7498 |    -83.9922 |                960 |             1950 |                    27 |                   21 |        1 |
| Loc 3           |    35.9077 |    -83.8392 |                960 |             1950 |                    27 |                   21 |        1 |
| Loc 4           |    35.9077 |    -83.8392 |                960 |             1950 |                    27 |                   21 |        1 |
| Loc 5           |    35.8625 |    -84.0666 |                960 |             1950 |                    27 |                   21 |        1 |

#### Transportation Matrix

Data frame of drive minutes.

| FROM_LOCATION_NAME   | TO_LOCATION_NAME   |   FROM_LATITUDE |   FROM_LONGITUDE |   TO_LATITUDE |   TO_LONGITUDE |   DRIVE_MINUTES |
|:---------------------|:-------------------|----------------:|-----------------:|--------------:|---------------:|----------------:|
| Depot                | Depot              |         36.1627 |         -86.7816 |       36.1627 |       -86.7816 |            0    |
| Depot                | Loc 1              |         36.1627 |         -86.7816 |       35.9021 |       -84.1508 |          163.85 |
| Depot                | Loc 2              |         36.1627 |         -86.7816 |       35.7498 |       -83.9922 |          206.06 |
| Depot                | Loc 3              |         36.1627 |         -86.7816 |       35.9077 |       -83.8392 |          210.03 |
| Depot                | Loc 4              |         36.1627 |         -86.7816 |       35.9077 |       -83.8392 |          210.03 |

#### Vehicles

Data frame for vehicles.

TEAM='assign' if route uses a team truck.
TEAM='not assign' if route does not use a team truck.
TEAM='select' if model decides using a team truck.

| VEHICLE_NAME   |   CAPACITY |   HELPER_COST_PER_HELPER_PER_ROUTE |   MAXIMUM_SOLO_TRAVEL_HOURS |   MAXIMUM_TEAM_TRAVEL_HOURS | TEAM   |   TEAM_COST_PER_TEAM_PER_ROUTE |   TRANS_COST_PER_MINUTE | TYPE            |
|:---------------|-----------:|-----------------------------------:|----------------------------:|----------------------------:|:-------|-------------------------------:|------------------------:|:----------------|
| Vehicle 1      |         20 |                               1200 |                          12 |                          20 | assign   |                           2000 |                       5 | 48 FOOTER TRUCK |

Sample Data
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
from cvrptw_optimization.src import data
from cvrptw_optimization import desrochers_et_all_1988 as d
d.run_desrochers_et_all_1988(data.depot,
                             data.locations,
                             data.transportation_matrix,
                             data.vehicles,
                             solver_time_limit_mins=1,
                             solver='or tools')
```
