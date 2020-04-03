'''
Input data sets
CVRPTW formulation
'''
import pulp

model = pulp.LpProblem("CVRPTW", pulp.LpMinimize)
time_var = pulp.LpVariable.dicts("Time", time_variables_dict.keys(), 0, None, pulp.LpContinuous)
assignment_var = pulp.LpVariable.dicts("Assign", assignment_variables_dict.keys(), 0, 1, pulp.LpBinary)  #Binary

# Time Windows
for vertex, vehicle in time_variables_dict.keys():
    print(vertex, vehicle)

    time_var[vertex, vehicle].bounds(float(LocationData[point][1]), float(LocationData[point][2]))



travel_times = []




class ModelFormulation:

    def __init__(self, transportation_matrix, customers, depot, vehicles):

        self.transportation_matrix = transportation_matrix
        self.customers = customers
        self.depot = depot
        self.depot_name = depot['LOCATION_NAME'].iloc[0]
        self.depot_leave = '{}_START'.format(self.depot_name)
        self.depot_enter = '{}_END'.format(self.depot_name)
        self.vehicles = vehicles
