'''
CVRPTW formulation by Desrochers et al 1988
    Desrochers, M., Lenstra, J.K., Savelsbergh, M.W.P., Soumis, F. (1988).
    Vehicle routing with time windows: Optimization and approximation.
    In: Golden, B.L., Assad, A.A. (Eds.), Vehicle Routing: Methods and Studies. North-Holland, Amsterdam, pp. 65–84.
'''

import pandas as pd
from ortools.linear_solver import pywraplp


class Formulation:

    def __init__(self, K, V, N, t, q, s, locations, depot,
                 outgoing_arcs, incoming_arcs, depot_leave, depot_enter,
                 a, b, M, Q, solver_time_limit_mins,
                 maximum_travel_hours):

        self.solver = None
        self.infinity = None

        self.K = K
        self.V = V
        self.N = N
        self.t = t
        self.q = q
        self.s = s
        self.Q = Q
        self.incoming_arcs = incoming_arcs
        self.outgoing_arcs = outgoing_arcs
        self.depot_leave = depot_leave
        self.depot_enter = depot_enter
        self.a = a
        self.b = b
        self.M = M

        self.maximum_travel_hours = maximum_travel_hours

        self.solver_time_limit_mins = None
        self.depot_lat = depot['LATITUDE'].iloc[0]
        self.depot_lon = depot['LONGITUDE'].iloc[0]
        self.locations = locations
        self.depot = depot
        self.solver_time_limit_mins = solver_time_limit_mins

        self.x = None
        self.w = None

        self.solution = None

        self.visit_orders = None
        self.service_start_time = None

        self.final_model_solution = None

    def initiate_solver(self):
        '''
        Function to initiate solver
        :return:
        '''
        self.solver = pywraplp.Solver('SolveIntegerProblem', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        self.infinity = self.solver.infinity()

    def create_model_formulation(self):
        '''
        Create model formulation
        :return:
        '''
        self._create_allocation_variable()
        self._create_service_start_time_variable()
        self._create_total_time_variable()
        self._create_customer_visit_constraint()
        self._create_vehicle_depot_leave_constraint()
        self._create_flow_in_flow_out_constraint()
        self._create_vehicle_depot_arriving_constraint()
        self._create_time_variable_constraint()
        self._create_time_windows_constraint()
        self._create_vehicle_capacity_constraint()

        if self.maximum_travel_hours is not None:
            self._create_maximum_travel_time_constraint()

    def _create_allocation_variable(self):
        '''
        Allocation variable; x_ijk = 1 if location j is visited after location i by vehicle k; 0 otherwise
        :return:
        '''
        self.x = {}
        for i, j in self.t.keys():
            for k in self.K:
                self.x[i, j, k] = self.solver.BoolVar('x[{}, {}, {}]'.format(str(i), str(j), str(k)))

    def _create_service_start_time_variable(self):
        '''
        Service start variable; w_ik = time when location i is started by vehicle k
        :return:
        '''
        self.w = {}
        for i in self.V:
            for k in self.K:
                self.w[i, k] = self.solver.NumVar(0, self.infinity, 'w[{}, {}]'.format(str(i), str(k)))

    def _create_total_time_variable(self):
        self.z = {}
        for k in self.K:
            self.z[k] = self.solver.NumVar(0, self.infinity, 'z[{}]'.format(str(k)))

    def _create_customer_visit_constraint(self):
        '''
        Each customer is visited exactly once
        :return:
        '''
        for i in self.N:
            self.solver.Add(self.solver.Sum([self.x[i, j, k] for k in self.K for j in self.outgoing_arcs[i]]) == 1)

    def _create_vehicle_depot_leave_constraint(self):
        '''
        Each vehicle is visiting one location after leaving depot
        :return:
        '''
        for k in self.K:
            self.solver.Add(self.solver.Sum([self.x[self.depot_leave, j, k] for j in self.N]) == 1)

    def _create_flow_in_flow_out_constraint(self):
        '''
        Flow conservation
        :return:
        '''
        for i in self.N:
            for k in self.K:
                self.solver.Add(self.solver.Sum([self.x[j, i, k] for j in self.incoming_arcs[i]]) - self.solver.Sum(
                    [self.x[i, j, k] for j in self.outgoing_arcs[i]]) == 0)

    def _create_vehicle_depot_arriving_constraint(self):
        '''
        Each vehicle is arriving from one location to depot
        :return:
        '''
        for k in self.K:
            self.solver.Add(self.solver.Sum([self.x[i, self.depot_enter, k] for i in self.N]) == 1)

    def _create_time_variable_constraint(self):
        '''
        Time variable constraint
        :return:
        '''
        for i, j in self.t.keys():
            for k in self.K:
                self.solver.Add(
                    self.w[j, k] - self.w[i, k] - self.s[i] - self.t[i, j] +
                    self.M[i, j] - self.M[i, j] * self.x[i, j, k] >= 0)

    def _create_time_windows_constraint(self):
        '''
        Time windows
        :return:
        '''
        for i in self.V:
            for k in self.K:
                self.solver.Add(self.w[i, k] >= self.a[i])
                self.solver.Add(self.w[i, k] <= self.b[i])

    def _create_vehicle_capacity_constraint(self):
        '''
        Total volume in the vehicle can not exceed the total capacity
        :return:
        '''
        for k in self.K:
            self.solver.Add(
                self.solver.Sum([self.q[i]*self.x[i, j, k] for i in self.N for j in self.outgoing_arcs[i]]) <= self.Q[k]
            )

    def _create_maximum_travel_time_constraint(self):
        '''
        Total travel time can not exceed total travel time
        :return:
        '''
        for k in self.K:
            for i in self.N:
                self.solver.Add(
                    self.w[self.depot_enter, k] - self.w[i, k] + self.t[self.depot_leave, i] <= self.z[k]
                )
                self.solver.Add(
                    self.w[self.depot_enter, k] - self.w[i, k] + self.t[self.depot_leave, i] <= self.maximum_travel_hours*60
                )

    def create_model_objective(self):
        # add objective
        self.solver.Minimize(self.solver.Sum(
            [self.t[i, j] * self.x[i, j, k] for k in self.K for i, j in self.t.keys()]))

        #self.solver.Minimize(
        #    self.solver.Sum(
        #        [self.z[k] for k in self.K]
        #    )
        #)

    def run_model(self):
        # solver.Minimize(1)
        solver_parameters = pywraplp.MPSolverParameters()
        solver_parameters.SetDoubleParam(pywraplp.MPSolverParameters.RELATIVE_MIP_GAP, 0.01)
        self.solver.SetTimeLimit(self.solver_time_limit_mins * 60 * 1000)
        self.solver.EnableOutput()
        self.solution = self.solver.Solve()

        # get solution
        if self.solution == pywraplp.Solver.OPTIMAL:
            print('Solution is found')
            print('Problem solved in {} milliseconds'.format(str(self.solver.WallTime())))
            print('Problem solved in {} iterations'.format(str(self.solver.Iterations())))

        else:
            raise Exception('No solution exists')

    def compile_results(self):

        visit_orders = []
        for i, j in self.t.keys():
            for k in self.K:
                visit_orders.append({'PREVIOUS_LOCATION_NAME': i,
                                     'LOCATION_NAME': j,
                                     'VEHICLE': k,
                                     'VALUE': self.x[i, j, k].solution_value(),
                                     'DRIVE_MINS': self.t[i, j]})

        visit_orders = pd.DataFrame(visit_orders)
        self.visit_orders = visit_orders[visit_orders['VALUE'] == 1]

        service_start_time = []
        for idx, i in enumerate(self.V):
            for k in self.K:
                if i == self.depot_leave:
                    event = 'LEAVING DEPOT'
                elif i == self.depot_enter:
                    event = 'ENTERING DEPOT'
                else:
                    event = 'SERVICING'

                service_start_time.append({'LOCATION_NAME': i,
                                           'VEHICLE': k,
                                           'EVENT': event,
                                           'TIME_WINDOW_START_MINS': self.a[i],
                                           'SERVICE_START_MINUTES': self.w[i, k].solution_value(),
                                           'SERVICE_TIME': self.s[i],
                                           'SERVICE_END_MINUTES': self.w[i, k].solution_value() + self.s[i],
                                           'TIME_WINDOW_END_MINUTES': self.b[i]})
        service_start_time = pd.DataFrame(service_start_time)
        self.service_start_time = service_start_time.sort_values(['VEHICLE', 'SERVICE_START_MINUTES'])

        solution = self.service_start_time.merge(self.visit_orders, how='left', on=['LOCATION_NAME', 'VEHICLE'])
        solution = solution.merge(self.locations[['LOCATION_NAME', 'LATITUDE', 'LONGITUDE']], how='left',
                                  on=['LOCATION_NAME'])
        solution = solution.sort_values(['VEHICLE', 'SERVICE_START_MINUTES'])
        filter_depots = solution['LOCATION_NAME'].isin([self.depot_leave, self.depot_enter])
        solution.loc[filter_depots, 'LATITUDE'] = self.depot_lat
        solution.loc[filter_depots, 'LONGITUDE'] = self.depot_lon
        solution['STOP_NUMBER'] = range(0, len(solution))
        self.final_model_solution = solution
