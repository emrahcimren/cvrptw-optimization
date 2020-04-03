'''
Input data sets
CVRPTW formulation
'''
import pulp

time_variables_dict = model_inputs.time_variables_dict
assignment_variables_dict = model_inputs.assignment_variables_dict
vertices_dict = model_inputs.vertices_dict
vehicles_dict = model_inputs.vehicles_dict
customers_dict = model_inputs.customers_dict

model = pulp.LpProblem("CVRPTW", pulp.LpMinimize)
time_var = pulp.LpVariable.dicts("Time", time_variables_dict.keys(), 0, None, pulp.LpContinuous)
assignment_var = pulp.LpVariable.dicts("Assign", assignment_variables_dict.keys(), 0, 1, pulp.LpBinary)  #Binary

# vehicle Capacity
for vehicle in vehicles_dict['CAPACITY'].keys():
    model += pulp.lpSum([float(LocationData[point][0]) * DecisionVar[point][node][vehicle] for point in Points
                       for node in Nodes if point!=node]) <= float(CapacityOfVehicle), "Capacity"+str(vehicle)

# Time Windows
for vertex, vehicle in time_variables_dict.keys():
    time_var[vertex, vehicle].bounds(float(vertices_dict['TIME_WINDOW_START'][vertex]), float(vertices_dict['TIME_WINDOW_END'][vertex]))



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
