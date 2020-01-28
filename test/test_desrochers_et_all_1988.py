'''
Test class for testing desrochers_et_all_1988.py
'''

import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../cvrptw_optimization')))
from cvrptw_optimization import desrochers_et_all_1988 as d
from cvrptw_optimization.src import data as test_data
from cvrptw_optimization.src import desrochers_et_all_1988_helpers as he
from cvrptw_optimization.src import desrochers_et_all_1988_inputs as ip


class DesrochersTest(unittest.TestCase):

    def test_desrochers_et_all_1988_inputs(self):
        '''
        Test for desrochers_et_all_1988_inputs
        :return:
        '''
        locations_name_list = list(test_data.locations['LOCATION_NAME'].unique())
        depot_name_list = list(test_data.depot['LOCATION_NAME'].unique())
        transportation_matrix = he.filter_transportation_matrix(test_data.transportation_matrix, locations_name_list,
                                                                depot_name_list)
        transportation_matrix = he.prepare_transportation_matrix(transportation_matrix, depot_name_list)

        inputs = ip.ModelInputs(transportation_matrix,
                                test_data.locations,
                                test_data.depot,
                                test_data.vehicles)

        self.assertTrue(len(inputs.t) > 0)

    def test_desrochers_et_all_1988(self):
        '''
        Test for desrochers_et_all_1988
        :return:
        '''

        solution = d.run_desrochers_et_all_1988(test_data.depot,
                                                test_data.locations,
                                                test_data.transportation_matrix,
                                                test_data.vehicles,
                                                solver_time_limit_mins=1,
                                                solver='or tools',
                                                fix_team=True)
        self.assertTrue(len(solution) > 0)


if __name__ == '__main__':
    unittest.main()
