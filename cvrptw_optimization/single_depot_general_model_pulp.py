from cvrptw_optimization.src import single_depot_general_model_pulp_inputs as inputs
from cvrptw_optimization.src import single_depot_general_model_pulp_formulation as formulation


def run_single_depot_general_model(depots,
                                   customers,
                                   transportation_matrix,
                                   vehicles):

    print('Running Single Depot General Model')

    print('Getting model inputs')
    model_inputs = inputs.ModelInputs(transportation_matrix, customers, depots, vehicles)

    print('Model')
    model = formulation.ModelFormulation(model_inputs.time_variables_dict,
                                         model_inputs.assignment_variables_dict,
                                         model_inputs.vertices_dict,
                                         model_inputs.vehicles_dict,
                                         model_inputs.customers_dict,
                                         model_inputs.transit_dict,
                                         model_inputs.transit_starting_customers_dict,
                                         depots['LOCATION_NAME'].iloc[0]
                                         )
    print('Formulating the problem')
    model.formulate_problem()

    print('Solving the model')
    model.solve_model()

    print('Getting model results')
    model.get_model_solution()

    return model.solution_path
