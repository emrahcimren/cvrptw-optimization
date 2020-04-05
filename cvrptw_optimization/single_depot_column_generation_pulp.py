from cvrptw_optimization.src import single_depot_general_model_pulp_inputs as inputs
from cvrptw_optimization.src import single_depot_general_model_pulp_formulation as formulation


def run_single_depot_column_generation(depots,
                                   customers,
                                   transportation_matrix,
                                   vehicles,
                                   bigm=100000000,
                                   mip_gap=0.001,
                                   solver_time_limit_minutes=10,
                                   enable_solution_messaging=1,
                                   solver_type='PULP_CBC_CMD'
                                   ):

    print('Running Single Depot Column Generation Model')

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
    model.formulate_problem(bigm)

    print('Solving the model')
    model.solve_model(mip_gap,
                      solver_time_limit_minutes,
                      enable_solution_messaging,
                      solver_type)

    print('Getting model results')
    model.get_model_solution()

    return model.solution_objective, model.solution_path
