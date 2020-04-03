import pandas as pd
import os
current_dir, this_filename = os.path.split(__file__)

customers1 = pd.read_pickle(os.path.join(current_dir, '../data/customers1.pkl'))
depots1 = pd.read_pickle(os.path.join(current_dir, '../data/depots1.pkl'))
transportation_matrix1 = pd.read_pickle(os.path.join(current_dir, '../data/transportation_matrix1.pkl'))
vehicles1 = pd.read_pickle(os.path.join(current_dir, '../data/vehicles1.pkl'))
