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

        self.K = None
        self.V = None
        self.N = None

        self.t = None

    def create_set_of_vehicles(self):
        self.K = list(range(0, self.maximum_trucks))

    def create_set_of_vertices(self):
        self.V = [self.depot_leave] + list(self.locations['LOCATION_NAME'].unique()) + [self.depot_enter]

    def create_set_of_nodes(self):
        self.N = list(self.locations['LOCATION_NAME'].unique())

    def create_transit_minutes(self):
        self.t = {}
        for row in self.transportation_matrix.itertuples():
            if (row.FROM_LOCATION_NAME in self.V) & (row.TO_LOCATION_NAME in self.V):
                self.t[row.FROM_LOCATION_NAME, row.TO_LOCATION_NAME] = row.DRIVE_MINUTES



