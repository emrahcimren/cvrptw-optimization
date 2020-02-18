'''
CVRPTW formulation by Desrochers et al 1988
    Desrochers, M., Lenstra, J.K., Savelsbergh, M.W.P., Soumis, F. (1988).
    Vehicle routing with time windows: Optimization and approximation.
    In: Golden, B.L., Assad, A.A. (Eds.), Vehicle Routing: Methods and Studies. North-Holland, Amsterdam, pp. 65–84.
'''

import pandas as pd
from gurobipy import *


class Formulation:

    def __init__(self, K, V, N, t, q, s, locations, depot,
                 outgoing_arcs, incoming_arcs, depot_leave, depot_enter,
                 a, b, M, Q, c, solver_time_limit_mins, mip_gap):

        self.solver = None
        self.infinity = None

        self.K = K
        self.V = V
        self.N = N
        self.t = t
        self.q = q
        self.s = s
        self.Q = Q
        self.c = c
        self.incoming_arcs = incoming_arcs
        self.outgoing_arcs = outgoing_arcs
        self.depot_leave = depot_leave
        self.depot_enter = depot_enter
        self.a = a
        self.b = b
        self.M = M

        self.mip_gap = mip_gap
        self.depot_lat = depot['LATITUDE'].iloc[0]
        self.depot_lon = depot['LONGITUDE'].iloc[0]
        self.locations = locations
        self.depot = depot
        self.solver_time_limit_mins = solver_time_limit_mins

        self.x = None
        self.w = None
        self.z = None
        self.y = None
        self.v = None

        self.x_set = None
        self.w_set = None

        self.objective = None

        self.x_solution = None
        self.y_solution = None
        self.z_solution = None
        self.w_solution = None

        self.solution = None

        self.visit_orders = None
        self.service_start_time = None

        self.final_model_solution = None

    def initiate_solver(self):
        '''
        Function to initiate solver
        :return:
        '''
        self.solver = Model('Desrochers et al 1988')

    def create_model_formulation(self):
        '''
        Function to create model formulation
        :return:
        '''
        self._create_allocation_variable()
        self._create_service_start_time_variable()
        self._create_helper_and_team_variables()
        self._fix_team()
        self._create_total_time_variable()
        self._create_customer_visit_constraint()
        self._create_vehicle_depot_leave_constraint()
        self._create_flow_in_flow_out_constraint()
        self._create_vehicle_depot_arriving_constraint()
        self._create_time_variable_constraint()
        self._create_time_windows_constraint()
        self._create_vehicle_capacity_constraint()
        self._create_maximum_travel_time_constraint()
        self.create_helper_team_relationship()

    def _create_allocation_variable(self):
        '''
        Allocation variable; x_ijk = 1 if location j is visited after location i by vehicle k; 0 otherwise
        :return:
        '''

        self.x_set = {}
        for i, j in self.t.keys():
            for k in self.K:
                self.x_set[i, j, k] = 0

        self.x = self.solver.addVars(
            self.x_set.keys(),
            vtype=GRB.BINARY,
            name="allocation",
        )

    def _create_service_start_time_variable(self):
        '''
        Service start variable; w_ik = time when location i is started by vehicle k
        :return:
        '''

        self.w_set = {}
        for i in self.V:
            for k in self.K:
                self.w_set[i, k] = 0

        self.w = self.solver.addVars(self.w_set.keys(), name="time")

    def _create_helper_and_team_variables(self):
        self.z = self.solver.addVars(
            self.K,
            vtype=GRB.BINARY,
            name="teams",
        )  # teams
        self.y = self.solver.addVars(
            self.K,
            vtype=GRB.BINARY,
            name="helpers",
        )  # helpers

    def _fix_team(self):
        for k in self.K:
            if self.Q[k].TEAM is not None:
                if self.Q[k].TEAM == 'assign':
                    self.solver.addConstr(
                        self.z[k]==1
                    )
                elif self.Q[k].TEAM == 'not assign':
                    self.solver.addConstr(
                        self.z[k]==0
                    )

    def _create_total_time_variable(self):
        self.v = self.solver.addVars(self.K, name="total time")

    def _create_customer_visit_constraint(self):
        '''
        Each customer is visited exactly once
        :return:
        '''

        self.solver.addConstrs(
            (quicksum(self.x[i, j, k] for k in self.K for j in self.outgoing_arcs[i]) == 1
             for i in self.N), "Each customer is visited exactly once"
        )

    def _create_vehicle_depot_leave_constraint(self):
        '''
        Each vehicle is visiting one location after leaving depot
        :return:
        '''

        self.solver.addConstrs(
            (
                quicksum(self.x[self.depot_leave, j, k] for j in self.N) == 1
                for k in self.K
            ),
            "Each vehicle is visiting one location after leaving depot"
        )

    def _create_flow_in_flow_out_constraint(self):
        '''
        Flow conservation
        :return:
        '''
        self.solver.addConstrs(
            (
                quicksum(self.x[j, i, k] for j in self.incoming_arcs[i]) - quicksum(self.x[i, j, k] for j in self.outgoing_arcs[i]) == 0
                for i in self.N for k in self.K
             ),
            "Flow conservation"
        )

    def _create_vehicle_depot_arriving_constraint(self):
        '''
        Each vehicle is arriving from one location to depot
        :return:
        '''
        self.solver.addConstrs(
            (
                quicksum(
                    self.x[i, self.depot_enter, k] for i in self.N
                ) == 1
                for k in self.K
            ),
            "Each vehicle is arriving from one location to depot"
        )

    def _create_time_variable_constraint(self):
        '''
        Time variable constraint
        :return:
        '''

        self.solver.addConstrs(
            (
                self.w[j, k] - self.w[i, k] -
                self.s[i].STOP_TIME_W_HELPER * self.z[k] -
                self.s[i].STOP_TIME_WH_HELPER * (1 - self.z[k]) -
                self.t[i, j] +
                self.M[i, j] - self.M[i, j] * self.x[i, j, k] >= 0
                for i, j in self.t.keys() for k in self.K
            ),
            "Time variable constraint"
        )

    def _create_time_windows_constraint(self):
        '''
        Time windows
        :return:
        '''
        self.solver.addConstrs(
            (
                self.w[i, k] >= self.a[i]
                for i in self.V for k in self.K
            ),
            "Early Time windows"
        )

        self.solver.addConstrs(
            (
                self.w[i, k] <= self.b[i]
                for i in self.V for k in self.K
            ),
            "Late Time windows"
        )

    def _create_vehicle_capacity_constraint(self):
        '''
        Total volume in the vehicle can not exceed the total capacity
        :return:
        '''
        self.solver.addConstrs(
            (
                quicksum(self.q[i]*self.x[i, j, k] for i in self.N for j in self.outgoing_arcs[i]) <= self.Q[k].CAPACITY
                for k in self.K
            ),
            "Total volume in the vehicle can not exceed the total capacity"
        )

    def _create_maximum_travel_time_constraint(self):
        '''
        Total travel time can not exceed total travel time
        :return:
        '''
        self.solver.addConstrs(
            (
                self.w[self.depot_enter, k] - self.w[self.depot_leave, k] <=
                self.z[k] * self.Q[k].MAXIMUM_TEAM_TRAVEL_HOURS * 60 + (1 - self.z[k]) * self.Q[
                    k].MAXIMUM_SOLO_TRAVEL_HOURS * 60
                for k in self.K
            ),
            "Total travel time can not exceed total travel time"
        )

    def create_helper_team_relationship(self):
        '''
        If team=1, then helper=1
        If team=0, then helper can be 0 or 1
        :return:
        '''
        self.solver.addConstrs(
            (
                self.z[k] - self.y[k] <= 0
                for k in self.K
            ),
            "Helper team relationship"
        )

    def create_model_objective(self):

        self.objective = LinExpr()

        for k in self.K:
            for i, j in self.t.keys():
                self.objective += (
                        self.c[k].TRANS_COST_PER_MINUTE * self.t[i, j] * self.x[i, j, k] +
                        self.c[k].TEAM_COST_PER_TEAM_PER_ROUTE * self.z[k] +
                        self.c[k].HELPER_COST_PER_HELPER_PER_ROUTE * self.y[k]
                )

        self.solver.setObjective(self.objective)

    def run_model(self):
        '''
        Run model
        :return:
        '''
        self.solver.modelSense = GRB.MINIMIZE
        self.solver.setParam('TimeLimit',  self.solver_time_limit_mins*60)
        self.solver.setParam('MIPGap', self.mip_gap)
        self.solver.optimize()

        print('Number of variables in model = {}'.format(str(self.solver.NumVars)))
        print('Number of constraints in model = {}'.format(str(self.solver.NumConstrs)))

        if self.solver.status == GRB.Status.OPTIMAL:
            print('Solution is found')
            print('Problem solved in {} milliseconds'.format(str(self.solver.Runtime)))
            print('Problem solved in {} iterations'.format(str(self.solver.IterCount)))
            print('Problem objective = {} '.format(str(self.solver.ObjVal)))

        elif self.solver.status == GRB.Status.TIME_LIMIT:
            raise Exception('Time limit is reached')

        else:
            raise Exception('No solution exists')

    def compile_results(self):
        '''
        Get results
        :return:
        '''

        self.x_solution = self.solver.getAttr("x", self.x)

        visit_orders = []
        for i, j in self.t.keys():
            for k in self.K:
                visit_orders.append({'PREVIOUS_LOCATION_NAME': i,
                                     'LOCATION_NAME': j,
                                     'VEHICLE': k,
                                     'VALUE': self.x_solution[i, j, k],
                                     'DRIVE_MINS': self.t[i, j]})

        visit_orders = pd.DataFrame(visit_orders)
        self.visit_orders = visit_orders[visit_orders['VALUE'] == 1]

        self.y_solution = self.solver.getAttr("x", self.y)
        self.z_solution = self.solver.getAttr("x", self.z)
        self.w_solution = self.solver.getAttr("x", self.w)

        service_start_time = []
        for idx, i in enumerate(self.V):
            for k in self.K:
                if i == self.depot_leave:
                    event = 'LEAVING DEPOT'
                elif i == self.depot_enter:
                    event = 'ENTERING DEPOT'
                else:
                    event = 'SERVICING'

                service_time = self.s[i].STOP_TIME_W_HELPER * self.y_solution[k] + \
                               self.s[i].STOP_TIME_WH_HELPER * (1-self.y_solution[k])

                service_start_time.append({'LOCATION_NAME': i,
                                           'VEHICLE': k,
                                           'EVENT': event,
                                           'HELPER': self.y_solution[k],
                                           'TEAM': self.z_solution[k],
                                           'TIME_WINDOW_START_MINS': self.a[i],
                                           'SERVICE_START_MINUTES': self.w_solution[i, k],
                                           'SERVICE_TIME': service_time,
                                           'SERVICE_END_MINUTES': self.w_solution[i, k] + service_time,
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
