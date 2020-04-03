'''
Test class for testing general model
'''

import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'cvrptw_optimization')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'cvrptw_optimization/src')))
from cvrptw_optimization.src import data as dat

depots = dat.depots_unit_test
customers = dat.customers_unit_test
transportation_matrix = dat.transportation_matrix_unit_test
vehicles = dat.vehicles_unit_test.head(2)


class SingleDepotTest(unittest.TestCase):

    def test_single_depot_general_model_pulp(self):
        '''
        Test for the single depot problem
        :return:
        '''

        from cvrptw_optimization.src import single_depot_general_model_pulp_inputs as inputs
        from cvrptw_optimization.src import single_depot_general_model_pulp_formulation as formulation

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

        self.assertTrue(len(model.solution_path) > 0)


if __name__ == '__main__':
    unittest.main()
