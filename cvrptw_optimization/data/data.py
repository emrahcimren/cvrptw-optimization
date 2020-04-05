import pandas as pd
import os
current_dir, this_filename = os.path.split(__file__)

# unit test data
customers_unit_test = pd.read_pickle(os.path.join(current_dir, 'customers_unit_test.pkl'))
depots_unit_test = pd.read_pickle(os.path.join(current_dir, 'depots_unit_test.pkl'))
transportation_matrix_unit_test = pd.read_pickle(os.path.join(current_dir, 'transportation_matrix_unit_test.pkl'))
vehicles_unit_test = pd.read_pickle(os.path.join(current_dir, 'vehicles_unit_test.pkl'))

# smaller test set #
customers0 = pd.read_pickle(os.path.join(current_dir, 'customers0.pkl'))
depots0 = pd.read_pickle(os.path.join(current_dir, 'depots0.pkl'))
transportation_matrix0 = pd.read_pickle(os.path.join(current_dir, 'transportation_matrix0.pkl'))
vehicles0 = pd.read_pickle(os.path.join(current_dir, 'vehicles0.pkl'))

# larger test set
customers1 = pd.read_pickle(os.path.join(current_dir, 'customers1.pkl'))
depots1 = pd.read_pickle(os.path.join(current_dir, 'depots1.pkl'))
transportation_matrix1 = pd.read_pickle(os.path.join(current_dir, 'transportation_matrix1.pkl'))
vehicles1 = pd.read_pickle(os.path.join(current_dir, 'vehicles1.pkl'))
