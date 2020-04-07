'''
Input data sets
CVRPTW formulation
'''
import numpy as np
from itertools import product


class ModelInputs:

    def __init__(self, transportation_matrix, customers, depots, vehicles):
        transportation_matrix = transportation_matrix[
            transportation_matrix['FROM_LOCATION_NAME'] != transportation_matrix['TO_LOCATION_NAME']]
        self.depot_names = depots['LOCATION_NAME'].unique()

        self.transportation_matrix = transportation_matrix
        self.customers = customers
        self.depots_original = depots
        self.depots = depots

        self.vehicles = vehicles

        # calculated
        self.transportation_matrix_starting_customers = None
        self.customers_dict = None
        self.depots_dict = None
        self.transit_dict = None
        self.transit_starting_customers_dict = None
        self.vehicles_dict = None
        self.paths = None
        self.paths_list = None
        self.paths_dict = None

        self.vertices = None
        self.vertices_dict = None

        self.time_variables_dict = None
        self.assignment_variables_dict = None

        self.update_depot_names()
        self.create_vertices()
        self.create_customers()
        self.create_depots()
        self.create_transit()
        self.create_vehicles()
        self.create_assignment_variables()
        self.create_time_variables()

    @staticmethod
    def _create_parameter_dict(parameter_df, keys, value):
        '''
        Function to create parameters dictionary
        :param parameter_df:
        :param keys:
        :param value:
        :return:
        '''
        parameter_df = parameter_df.set_index(keys)
        return parameter_df[value].to_dict()

    def update_depot_names(self):
        '''
        Updated depot names
        :return:
        '''
        filter_from_locs = self.transportation_matrix['FROM_LOCATION_NAME'].isin(self.depot_names)
        self.transportation_matrix_starting_customers = self.transportation_matrix[~filter_from_locs]
        self.transportation_matrix.loc[filter_from_locs, 'FROM_LOCATION_NAME'] = self.transportation_matrix.loc[
                                                                                     filter_from_locs, 'FROM_LOCATION_NAME'] + '_LEAVE'

        filter_to_locs = self.transportation_matrix['TO_LOCATION_NAME'].isin(self.depot_names)
        self.transportation_matrix.loc[filter_to_locs, 'TO_LOCATION_NAME'] = self.transportation_matrix.loc[
                                                                                 filter_to_locs, 'TO_LOCATION_NAME'] + '_ENTER'

        filter_to_locs = self.transportation_matrix_starting_customers['TO_LOCATION_NAME'].isin(self.depot_names)
        self.transportation_matrix_starting_customers.loc[filter_to_locs, 'TO_LOCATION_NAME'] = self.transportation_matrix_starting_customers.loc[
                                                                                 filter_to_locs, 'TO_LOCATION_NAME'] + '_ENTER'

        depots_leave = self.depots.copy()
        depots_leave['LOCATION_NAME'] = depots_leave['LOCATION_NAME'] + '_LEAVE'
        depots_enter = self.depots.copy()
        depots_enter['LOCATION_NAME'] = depots_enter['LOCATION_NAME'] + '_ENTER'
        self.depots = depots_leave.append(depots_enter)

    def create_vertices(self):
        '''
        Create vertices
        :return:
        '''
        self.vertices = self.depots[['LOCATION_NAME', 'TIME_WINDOW_START', 'TIME_WINDOW_END']].append(
            self.customers[['LOCATION_NAME', 'TIME_WINDOW_START', 'TIME_WINDOW_END']])
        self.vertices_dict = self._create_parameter_dict(self.vertices,
                                                         ['LOCATION_NAME'],
                                                         ['TIME_WINDOW_START', 'TIME_WINDOW_END'])

    def create_customers(self):
        '''
        Create customers
        :return:
        '''
        self.customers_dict = self._create_parameter_dict(self.customers, ['LOCATION_NAME'],
                                                          ['DEMAND', 'STOP_TIME', 'TIME_WINDOW_START',
                                                           'TIME_WINDOW_END'])

    def create_depots(self):
        '''
        Create depots
        :return:
        '''
        self.depots_dict = self._create_parameter_dict(self.depots, ['LOCATION_NAME'],
                                                       ['MAXIMUM_CAPACITY', 'TIME_WINDOW_START', 'TIME_WINDOW_END'])

    def create_vehicles(self):
        '''
        Create vehicles
        :return:
        '''
        self.vehicles_dict = self._create_parameter_dict(self.vehicles, ['VEHICLE_NAME'],
                                                         ['CAPACITY', 'VEHICLE_FIXED_COST'])

    def create_transit(self):
        '''
        Create transit dictionary
        :return:
        '''
        self.transit_dict = self._create_parameter_dict(self.transportation_matrix,
                                                        ['FROM_LOCATION_NAME', 'TO_LOCATION_NAME'],
                                                        ['DRIVE_MINUTES', 'TRANSPORTATION_COST'])

        self.transit_starting_customers_dict = self._create_parameter_dict(
            self.transportation_matrix_starting_customers,
            ['FROM_LOCATION_NAME', 'TO_LOCATION_NAME'],
            ['DRIVE_MINUTES', 'TRANSPORTATION_COST'])

    def create_assignment_variables(self):
        '''
        Create assignment variables set
        :return:
        '''
        self.assignment_variables_dict = {}
        #for tup in product(self.transit_dict['DRIVE_MINUTES'].keys(), self.vehicles_dict['CAPACITY'].keys()):
        for tup in self.transit_dict['DRIVE_MINUTES'].keys():
            self.assignment_variables_dict[tup[0], tup[1]] = 0

    def create_time_variables(self):
        '''
        Create time variables set
        :return:
        '''
        self.time_variables_dict = {}
        #for tup in product(self.vertices['LOCATION_NAME'], self.vehicles_dict['CAPACITY'].keys()):
        for tup in self.vertices['LOCATION_NAME']:
            self.time_variables_dict[tup] = 0

    def create_initial_paths(self):
        '''
        Function to create initial paths
        :return:
        '''

        self.paths = self.customers.copy()
        self.paths['PATH_NAME'] = range(len(self.paths))
        self.paths['PATH_NAME'] = 'PATH ' + self.paths['PATH_NAME'].astype(str)
        self.paths_list = list(zip(self.paths['PATH_NAME'], self.paths['LOCATION_NAME']))
        self.paths_dict = {}
        for path in self.paths_list:
            self.paths_dict[path[0]] = [self.depot_names[0] + '_LEAVE', path[1], self.depot_names[0] + '_ENTER']

    def calculate_path_costs(self, paths_dict, transit_dict):
        '''
        Calcuate path costs
        :param paths_dict:
        :param transit_dict:
        :return:
        '''
        paths_cost_dict = {}
        for path in paths_dict.keys():
            trans_cost = 0
            for path_idx in range(0, len(paths_dict[path])-1):
                trans_cost = trans_cost + transit_dict['TRANSPORTATION_COST'][paths_dict[path][path_idx], paths_dict[path][path_idx+1]]
            paths_cost_dict[path] = trans_cost

        return paths_cost_dict

    def calculate_path_customer_allocation(self, paths_dict, customers_list):
        '''
        Calculate customer allocation
        :param paths_dict:
        :param customers_list:
        :return:
        '''

        paths_customers_dict = {}
        for path in paths_dict.keys():
            for customer in customers_list:
                if customer in paths_dict[path]:
                    paths_customers_dict[path, customer] = 1
                else:
                    paths_customers_dict[path, customer] = 0

        return paths_customers_dict
