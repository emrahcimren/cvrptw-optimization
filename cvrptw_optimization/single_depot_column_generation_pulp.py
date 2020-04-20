import pandas as pd
import numpy as np

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


def process_paths(master_path, transit_dict, customers_dict, vertices_dict):
    '''
    Function to process final master problem results
    :param master_path:
    :param transit_dict:
    :param customers_dict:
    :param vertices_dict:
    :return:
    '''

    solution = master_path.explode('PATH').reset_index(drop=True)
    solution['STOP_NUMBER'] = solution.groupby(['PATH_NAME']).cumcount() + 1
    solution['LOCATION_NAME'] = solution['PATH']
    solution['PREVIOUS_LOCATION_NAME'] = solution.groupby(['PATH_NAME'])['LOCATION_NAME'].shift(1)
    solution['ORIGINAL_LOCATION_NAME'] = solution['LOCATION_NAME']
    solution['ORIGINAL_LOCATION_NAME'] = solution['ORIGINAL_LOCATION_NAME'].str.replace('_ENTER', '')
    solution['ORIGINAL_LOCATION_NAME'] = solution['ORIGINAL_LOCATION_NAME'].str.replace('_LEAVE', '')
    solution['DRIVE_MINUTES'] = np.nan
    solution['TRANSPORTATION_COST'] = np.nan
    solution['TIME_WINDOW_START'] = np.nan
    solution['STOP_TIME'] = 0
    solution['TIME_WINDOW_END'] = np.nan
    solution['DEMAND'] = 0

    for idx, row in solution.iterrows():
        if (row.PREVIOUS_LOCATION_NAME, row.LOCATION_NAME) in transit_dict['TRANSPORTATION_COST'].keys():
            solution['DRIVE_MINUTES'][idx] = transit_dict['DRIVE_MINUTES'][
                row.PREVIOUS_LOCATION_NAME, row.LOCATION_NAME]
            solution['TRANSPORTATION_COST'][idx] = transit_dict['TRANSPORTATION_COST'][
                row.PREVIOUS_LOCATION_NAME, row.LOCATION_NAME]

        if row.LOCATION_NAME in customers_dict['STOP_TIME'].keys():
            solution['STOP_TIME'][idx] = customers_dict['STOP_TIME'][row.LOCATION_NAME]
            solution['DEMAND'][idx] = customers_dict['DEMAND'][row.LOCATION_NAME]

        if row.LOCATION_NAME in vertices_dict['TIME_WINDOW_START'].keys():
            solution['TIME_WINDOW_START'][idx] = vertices_dict['TIME_WINDOW_START'][row.LOCATION_NAME]
            solution['TIME_WINDOW_END'][idx] = vertices_dict['TIME_WINDOW_END'][row.LOCATION_NAME]

        solution['START_TIME'] = solution['TIME_WINDOW_START']

    return solution


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
    :return: solution, algorithm master problem and subproblem objectives
    '''

    model_inputs, model_formulation = initiate_single_depot_column_generation(depots,
                                                                              customers,
                                                                              transportation_matrix,
                                                                              vehicles)

    paths_dict = model_inputs.paths_dict.copy()

    iteration = 0
    solution_statistics = []
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
            binary_model=False,
            lp_file_name=None,
            mip_gap=mip_gap,
            solver_time_limit_minutes=solver_time_limit_minutes,
            enable_solution_messaging=enable_solution_messaging,
            solver_type=solver_type
        )

        print("Dual values: ", price)

        # solve sub-problem
        print('Solving sub-problem')
        path_name = 'PATH ' + str(len(paths_dict))
        model_name = str(iteration) + 'SUBP'
        solution_objective, solution_path, sub_model = model_formulation.formulate_and_solve_subproblem(price,
                                                                                                        capacity,
                                                                                                        path_name,
                                                                                                        lp_file_name=None,
                                                                                                        bigm=1000000,
                                                                                                        mip_gap=mip_gap,
                                                                                                        solver_time_limit_minutes=solver_time_limit_minutes,
                                                                                                        enable_solution_messaging=enable_solution_messaging,
                                                                                                        solver_type=solver_type
                                                                                                        )

        print("Master LP problem objective value: ", solution_master_model_objective)
        print("Sub-problem Objective value: ", solution_objective)
        solution_statistics.append({'ITERATION': iteration,
                                    'MASTER_PROBLEM_OBJECTIVE': solution_master_model_objective,
                                    'SUB_PROBLEM_OBJECTIVE': solution_objective})

        # check if
        if (solution_objective > -1) or iteration == max_iteration:
            break
        else:
            paths_dict[path_name] = solution_path['LOCATION_NAME'].tolist()

        iteration += 1

    # Setup all variables to integers and solve the master problem
    print("Setup all variables to integers and solve the master problem")
    final_price, final_solution_master_model_objective, final_solution_master_path = model_formulation.formulate_and_solve_master_problem(
        paths_dict,
        paths_cost_dict,
        paths_customers_dict,
        binary_model=True,
        lp_file_name=None,
        mip_gap=mip_gap,
        solver_time_limit_minutes=solver_time_limit_minutes,
        enable_solution_messaging=enable_solution_messaging,
        solver_type=solver_type
    )

    print("Master Binary problem objective value: ", final_solution_master_model_objective)

    print("Compiling solution")
    solution = process_paths(final_solution_master_path,
                             model_inputs.transit_dict,
                             model_inputs.customers_dict,
                             model_inputs.vertices_dict)

    return solution, solution_statistics
