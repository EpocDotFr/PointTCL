import requests


class Client:
    """Wrapper for the Grand Lyon Data API

    See http://data.grandlyon.com/ for more information."""
    endpoint = 'https://download.data.grandlyon.com/ws/'

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def _call(self, resource, parameters=None):
        url = self.endpoint + resource

        response = requests.get(url, auth=(self.login, self.password), params=parameters)

        response.raise_for_status()

        return response.json()

    def get_line_disruptions(self, line=None):
        """Get disruptions happening on a specific TCL line"""
        parameters = {}

        if line:
            parameters['field'] = 'ligne_com'
            parameters['value'] = line

        return self._call('rdata/tcl_sytral.tclalertetrafic/all.json', parameters)['values']

    def get_all_bus_lines(self):
        """Get all TCL bus lines"""
        return self._call('rdata/tcl_sytral.tcllignebus/all.json')['values']

    def get_all_subway_funicular_lines(self):
        """Get all TCL subway and funicular lines"""
        return self._call('rdata/tcl_sytral.tcllignemf/all.json')['values']

    def get_all_tram_lines(self):
        """Get all TCL tram lines"""
        return self._call('rdata/tcl_sytral.tcllignetram/all.json')['values']

    def get_velov_station_infos(self, name):
        """Get the informations of a specific Velo'v station"""
        return self._call('rdata/jcd_jcdecaux.jcdvelov/all.json', {'field': 'name', 'value': name})['values']
