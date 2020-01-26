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

    def test_desrochers_et_all_1988(self):
        '''
        Test for desrochers_et_all_1988
        :return:
        '''

        solution = d.run_desrochers_et_all_1988(test_data.depot,
                                                test_data.locations,
                                                test_data.transportation_matrix,
                                                test_data.vehicles,
                                                maximum_travel_hours=22,
                                                solver_time_limit_mins=2,
                                                solver='or tools')

        self.assertTrue(len(solution) > 0)


if __name__ == '__main__':
    unittest.main()
