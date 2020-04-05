'''
Input data sets
CVRPTW formulation
'''
from pulp import *
import pandas as pd


class ModelFormulation:

    def __init__(self, time_variables_dict,
                 assignment_variables_dict,
                 vertices_dict,
                 vehicles_dict,
                 customers_dict,
                 transit_dict,
                 transit_starting_customers_dict,
                 depot_name):

        self.time_variables_dict = time_variables_dict
        self.assignment_variables_dict = assignment_variables_dict
        self.vertices_dict = vertices_dict
        self.vehicles_dict = vehicles_dict
        self.customers_dict = customers_dict
        self.transit_dict = transit_dict
        self.transit_starting_customers_dict = transit_starting_customers_dict
        self.depot_name = depot_name

        # model variables
        self.time_var = None
        self.assignment_var = None
        self.model = None

        # model results
        self.solution_assignment = None
        self.solution_time = None
        self.solution_path = None

    def formulate_problem(self,
                          bigm=100000000):
        '''
        Formulate problem
        :param bigm:
        :return:
        '''
        self.time_var = pulp.LpVariable.dicts("Time", self.time_variables_dict.keys(), 0, None, pulp.LpContinuous)
        self.assignment_var = pulp.LpVariable.dicts("Assign", self.assignment_variables_dict.keys(), 0, 1,
                                                    pulp.LpBinary)  # Binary

        self.model = pulp.LpProblem("CVRPTW", pulp.LpMinimize)

        # objective function
        print('objective function')
        self.model += pulp.lpSum(
            self.transit_dict['TRANSPORTATION_COST'][from_loc, to_loc] * self.assignment_var[from_loc, to_loc, vehicle]
            for
            from_loc, to_loc, vehicle in self.assignment_variables_dict.keys())

        # Each vehicle can only be used at most once
        print('Each vehicle can only be used at most once')
        for customer in self.customers_dict['DEMAND'].keys():
            outgoing_arcs = []
            for from_loc, to_loc in self.transit_dict['DRIVE_MINUTES'].keys():
                if from_loc == customer:
                    outgoing_arcs.append(to_loc)

            self.model += pulp.lpSum(
                [self.assignment_var[customer, to_loc, vehicle] for to_loc in outgoing_arcs for vehicle in
                 self.vehicles_dict['CAPACITY'].keys()]) == 1, "customerVisit" + str(
                customer) + 'k'

        # Each vehicle should leave from a depot
        print('Each vehicle should leave from a depot')
        depot_leave = self.depot_name + '_LEAVE'
        for vehicle in self.vehicles_dict['CAPACITY'].keys():
            self.model += pulp.lpSum([self.assignment_var[depot_leave, customer, vehicle]
                                      for customer in
                                      self.customers_dict['DEMAND'].keys()]) == 1, "entryDepotConnection" + str(
                vehicle)

        # Flow in Flow Out
        print('Flow in Flow out')
        for customer in self.customers_dict['DEMAND'].keys():
            for vehicle in self.vehicles_dict['CAPACITY'].keys():
                incoming_arcs = []
                outgoing_arcs = []

                for from_loc, to_loc, temp_vehicle in self.assignment_variables_dict.keys():
                    if (to_loc == customer) & (temp_vehicle == vehicle):
                        incoming_arcs.append(from_loc)
                    if (from_loc == customer) & (temp_vehicle == vehicle):
                        outgoing_arcs.append(to_loc)

                self.model += pulp.lpSum(
                    [self.assignment_var[from_loc, customer, vehicle] for from_loc in incoming_arcs]) - pulp.lpSum(
                    [self.assignment_var[customer, to_loc, vehicle] for to_loc in outgoing_arcs]) == 0, "forTrip" + str(
                    customer) + 'k' + str(vehicle)

        # Each vehicle should enter a depot
        print('Each vehicle should enter a depot')
        depot_enter = self.depot_name + '_ENTER'
        for vehicle in self.vehicles_dict['CAPACITY'].keys():
            self.model += pulp.lpSum([self.assignment_var[customer, depot_enter, vehicle]
                                      for customer in
                                      self.customers_dict['DEMAND'].keys()]) == 1, "exitDepotConnection" + str(
                vehicle)

        # vehicle Capacity
        print('vehicle Capacity')
        for vehicle in self.vehicles_dict['CAPACITY'].keys():
            self.model += pulp.lpSum(
                [float(self.customers_dict['DEMAND'][from_loc]) * self.assignment_var[from_loc, to_loc, vehicle]
                 for from_loc, to_loc in
                 self.transit_starting_customers_dict['DRIVE_MINUTES'].keys()]) <= float(
                self.vehicles_dict['CAPACITY'][vehicle]), "Capacity" + str(vehicle)

        # Time intervals
        print('time intervals')
        for from_loc, to_loc, vehicle in self.assignment_variables_dict.keys():
            stop_time = 0
            if from_loc != depot_leave:
                stop_time = self.customers_dict['STOP_TIME'][from_loc]
            self.model += self.time_var[to_loc, vehicle] - self.time_var[from_loc, vehicle] >= \
                          self.transit_dict['DRIVE_MINUTES'][
                              from_loc, to_loc] + stop_time + bigm * self.assignment_var[
                              from_loc, to_loc, vehicle] - bigm, "timewindow" + str(vehicle) + 'p' + str(
                from_loc) + 'p' + str(to_loc)

        # Time Windows
        print('time windows')
        for vertex, vehicle in self.time_variables_dict.keys():
            self.time_var[vertex, vehicle].bounds(float(self.vertices_dict['TIME_WINDOW_START'][vertex]),
                                                  float(self.vertices_dict['TIME_WINDOW_END'][vertex]))

    def solve_model(self,
                    mip_gap=0.001,
                    solver_time_limit_minutes=10,
                    enable_solution_messaging=1,
                    solver_type='PULP_CBC_CMD'):
        '''
        Solve model
        :param mip_gap:
        :param solver_time_limit_minutes:
        :param enable_solution_messaging:
        :param solver_type:
        :return:
        '''

        print('solving model')
        if solver_type == 'PULP_CBC_CMD':
            self.model.solve(PULP_CBC_CMD(
                msg=enable_solution_messaging,
                maxSeconds=60 * solver_time_limit_minutes,
                fracGap=mip_gap)
            )

    def get_model_solution(self):
        '''
        Get model results
        :return:
        '''
        if self.model.status == 1:

            print('problem is feasible')

            # get assignment variable values
            print('getting solution for assignment variables')
            solution_assignment = []
            for from_loc, to_loc, vehicle in self.assignment_variables_dict.keys():
                if self.assignment_var[from_loc, to_loc, vehicle].value() > 0:
                    solution_assignment.append({'FROM_LOCATION_NAME': from_loc,
                                                'TO_LOCATION_NAME': to_loc,
                                                'VEHICLE': vehicle,
                                                'VALUE': self.assignment_var[from_loc, to_loc, vehicle].value(),
                                                'DRIVE_MINUTES': self.transit_dict['DRIVE_MINUTES'][from_loc, to_loc],
                                                'TRANSPORTATION_COST': self.transit_dict['TRANSPORTATION_COST'][
                                                    from_loc, to_loc]
                                                })

            self.solution_assignment = pd.DataFrame(solution_assignment)

            # get time variable values
            print('getting solution for time variables')
            solution_time = []
            for loc, vehicle in self.time_var.keys():
                if self.time_var[loc, vehicle].value() > 0:
                    demand = 0
                    stop_time = 0
                    if loc in self.customers_dict['DEMAND'].keys():
                        demand = self.customers_dict['DEMAND'][loc]
                        stop_time = self.customers_dict['STOP_TIME'][loc]

                    solution_time.append({'LOCATION_NAME': loc,
                                          'VEHICLE': vehicle,
                                          'START_TIME': self.time_var[loc, vehicle].value(),
                                          'END_TIME': self.time_var[loc, vehicle].value() + stop_time,
                                          'DEMAND': demand,
                                          'STOP_TIME': stop_time,
                                          'TIME_WINDOW_START': self.vertices_dict['TIME_WINDOW_START'][loc],
                                          'TIME_WINDOW_END': self.vertices_dict['TIME_WINDOW_END'][loc],
                                          'VEHICLE_CAPACITY': self.vehicles_dict['CAPACITY'][vehicle]
                                          })

            self.solution_time = pd.DataFrame(solution_time)

            print('Creating Paths')
            vehicles_list = self.solution_assignment['VEHICLE'].unique()
            solution_path = []
            for vehicle in vehicles_list:
                route = self.solution_assignment[self.solution_assignment['VEHICLE'] == vehicle]
                path = list(set(route['FROM_LOCATION_NAME'].to_list() + route['TO_LOCATION_NAME'].to_list()))
                times = self.solution_time[self.solution_time['VEHICLE'] == vehicle]
                times = times[times['LOCATION_NAME'].isin(path)]
                times.sort_values(['START_TIME'], inplace=True)
                times['STOP_NUMBER'] = range(0, len(times))
                times['PREVIOUS_LOCATION_NAME'] = times['LOCATION_NAME'].shift(1)
                route.rename(
                    columns={'FROM_LOCATION_NAME': 'PREVIOUS_LOCATION_NAME', 'TO_LOCATION_NAME': 'LOCATION_NAME'},
                    inplace=True)
                times = times.merge(route, how='left', on=['PREVIOUS_LOCATION_NAME', 'LOCATION_NAME', 'VEHICLE'])
                times['ORIGINAL_LOCATION_NAME'] = times['LOCATION_NAME']
                times['ORIGINAL_LOCATION_NAME'] = times['ORIGINAL_LOCATION_NAME'].str.replace('_ENTER', '')
                times['ORIGINAL_LOCATION_NAME'] = times['ORIGINAL_LOCATION_NAME'].str.replace('_LEAVE', '')
                times.drop(['VALUE'], 1, inplace=True)
                solution_path.append(times)
            self.solution_path = pd.concat(solution_path)

        else:
            raise Exception('No Solution Exists')
