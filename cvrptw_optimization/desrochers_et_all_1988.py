'''
CVRPTW formulation by Desrochers et al 1988
    Desrochers, M., Lenstra, J.K., Savelsbergh, M.W.P., Soumis, F. (1988).
    Vehicle routing with time windows: Optimization and approximation.
    In: Golden, B.L., Assad, A.A. (Eds.), Vehicle Routing: Methods and Studies. North-Holland, Amsterdam, pp. 65–84.
'''

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
from cvrptw_optimization.src import desrochers_et_all_1988_helpers as he
from cvrptw_optimization.src import desrochers_et_all_1988_inputs as di


def run_desrochers_et_all_1988(depot,
                               locations,
                               transportation_matrix,
                               vehicles,
                               maximum_travel_hours,
                               solver_time_limit_mins,
                               solver='or tools'):
    '''
    Run Desrochers model
    :param depot:
    :param locations:
    :param transportation_matrix:
    :param vehicles:
    :param maximum_travel_hours:
    :param solver_time_limit_mins:
    :param solver:
    :return:
    '''

    locations_name_list = list(locations['LOCATION_NAME'].unique())
    depot_name_list = list(depot['LOCATION_NAME'].unique())

    # filter transportation matrix
    transportation_matrix = he.filter_transportation_matrix(transportation_matrix, locations_name_list, depot_name_list)

    # validate transportation matrix
    he.validate_transportation_matrix(transportation_matrix, locations_name_list, depot_name_list)

    # convert transportation matrix
    transportation_matrix = he.prepare_transportation_matrix(transportation_matrix, depot_name_list)

    # prepare model inputs
    inputs = di.ModelInputs(transportation_matrix, locations, depot, vehicles)

    # create model formulation #
    if solver == 'or tools':
        print('solving with or tools')
        from cvrptw_optimization.src import desrochers_et_all_1988_ortools_formulation as orf

        model = orf.Formulation(inputs.K, inputs.V, inputs.N, inputs.t, inputs.q, inputs.s,
                                inputs.locations, inputs.depot, inputs.outgoing_arcs, inputs.incoming_arcs,
                                inputs.depot_leave, inputs.depot_enter, inputs.a, inputs.b, inputs.M, inputs.Q,
                                solver_time_limit_mins,
                                maximum_travel_hours)

        model.initiate_solver()
        model.create_model_formulation()
        model.create_model_objective()
        model.run_model()
        model.compile_results()

        return model.final_model_solution

    elif solver == 'gurobi':
        print('solving with gurobi')

        return None

    else:
        return print('no solver is defined')
