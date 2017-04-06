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

        response = requests.get(url, auth=(self.login, self.password), params=parameters, verify=False)

        response.raise_for_status()

        return response.json()

    def get_disrupted_lines(self, line=None):
        """Get lines that are currently disrupted."""
        gl_disruptions = self._call('rdata/tcl_sytral.tclalertetrafic/all.json')['values']
        disrupted_lines = {}

        now = arrow.now()

        for gl_disruption in gl_disruptions:
            gl_line = gl_disruption['ligne_com'].rstrip('AB').lower() # Remove the trailing A or B at the end of the line name (seems to be the line direction)

            if line and gl_line != line:
                continue

            if 'debut' in gl_disruption:
                start = arrow.get(gl_disruption['debut'])

                if start > now:
                    continue
            else:
                start = now

            if 'fin' in gl_disruption:
                end = arrow.get(gl_disruption['fin'])

                if end <= now:
                    continue

            if gl_line not in disrupted_lines:
                disrupted_lines[gl_line] = {
                    'started_at': start,
                    'reason': gl_disruption['message'] if 'message' in gl_disruption else None
                }

        return disrupted_lines

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
