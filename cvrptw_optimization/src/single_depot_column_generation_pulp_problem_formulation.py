'''
CVRPTW master and sub formulation
'''
from pulp import *
import pandas as pd


class ColumnGenerationFormulation:

    def __init__(self,
                 time_variables_dict,
                 assignment_variables_dict,
                 vertices_dict,
                 customers_dict,
                 transit_dict,
                 transit_starting_customers_dict,
                 depot_name):

        self.time_variables_dict = time_variables_dict
        self.assignment_variables_dict = assignment_variables_dict
        self.vertices_dict = vertices_dict
        self.depot_leave = depot_name + '_LEAVE'
        self.depot_enter = depot_name + '_ENTER'
        self.customers_dict = customers_dict
        self.transit_dict = transit_dict
        self.transit_starting_customers_dict = transit_starting_customers_dict

    def formulate_and_solve_master_problem(self,
                                           paths_dict,
                                           paths_cost_dict,
                                           paths_customers_dict,
                                           lp_file_name=None,
                                           mip_gap=0.001,
                                           solver_time_limit_minutes=10,
                                           enable_solution_messaging=1,
                                           solver_type='PULP_CBC_CMD'
                                           ):

        '''
        Formulate and solve master problem
        :param paths_dict:
        :param paths_cost_dict:
        :param paths_customers_dict:
        :param lp_file_name:
        :param mip_gap:
        :param solver_time_limit_minutes:
        :param enable_solution_messaging:
        :param solver_type:
        :return:
        '''

        master_model = pulp.LpProblem("MA_CVRPTW", pulp.LpMinimize)
        path_var = pulp.LpVariable.dicts("Path", paths_dict.keys(), 0, 1, pulp.LpContinuous)
        print('Master model objective function')
        master_model += pulp.lpSum(paths_cost_dict[path] * path_var[path] for path in paths_dict.keys())

        print('Each customer belongs to one path')
        for customer in self.customers_dict['DEMAND'].keys():
            master_model += pulp.lpSum(
                [paths_customers_dict[path, customer] * path_var[path] for path in
                 paths_dict.keys()]) == 1, "Customer" + str(customer)

        if lp_file_name is not None:
            master_model.writeLP('{}.lp'.format(str(lp_file_name)))

        if solver_type == 'PULP_CBC_CMD':
            master_model.solve(PULP_CBC_CMD(
                msg=enable_solution_messaging,
                maxSeconds=60 * solver_time_limit_minutes,
                fracGap=mip_gap)
            )

        if master_model.status == 1:

            solution_master_model_objective = value(master_model.objective)
            print('Master model objective = {}'.format(str(solution_master_model_objective)))

            price = {}
            for customer in self.customers_dict['DEMAND'].keys():
                price[customer] = float(master_model.constraints["Customer" + str(customer).replace(" ", "_")].pi)
            print("Dual values: ", price)

            for name, c in list(master_model.constraints.items()):
                print(name, ":", c, "\t", c.pi, "\t\t", c.slack)

            solution_master_path = []
            for path in path_var.keys():
                if path_var[path].value() > 0:
                    solution_master_path.append({'PATH_NAME': path,
                                                 'VALUE': path_var[path].value(),
                                                 'PATH': paths_dict[path]
                                                 })
            solution_master_path = pd.DataFrame(solution_master_path)
            solution_master_path['OBJECTIVE'] = solution_master_model_objective

            return price, solution_master_model_objective, solution_master_path

        else:
            raise Exception('No Solution Exists')

    def formulate_and_solve_subproblem(self,
                                       price,
                                       capacity,
                                       path_name,
                                       lp_file_name = None,
                                       bigm=1000000,
                                       mip_gap=0.001,
                                       solver_time_limit_minutes=10,
                                       enable_solution_messaging=1,
                                       solver_type='PULP_CBC_CMD'
                                       ):
        '''
        Formulate and solve subproblem
        :param price:
        :param capacity:
        :param path_name:
        :param lp_file_name:
        :param bigm:
        :param mip_gap:
        :param solver_time_limit_minutes:
        :param enable_solution_messaging:
        :param solver_type:
        :return:
        '''

        # sub problem
        sub_model = pulp.LpProblem("SU_CVRPTW", pulp.LpMinimize)
        time_var = pulp.LpVariable.dicts("Time", self.time_variables_dict.keys(), 0, None, pulp.LpContinuous)
        assignment_var = pulp.LpVariable.dicts("Assign", self.assignment_variables_dict.keys(), 0, 1, pulp.LpBinary)

        print('objective function')
        objective_keys = []
        for from_loc, to_loc in self.assignment_variables_dict.keys():
            if from_loc != self.depot_leave:
                objective_keys.append([from_loc, to_loc])

        sub_model += pulp.lpSum(
            self.transit_dict['TRANSPORTATION_COST'][from_loc, to_loc] * assignment_var[from_loc, to_loc] -
            price[from_loc] * assignment_var[from_loc, to_loc]
            for from_loc, to_loc in objective_keys
        )

        # Each vehicle should leave from a depot
        print('Each vehicle should leave from a depot')
        sub_model += pulp.lpSum([assignment_var[self.depot_leave, customer]
                                 for customer in
                                 self.customers_dict['DEMAND'].keys()]) == 1, "entryDepotConnection"

        # Flow in Flow Out
        print('Flow in Flow out')
        for customer in self.customers_dict['DEMAND'].keys():
            incoming_arcs = []
            outgoing_arcs = []

            for from_loc, to_loc in self.assignment_variables_dict.keys():
                if to_loc == customer:
                    incoming_arcs.append(from_loc)
                if from_loc == customer:
                    outgoing_arcs.append(to_loc)

            sub_model += pulp.lpSum(
                [assignment_var[from_loc, customer] for from_loc in incoming_arcs]) - pulp.lpSum(
                [assignment_var[customer, to_loc] for to_loc in outgoing_arcs]) == 0, "forTrip" + str(
                customer)

        # Each vehicle should enter a depot
        print('Each vehicle should enter a depot')
        sub_model += pulp.lpSum([assignment_var[customer, self.depot_enter]
                                 for customer in
                                 self.customers_dict['DEMAND'].keys()]) == 1, "exitDepotConnection"

        # vehicle Capacity
        print('vehicle Capacity')
        sub_model += pulp.lpSum(
            [float(self.customers_dict['DEMAND'][from_loc]) * assignment_var[from_loc, to_loc]
             for from_loc, to_loc in
             self.transit_starting_customers_dict['DRIVE_MINUTES'].keys()]) <= float(capacity), "Capacity"

        # Time intervals
        print('time intervals')
        for from_loc, to_loc in self.assignment_variables_dict.keys():
            stop_time = 0
            if from_loc != self.depot_leave:
                stop_time = self.customers_dict['STOP_TIME'][from_loc]
            sub_model += time_var[to_loc] - time_var[from_loc] >= \
                         self.transit_dict['DRIVE_MINUTES'][
                             from_loc, to_loc] + stop_time + bigm * assignment_var[
                             from_loc, to_loc] - bigm, "timewindow" + str(
                from_loc) + 'p' + str(to_loc)

        # Time Windows
        print('time windows')
        for vertex in self.time_variables_dict.keys():
            time_var[vertex].bounds(float(self.vertices_dict['TIME_WINDOW_START'][vertex]),
                                    float(self.vertices_dict['TIME_WINDOW_END'][vertex]))

        if lp_file_name is not None:
            sub_model.writeLP('{}.lp'.format(str(lp_file_name)))

        if solver_type == 'PULP_CBC_CMD':
            sub_model.solve(PULP_CBC_CMD(
                msg=enable_solution_messaging,
                maxSeconds=60 * solver_time_limit_minutes,
                fracGap=mip_gap)
            )

        if pulp.LpStatus[sub_model.status] in ('Optimal', 'Undefined'):

            print('Model Status = {}'.format(pulp.LpStatus[sub_model.status]))
            print("The optimised objective function= ", value(sub_model.objective))

            solution_objective = value(sub_model.objective)

            # get assignment variable values
            print('getting solution for assignment variables')
            solution_assignment = []
            for from_loc, to_loc in self.assignment_variables_dict.keys():
                if assignment_var[from_loc, to_loc].value() > 0:
                    solution_assignment.append({'FROM_LOCATION_NAME': from_loc,
                                                'TO_LOCATION_NAME': to_loc,
                                                'VALUE': assignment_var[from_loc, to_loc].value(),
                                                'DRIVE_MINUTES': self.transit_dict['DRIVE_MINUTES'][from_loc, to_loc],
                                                'TRANSPORTATION_COST': self.transit_dict['TRANSPORTATION_COST'][
                                                    from_loc, to_loc]
                                                })

            solution_assignment = pd.DataFrame(solution_assignment)

            # get time variable values
            print('getting solution for time variables')
            solution_time = []
            for loc in time_var.keys():
                if time_var[loc].value() > 0:
                    demand = 0
                    stop_time = 0
                    if loc in self.customers_dict['DEMAND'].keys():
                        demand = self.customers_dict['DEMAND'][loc]
                        stop_time = self.customers_dict['STOP_TIME'][loc]

                    solution_time.append({'LOCATION_NAME': loc,
                                          'START_TIME': time_var[loc].value(),
                                          'END_TIME': time_var[loc].value() + stop_time,
                                          'DEMAND': demand,
                                          'STOP_TIME': stop_time,
                                          'TIME_WINDOW_START': self.vertices_dict['TIME_WINDOW_START'][loc],
                                          'TIME_WINDOW_END': self.vertices_dict['TIME_WINDOW_END'][loc],
                                          'VEHICLE_CAPACITY': capacity
                                          })

            solution_time = pd.DataFrame(solution_time)

            print('Creating Paths')
            route = solution_assignment.copy()
            path = list(set(route['FROM_LOCATION_NAME'].to_list() + route['TO_LOCATION_NAME'].to_list()))
            times = solution_time.copy()
            times = times[times['LOCATION_NAME'].isin(path)]
            times.sort_values(['START_TIME'], inplace=True)
            times['STOP_NUMBER'] = range(0, len(times))
            times['PREVIOUS_LOCATION_NAME'] = times['LOCATION_NAME'].shift(1)
            route.rename(
                columns={'FROM_LOCATION_NAME': 'PREVIOUS_LOCATION_NAME', 'TO_LOCATION_NAME': 'LOCATION_NAME'},
                inplace=True)
            times = times.merge(route, how='left', on=['PREVIOUS_LOCATION_NAME', 'LOCATION_NAME'])
            times['ORIGINAL_LOCATION_NAME'] = times['LOCATION_NAME']
            times['ORIGINAL_LOCATION_NAME'] = times['ORIGINAL_LOCATION_NAME'].str.replace('_ENTER', '')
            times['ORIGINAL_LOCATION_NAME'] = times['ORIGINAL_LOCATION_NAME'].str.replace('_LEAVE', '')
            times.drop(['VALUE'], 1, inplace=True)
            solution_path = times.copy()

            solution_path['PATH_NAME'] = path_name
            solution_path['OBJECTIVE'] = solution_objective

            return solution_objective, solution_path, sub_model

        else:
            print('Model Status = {}'.format(pulp.LpStatus[sub_model.status]))
            raise Exception('No Solution Exists for the Sub problem')
