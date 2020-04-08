import pandas as pd

from cvrptw_optimization.src import single_depot_column_generation_pulp_inputs as inputs
from cvrptw_optimization.src import single_depot_column_generation_pulp_problem_formulation as formulation


def initiate_single_depot_column_generation(depots,
                                            customers,
                                            transportation_matrix,
                                            vehicles
                                            ):
    '''
    Function to initiate column generation algorithm
    :param depots:
    :param customers:
    :param transportation_matrix:
    :param vehicles:
    :return:
    '''

    print('Initiating Single Depot Column Generation Model')

    print('Getting model inputs')
    model_inputs = inputs.ModelInputs(transportation_matrix, customers, depots, vehicles)
    model_inputs.create_initial_paths()

    print('Column generation formuation')
    depot_name = model_inputs.depot_names[0]
    model_formulation = formulation.ColumnGenerationFormulation(model_inputs.time_variables_dict,
                                                                model_inputs.assignment_variables_dict,
                                                                model_inputs.vertices_dict,
                                                                model_inputs.customers_dict,
                                                                model_inputs.transit_dict,
                                                                model_inputs.transit_starting_customers_dict,
                                                                depot_name)

    return model_inputs, model_formulation


def run_single_depot_column_generation(depots,
                                       customers,
                                       transportation_matrix,
                                       vehicles,
                                       capacity,
                                       mip_gap=0.001,
                                       solver_time_limit_minutes=10,
                                       enable_solution_messaging=0,
                                       solver_type='PULP_CBC_CMD',
                                       max_iteration=50):

    '''
    Function to run the column generation algorithm
    :param depots:
    :param customers:
    :param transportation_matrix:
    :param vehicles:
    :param capacity:
    :param mip_gap:
    :param solver_time_limit_minutes:
    :param enable_solution_messaging:
    :param solver_type:
    :param max_iteration:
    :return:
    '''

    model_inputs, model_formulation = initiate_single_depot_column_generation(depots,
                                                                              customers,
                                                                              transportation_matrix,
                                                                              vehicles)

    paths_dict = model_inputs.paths_dict.copy()

    iteration = 0
    solution_subproblem = []
    while True:

        print("Column Generation Iteration: ", iteration)

        # solve master problem
        print('Solving master problem')
        paths_cost_dict = model_inputs.calculate_path_costs(paths_dict, model_inputs.transit_dict)
        paths_customers_dict = model_inputs.calculate_path_customer_allocation(paths_dict, list(
            model_inputs.customers_dict['DEMAND'].keys()))

        model_name = str(iteration) + 'MASP'
        price, solution_master_model_objective, solution_master_path = model_formulation.formulate_and_solve_master_problem(
            paths_dict,
            paths_cost_dict,
            paths_customers_dict,
            lp_file_name=model_name,
            mip_gap=0.001,
            solver_time_limit_minutes=10,
            enable_solution_messaging=1,
            solver_type='PULP_CBC_CMD'
        )

        print("Dual values: ", price)

        # solve sub-problem
        print('Solving sub-problem')
        path_name = 'PATH ' + str(len(paths_dict))
        model_name = str(iteration)+'SUBP'
        solution_objective, solution_path, sub_model = model_formulation.formulate_and_solve_subproblem(price,
                                                                                                        capacity,
                                                                                                        path_name,
                                                                                                        lp_file_name=model_name,
                                                                                                        bigm=1000000,
                                                                                                        mip_gap=0.0001,
                                                                                                        solver_time_limit_minutes=10,
                                                                                                        enable_solution_messaging=0,
                                                                                                        solver_type='PULP_CBC_CMD'
                                                                                                        )
        solution_subproblem.append(solution_path)
        print("Master LP problem objective value: ", solution_master_model_objective)
        print("Sub-problem Objective value: ", solution_objective)

        # check if
        if (solution_objective > -1) or iteration == max_iteration:
            break
        else:
            paths_dict[path_name] = solution_path['LOCATION_NAME'].tolist()

        iteration += 1

    solution_subproblem = pd.concat(solution_subproblem)
    solution_subproblem.rename(columns={'OBJECTIVE': 'OBJECTIVE_SUBPROBLEM'}, inplace=True)
    solution_master_path.rename(columns={'OBJECTIVE': 'OBJECTIVE_MASTERPROBLEM'}, inplace=True)

    # Setup all variables to integers and solve the master problem

    final_solution = solution_master_path.merge(solution_subproblem, how='left', on=['PATH_NAME'])

    return final_solution
