from cvrptw_optimization.src import single_depot_general_model_pulp_inputs as inputs


def run_single_depot_general_model(depots,
                                   customers,
                                   transportation_matrix,
                                   vehicles):

    print('ok')
    model_inputs = inputs.ModelInputs(transportation_matrix, customers, depots, vehicles)



