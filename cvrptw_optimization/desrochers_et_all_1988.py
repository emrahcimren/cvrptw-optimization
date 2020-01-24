'''
CVRPTW formulation by Desrochers et al 1988
    Desrochers, M., Lenstra, J.K., Savelsbergh, M.W.P., Soumis, F. (1988).
    Vehicle routing with time windows: Optimization and approximation.
    In: Golden, B.L., Assad, A.A. (Eds.), Vehicle Routing: Methods and Studies. North-Holland, Amsterdam, pp. 65–84.
'''

import pandas as pd
from cvrptw_optimization.src import data
from cvrptw_optimization.src import desrochers_et_all_1988_inputs as di


def run_desrochers_et_all_1988(depot,
                               locations,
                               transportation_matrix,
                               solver='ortools'):

    locations_name_list = list(locations['LOCATION_NAME'].unique())
    depot_name_list = list(depot['LOCATION_NAME'].unique())

    # filter transportation matrix
    transportation_matrix = di.filter_transportation_matrix(transportation_matrix, locations_name_list, depot_name_list)

    # validate transportation matrix
    di.validate_transportation_matrix(transportation_matrix, locations_name_list, depot_name_list)

    # convert transportation matrix
    transportation_matrix = di.prepare_transportation_matrix(transportation_matrix, depot_name_list)

    # prepare model inputs


    return None
