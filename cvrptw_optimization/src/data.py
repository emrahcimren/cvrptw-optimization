import pandas as pd
import os
current_dir, this_filename = os.path.split(__file__)

# unit test data
customers_unit_test = pd.read_pickle(os.path.join(current_dir, '../data/customers_unit_test.pkl'))
depots_unit_test = pd.read_pickle(os.path.join(current_dir, '../data/depots_unit_test.pkl'))
transportation_matrix_unit_test = pd.read_pickle(os.path.join(current_dir, '../data/transportation_matrix_unit_test.pkl'))
vehicles_unit_test = pd.read_pickle(os.path.join(current_dir, '../data/vehicles_unit_test.pkl'))

# smaller test set #
customers0 = pd.read_pickle(os.path.join(current_dir, '../data/customers0.pkl'))
depots0 = pd.read_pickle(os.path.join(current_dir, '../data/depots0.pkl'))
transportation_matrix0 = pd.read_pickle(os.path.join(current_dir, '../data/transportation_matrix0.pkl'))
vehicles0 = pd.read_pickle(os.path.join(current_dir, '../data/vehicles0.pkl'))

# larger test set
customers1 = pd.read_pickle(os.path.join(current_dir, '../data/customers1.pkl'))
depots1 = pd.read_pickle(os.path.join(current_dir, '../data/depots1.pkl'))
transportation_matrix1 = pd.read_pickle(os.path.join(current_dir, '../data/transportation_matrix1.pkl'))
vehicles1 = pd.read_pickle(os.path.join(current_dir, '../data/vehicles1.pkl'))
