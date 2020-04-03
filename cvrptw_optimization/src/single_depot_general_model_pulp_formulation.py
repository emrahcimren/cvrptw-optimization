'''
Input data sets
CVRPTW formulation
'''
from pulp import *
import pandas as pd

time_variables_dict = model_inputs.time_variables_dict
assignment_variables_dict = model_inputs.assignment_variables_dict
vertices_dict = model_inputs.vertices_dict
vehicles_dict = model_inputs.vehicles_dict
customers_dict = model_inputs.customers_dict
transit_dict = model_inputs.transit_dict
transit_starting_customers_dict = model_inputs.transit_starting_customers_dict
depot_name = model_inputs.depot_names[0]
bigm = 100000000

time_var = pulp.LpVariable.dicts("Time", time_variables_dict.keys(), 0, None, pulp.LpContinuous)
assignment_var = pulp.LpVariable.dicts("Assign", assignment_variables_dict.keys(), 0, 1, pulp.LpBinary)  #Binary

model = pulp.LpProblem("CVRPTW", pulp.LpMinimize)

# objective function
print('objective function')
model += pulp.lpSum(transit_dict['TRANSPORTATION_COST'][from_loc, to_loc] * assignment_var[from_loc, to_loc, vehicle] for from_loc, to_loc, vehicle in assignment_variables_dict.keys())

# Each vehicle can only be used at most once
print('Each vehicle can only be used at most once')
for customer in customers_dict['DEMAND'].keys():
    outgoing_arcs = []
    for from_loc, to_loc in transit_dict['DRIVE_MINUTES'].keys():
        if from_loc == customer:
            outgoing_arcs.append(to_loc)

    model += pulp.lpSum([assignment_var[customer, to_loc, vehicle] for to_loc in outgoing_arcs for vehicle in vehicles_dict['CAPACITY'].keys()]) == 1, "customerVisit" + str(
        customer) + 'k'

# Each vehicle should leave from a depot
print('Each vehicle should leave from a depot')
depot_leave = depot_name + '_LEAVE'
for vehicle in vehicles_dict['CAPACITY'].keys():
    model += pulp.lpSum([assignment_var[depot_leave, customer, vehicle]
                         for customer in customers_dict['DEMAND'].keys()]) == 1, "entryDepotConnection" + str(vehicle)

# Flow in Flow Out
print('Flow in Flow out')
for customer in customers_dict['DEMAND'].keys():
    for vehicle in vehicles_dict['CAPACITY'].keys():
        incoming_arcs = []
        outgoing_arcs = []

        for from_loc, to_loc, temp_vehicle in assignment_variables_dict.keys():
            if (to_loc == customer) & (temp_vehicle == vehicle):
                incoming_arcs.append(from_loc)
            if (from_loc == customer) & (temp_vehicle == vehicle):
                outgoing_arcs.append(to_loc)

        model += pulp.lpSum([assignment_var[from_loc, customer, vehicle] for from_loc in incoming_arcs]) - pulp.lpSum([assignment_var[customer, to_loc, vehicle] for to_loc in outgoing_arcs]) == 0, "forTrip" + str(customer) + 'k' + str(vehicle)

# Each vehicle should enter a depot
print('Each vehicle should enter a depot')
depot_enter = depot_name + '_ENTER'
for vehicle in vehicles_dict['CAPACITY'].keys():
    model += pulp.lpSum([assignment_var[customer, depot_enter, vehicle]
                         for customer in customers_dict['DEMAND'].keys()]) == 1, "exitDepotConnection" + str(vehicle)

# vehicle Capacity
print('vehicle Capacity')
for vehicle in vehicles_dict['CAPACITY'].keys():
    model += pulp.lpSum([float(customers_dict['DEMAND'][from_loc]) * assignment_var[from_loc, to_loc, vehicle]
                         for from_loc, to_loc in transit_starting_customers_dict['DRIVE_MINUTES'].keys()]) <= float(vehicles_dict['CAPACITY'][vehicle]), "Capacity"+str(vehicle)

# Time intervals
print('time intervals')
for from_loc, to_loc, vehicle in assignment_variables_dict.keys():
    stop_time = 0
    if from_loc != depot_leave:
        stop_time = customers_dict['STOP_TIME'][from_loc]
    model += time_var[to_loc, vehicle] - time_var[from_loc, vehicle] >= transit_dict['DRIVE_MINUTES'][from_loc, to_loc] + stop_time + bigm*assignment_var[from_loc, to_loc, vehicle] - bigm, "timewindow" + str(vehicle) + 'p' + str(from_loc) + 'p' + str(to_loc)

# Time Windows
print('time windows')
for vertex, vehicle in time_variables_dict.keys():
    time_var[vertex, vehicle].bounds(float(vertices_dict['TIME_WINDOW_START'][vertex]), float(vertices_dict['TIME_WINDOW_END'][vertex]))

print('solving model')
model.solve(PULP_CBC_CMD(msg=1))

if model.status == 1:
    print('problem is feasible')

    # get assignment variable values
    print('getting solution for assignment variables')
    solution_assignment = []
    for from_loc, to_loc, vehicle in assignment_variables_dict.keys():
        if assignment_var[from_loc, to_loc, vehicle].value() > 0:
            solution_assignment.append({'FROM_LOCATION_NAME': from_loc,
                                        'TO_LOCATION_NAME': to_loc,
                                        'VEHICLE': vehicle,
                                        'VALUE': assignment_var[from_loc, to_loc, vehicle].value(),
                                        'DRIVE_MINUTES': transit_dict['DRIVE_MINUTES'][from_loc, to_loc],
                                        'TRANSPORTATION_COST': transit_dict['TRANSPORTATION_COST'][from_loc, to_loc]
                                        })

    solution_assignment = pd.DataFrame(solution_assignment)

    # get time variable values
    print('getting solution for time variables')
    solution_time = []
    for loc, vehicle in time_var.keys():
        if time_var[loc, vehicle].value() > 0:
            demand = 0
            stop_time = 0
            if loc in customers_dict['DEMAND'].keys():
                demand = customers_dict['DEMAND'][loc]
                stop_time = customers_dict['STOP_TIME'][loc]

            solution_time.append({'LOCATION_NAME': loc,
                                  'VEHICLE': vehicle,
                                  'TIME': time_var[loc, vehicle].value(),
                                  'DEMAND': demand,
                                  'STOP_TIME': stop_time,
                                  'TIME_WINDOW_START': vertices_dict['TIME_WINDOW_START'][loc],
                                  'TIME_WINDOW_END': vertices_dict['TIME_WINDOW_END'][loc],
                                  'VEHICLE_CAPACITY': vehicles_dict['CAPACITY'][vehicle]
                                  })

    solution_time = pd.DataFrame(solution_time)

    print('Creating Paths')
    vehicles_list = solution_assignment['VEHICLE'].unique()
    solution_path = []
    for vehicle in vehicles_list:
        route = solution_assignment[solution_assignment['VEHICLE']==vehicle]
        path = list(set(route['FROM_LOCATION_NAME'].to_list() + route['TO_LOCATION_NAME'].to_list()))
        times = solution_time[solution_time['VEHICLE']==vehicle]
        times = times[times['LOCATION_NAME'].isin(path)]
        times.sort_values(['TIME'], inplace=True)
        times['STOP_NUMBER'] = range(0, len(times))
        times['PREVIOUS_LOCATION_NAME'] = times['LOCATION_NAME'].shift(1)
        route.rename(columns={'FROM_LOCATION_NAME': 'PREVIOUS_LOCATION_NAME', 'TO_LOCATION_NAME': 'LOCATION_NAME'}, inplace=True)
        times = times.merge(route, how='left', on=['PREVIOUS_LOCATION_NAME', 'LOCATION_NAME', 'VEHICLE'])
        times['ORIGINAL_LOCATION_NAME'] = times['LOCATION_NAME']
        times['ORIGINAL_LOCATION_NAME'] = times['ORIGINAL_LOCATION_NAME'].str.replace('_ENTER', '')
        times['ORIGINAL_LOCATION_NAME'] = times['ORIGINAL_LOCATION_NAME'].str.replace('_LEAVE', '')
        times.drop(['VALUE'], 1, inplace=True)
        solution_path.append(times)
    solution_path = pd.concat(solution_path)





class ModelFormulation:

    def __init__(self, transportation_matrix, customers, depot, vehicles):

        self.transportation_matrix = transportation_matrix
        self.customers = customers
        self.depot = depot
        self.depot_name = depot['LOCATION_NAME'].iloc[0]
        self.depot_leave = '{}_START'.format(self.depot_name)
        self.depot_enter = '{}_END'.format(self.depot_name)
        self.vehicles = vehicles
