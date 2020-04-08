'''
CVRPTW master and sub formulation in OR Tools
'''
import pandas as pd
from ortools.linear_solver import pywraplp

customers_dict = model_inputs.customers_dict

master_model = pywraplp.Solver('MA_CVRPTW', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
infinity = master_model.infinity()

path_var = {}
for path in paths_dict.keys():
    path_var[path] = master_model.NumVar(0, infinity, 'z[{}]'.format(str(path)))

for customer in customers_dict['DEMAND'].keys():
    master_model.Add(
        master_model.Sum([paths_customers_dict[path, customer] * path_var[path] for path in
         paths_dict.keys()]) == 1
    )

master_model.Minimize(
    master_model.Sum([paths_cost_dict[path] * path_var[path] for path in paths_dict.keys()])
)

master_model.Solve()

activities = master_model.ComputeConstraintActivities()
for i, constraint in enumerate(master_model.constraints()):
    print(('constraint %d: dual value = %f\n'
           '               activity = %f' %
           (i, constraint.dual_value(), activities[constraint.index()])))


print('Successful solve.')
# The problem has an optimal solution.
print(('Problem solved in %f milliseconds' % master_model.wall_time()))
# The objective value of the solution.
print(('Optimal objective value = %f' % master_model.Objective().Value()))
# The value of each variable in the solution.
var_sum = 0
for variable in variable_list:
    print(('%s = %f' % (variable.name(), variable.solution_value())))
    var_sum += variable.solution_value()
print(('Variable sum = %f' % var_sum));

print('Advanced usage:')
print(('Problem solved in %d iterations' % master_model.iterations()))

for variable in variable_list:
    print(('%s: reduced cost = %f' % (variable.name(), variable.reduced_cost())))




solver_parameters = pywraplp.MPSolverParameters()
        solver_parameters.SetDoubleParam(pywraplp.MPSolverParameters.RELATIVE_MIP_GAP, self.mip_gap)
        self.solver.SetTimeLimit(self.solver_time_limit_mins * 60 * 1000)
        self.solver.EnableOutput()
        self.solution = self.

pulp.lpSum()

print('Each customer belongs to one path')

    master_model += pulp.lpSum(
         == 1, "Customer" + str(customer)


master_model = pulp.LpProblem("MA_CVRPTW", pulp.LpMinimize)
path_var = pulp.LpVariable.dicts("Path", paths_dict.keys(), 0, 1, pulp.LpContinuous)
print('Master model objective function')
master_model +=


