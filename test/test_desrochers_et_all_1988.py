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


class DesrochersTest(unittest.TestCase):

    def set_up(self):

        self.input_locations = test_data.locations_test
        self.input_locations_with_clusters = test_data.locations_with_clusters_test
        self.number_of_clusters = len(test_data.locations_with_clusters_test.CLUSTER.unique())
        self.minimum_elements_in_a_cluster = test_data.minimum_elements_in_a_cluster
        self.maximum_elements_in_a_cluster = test_data.maximum_elements_in_a_cluster
        self.maximum_iteration = test_data.maximum_iteration
        self.objective_range = test_data.objective_range
        self.enable_minimum_maximum_elements_in_a_cluster = test_data.enable_minimum_maximum_elements_in_a_cluster

    def test_desrochers_et_all_1988(self):
        '''
        Test for desrochers_et_all_1988
        :return:
        '''

        self.set_up()

        solution = d.run_desrochers_et_all_1988(test_data.depot,
                                                test_data.locations,
                                                test_data.transportation_matrix,
                                                test_data.vehicles,
                                                test_data.maximum_travel_hours,
                                                solver_time_limit_mins=2,
                                                solver='ortools')

        self.assertTrue(len(solution) > 0)


if __name__ == '__main__':
    unittest.main()
