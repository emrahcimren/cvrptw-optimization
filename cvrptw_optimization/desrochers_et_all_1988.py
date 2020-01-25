'''
CVRPTW formulation by Desrochers et al 1988
    Desrochers, M., Lenstra, J.K., Savelsbergh, M.W.P., Soumis, F. (1988).
    Vehicle routing with time windows: Optimization and approximation.
    In: Golden, B.L., Assad, A.A. (Eds.), Vehicle Routing: Methods and Studies. North-Holland, Amsterdam, pp. 65–84.
'''

import pandas as pd
from cvrptw_optimization.src import data
from cvrptw_optimization.src import desrochers_et_all_1988_helpers as he
from cvrptw_optimization.src import desrochers_et_all_1988_inputs as di

def run_desrochers_et_all_1988(depot,
                               locations,
                               transportation_matrix,
                               maximum_trucks,
                               solver='ortools'):
    '''
    Run Desrochers model
    :param depot:
    :param locations:
    :param transportation_matrix:
    :param maximum_trucks:
    :param solver:
    :return:
    '''
    transportation_matrix = data.transportation_matrix
    locations = data.locations
    depot = data.depot
    maximum_trucks = 1

    locations_name_list = list(locations['LOCATION_NAME'].unique())
    depot_name_list = list(depot['LOCATION_NAME'].unique())

    # filter transportation matrix
    transportation_matrix = he.filter_transportation_matrix(transportation_matrix, locations_name_list, depot_name_list)

    # validate transportation matrix
    he.validate_transportation_matrix(transportation_matrix, locations_name_list, depot_name_list)

    # convert transportation matrix
    transportation_matrix = he.prepare_transportation_matrix(transportation_matrix, depot_name_list)

    # prepare model inputs
    model_inputs = di.ModelInputs(transportation_matrix, locations, depot, maximum_trucks)

    # create model formulation #

    # run model #

    # summarize results #

    return None
