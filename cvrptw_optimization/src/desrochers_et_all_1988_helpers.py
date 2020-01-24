'''
Input data sets
CVRPTW formulation by Desrochers et al 1988
    Desrochers, M., Lenstra, J.K., Savelsbergh, M.W.P., Soumis, F. (1988).
    Vehicle routing with time windows: Optimization and approximation.
    In: Golden, B.L., Assad, A.A. (Eds.), Vehicle Routing: Methods and Studies. North-Holland, Amsterdam, pp. 65–84.
'''


def filter_transportation_matrix(transportation_matrix, locations_name_list, depot_name_list):
    '''
    Aligns transportation matrix with locations and depot
    :param transportation_matrix:
    :param locations_name_list:
    :param depot_name_list:
    :return:
    '''
    transportation_matrix = transportation_matrix[
        transportation_matrix['FROM_LOCATION_NAME'].isin(locations_name_list + depot_name_list)]
    transportation_matrix = transportation_matrix[
        transportation_matrix['TO_LOCATION_NAME'].isin(locations_name_list + depot_name_list)]

    return transportation_matrix


def validate_transportation_matrix(transportation_matrix, locations_name_list, depot_name_list):
    '''
    Validates transportation matrix
    :param transportation_matrix:
    :param locations_name_list:
    :param depot_name_list:
    :return:
    '''
    if len(transportation_matrix) == len(locations_name_list+depot_name_list)*len(locations_name_list+depot_name_list):
        return print('Transportation matrix is valid')
    else:
        raise Exception('Transportation matrix is not valid. Please investigate')


def prepare_transportation_matrix(transportation_matrix, depot_name_list):
    '''
    Extend transportation matrix with depots
    :param transportation_matrix:
    :param depot_name_list:
    :return:
    '''
    filter_depots = transportation_matrix['FROM_LOCATION_NAME'] == transportation_matrix['TO_LOCATION_NAME']
    transportation_matrix = transportation_matrix[~filter_depots]

    filter_depots = transportation_matrix['FROM_LOCATION_NAME'].isin(depot_name_list)
    transportation_matrix_store_to_store = transportation_matrix[~filter_depots]
    filter_depots = transportation_matrix_store_to_store['TO_LOCATION_NAME'].isin(depot_name_list)
    transportation_matrix_store_to_store = transportation_matrix_store_to_store[~filter_depots]

    filter_depots = transportation_matrix['FROM_LOCATION_NAME'].isin(depot_name_list)
    transportation_matrix_depot_to_store = transportation_matrix[filter_depots]
    transportation_matrix_depot_to_store['FROM_LOCATION_NAME'] = transportation_matrix_depot_to_store[
                                                                     'FROM_LOCATION_NAME'] + '_START'

    filter_depots = transportation_matrix['TO_LOCATION_NAME'].isin(depot_name_list)
    transportation_matrix_store_to_depot = transportation_matrix[filter_depots]
    transportation_matrix_store_to_depot['TO_LOCATION_NAME'] = transportation_matrix_store_to_depot[
                                                                   'TO_LOCATION_NAME'] + '_END'

    transportation_matrix = transportation_matrix_depot_to_store.append(transportation_matrix_store_to_store)
    transportation_matrix = transportation_matrix.append(transportation_matrix_store_to_depot)

    return transportation_matrix
