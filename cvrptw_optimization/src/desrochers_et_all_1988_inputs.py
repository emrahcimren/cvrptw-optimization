'''
Input data sets
CVRPTW formulation by Desrochers et al 1988
    Desrochers, M., Lenstra, J.K., Savelsbergh, M.W.P., Soumis, F. (1988).
    Vehicle routing with time windows: Optimization and approximation.
    In: Golden, B.L., Assad, A.A. (Eds.), Vehicle Routing: Methods and Studies. North-Holland, Amsterdam, pp. 65–84.
'''


class ModelInputs:

    def __init__(self, transportation_matrix, locations, depot, maximum_trucks):

        self.transportation_matrix = transportation_matrix
        self.locations = locations
        self.depot = depot
        self.depot_name = depot['LOCATION_NAME'].iloc[0]
        self.depot_leave = '{}_START'.format(self.depot_name)
        self.depot_enter = '{}_END'.format(self.depot_name)
        self.maximum_trucks = maximum_trucks

        self.K = None #set pf vehicles
        self.V = None #set pf vertices
        self.N = None #set of nodes

        self.t = None #transit times
        self.s = None #stop times
        self.q = None #location demand

        self.a = None #time window start
        self.b = None #time window end

        self.M = None #time bounds

        self.incoming_arcs = None #ncoming arcs set
        self.outgoing_arcs = None #outgoing arcs set

        # prepare inputs
        self.create_set_of_vehicles()
        self.create_set_of_vertices()
        self.create_set_of_nodes()
        self.create_transit_minutes()
        self.crate_location_demand()
        self.crate_stop_times()
        self.create_time_windows()
        self.create_depot_time_windows()
        self.create_time_bound()
        self.create_incoming_and_outgoing_arcs()

    def create_set_of_vehicles(self):
        '''
        Model set of vehicles
        :return:
        '''
        self.K = list(range(0, self.maximum_trucks))

    def create_set_of_vertices(self):
        '''
        Model set of vertices: depots + locations
        :return:
        '''
        self.V = [self.depot_leave] + list(self.locations['LOCATION_NAME'].unique()) + [self.depot_enter]

    def create_set_of_nodes(self):
        '''
        Set of nodes: locations
        :return:
        '''
        self.N = list(self.locations['LOCATION_NAME'].unique())

    def create_transit_minutes(self):
        '''
        Transit minutes
        :return:
        '''
        self.t = {}
        for row in self.transportation_matrix.itertuples():
            if (row.FROM_LOCATION_NAME in self.V) & (row.TO_LOCATION_NAME in self.V):
                self.t[row.FROM_LOCATION_NAME, row.TO_LOCATION_NAME] = row.DRIVE_MINUTES

    def crate_stop_times(self):
        '''
        Stop times
        :return:
        '''
        self.s = {}
        for location in self.V:
            if location == self.depot_leave:
                stop_mins = 0
            elif location == self.depot_enter:
                stop_mins = 0
            else:
                stop = self.locations[self.locations['LOCATION_NAME'] == location]
                stop_mins = stop['STOP_TIME'].iloc[0]
            self.s[location] = stop_mins

    def crate_location_demand(self):
        '''
        Location demand
        :return:
        '''
        self.q = {}
        for location in self.N:
            stop = self.locations[self.locations['LOCATION_NAME'] == location]
            self.q[location] = stop['DEMAND'].iloc[0]

    def create_time_windows(self):
        '''
        Time windows
        :return:
        '''
        self.a = {}
        self.b = {}
        for location in self.V:
            if location == self.depot_leave:
                tw_start = 0
                tw_end = 10000000000000
            elif location == self.depot_enter:
                tw_start = 0
                tw_end = 10000000000000
            else:
                stop = self.locations[self.locations['LOCATION_NAME'] == location]
                tw_start = stop['TW_START_MINUTES'].iloc[0]
                tw_end = stop['TW_END_MINUTES'].iloc[0]

            self.a[location] = tw_start
            self.b[location] = tw_end

    def create_depot_time_windows(self):
        '''
        Update depot time windows
        :return:
        '''
        a_s = {}
        a_t = {}
        b_s = {}
        b_t = {}
        for location in self.N:
            a_s[location] = self.a[location] - self.t[self.depot_leave, location]
            b_s[location] = self.b[location] - self.t[self.depot_leave, location]
            a_t[location] = self.a[location] + self.s[location] + self.t[location, self.depot_enter]
            b_t[location] = self.b[location] + self.s[location] + self.t[location, self.depot_enter]

        self.a[self.depot_leave] = min(a_s.values())
        self.b[self.depot_leave] = max(b_s.values())
        self.a[self.depot_enter] = min(a_t.values())
        self.b[self.depot_enter] = max(b_t.values())

    def create_time_bound(self):
        '''
        Time bound
        :return:
        '''
        self.M = {}
        for i, j in self.t.keys():
            self.M[i, j] = max(0, self.b[i] + self.s[i] + self.t[i, j] - self.a[j])

    def create_incoming_and_outgoing_arcs(self):
        '''
        Incoming and outgoing arcs
        :return:
        '''
        self.incoming_arcs = {}
        for j in self.N:

            incoming_arcs_list = []
            for i, to_loc in self.t.keys():
                if to_loc == j:
                    incoming_arcs_list.append(i)
            self.incoming_arcs[j] = incoming_arcs_list

        self.outgoing_arcs = {}
        for i in self.N:
            outgoing_arcs_list = []
            for from_loc, j in self.t.keys():
                if from_loc == i:
                    outgoing_arcs_list.append(j)
            self.outgoing_arcs[i] = outgoing_arcs_list
