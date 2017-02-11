import requests
import arrow


__all__ = [
    'Client'
]


class Client:
    """Wrapper for the Grand Lyon Data API.

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

    def get_line_disruptions(self, line):
        """Get disruptions happening on a specific TCL line."""
        gl_disruptions = self._call('rdata/tcl_sytral.tclalertetrafic/all.json')['values']
        disruptions = []

        for gl_disruption in gl_disruptions:
            gl_line = gl_disruption['ligne_com'].rstrip('AB').lower() # Remove the trailing A or B at the end of the line name (seems to be the line direction)

            if gl_line == line and gl_disruption['message'] not in disruptions:
                disrupted_since = arrow.get(gl_disruption['debut'])

                disruptions.append(gl_disruption['message'])

        return disruptions

    def get_all_bus_lines(self):
        """Get all TCL bus lines."""
        return self._call('rdata/tcl_sytral.tcllignebus/all.json')['values']

    def get_all_subway_funicular_lines(self):
        """Get all TCL subway and funicular lines."""
        return self._call('rdata/tcl_sytral.tcllignemf/all.json')['values']

    def get_all_tram_lines(self):
        """Get all TCL tram lines."""
        return self._call('rdata/tcl_sytral.tcllignetram/all.json')['values']

    def get_velov_station_infos(self, name):
        """Get the informations of a specific Velo'v station."""
        return self._call('rdata/jcd_jcdecaux.jcdvelov/all.json', {'field': 'name', 'value': name})['values']
