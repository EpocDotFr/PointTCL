import requests


class Client:
    """Wrapper for the Data Grand Lyon API

    See http://data.grandlyon.com/ for more information."""
    endpoint = 'https://download.data.grandlyon.com/ws/rdata/'

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def _call(self, resource, parameters=None):
        url = self.endpoint + resource

        response = requests.get(url, auth=(self.login, self.password), params=parameters)

        response.raise_for_status()

        response_json = response.json()

        # TODO exception (GrandLyonException) when logical API error occurs

        return response_json

    def get_line_disruptions(self, line):
        """Get disruptions happening on a specific TCL line"""
        return self._call('tcl_sytral.tclalertetrafic/all.json', {'field': 'ligne_com', 'value': line})['values']

    def get_all_bus_lines(self):
        """Get all TCL bus lines"""
        return self._call('tcl_sytral.tcllignebus/all.json')['values']

    def get_all_subway_funicular_lines(self):
        """Get all TCL subway and funicular lines"""
        return self._call('tcl_sytral.tcllignemf/all.json')['values']

    def get_all_tram_lines(self):
        """Get all TCL tram lines"""
        return self._call('tcl_sytral.tcllignetram/all.json')['values']

    def get_velov_station_infos(self, name):
        """Get the informations of a specific Velo'v station"""
        return self._call('jcd_jcdecaux.jcdvelov/all.json', {'field': 'name', 'value': name})['values']


class GrandLyonException(Exception):
    pass
