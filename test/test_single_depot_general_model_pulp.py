'''
Test class for testing general model
'''

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'cvrptw_optimization')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'cvrptw_optimization/src')))
from cvrptw_optimization.src import data as dat

depots = dat.depots0
customers = dat.customers0
transportation_matrix = dat.transportation_matrix0
vehicles = dat.vehicles0.head(3)
