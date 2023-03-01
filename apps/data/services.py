import json
from urllib.parse import quote_plus

import requests
from utils.logger import ilogger


class GeoProvider:
    pass


class OSMProvider(GeoProvider):

    URL = "https://nominatim.openstreetmap.org/search/{address}?format=json&addressdetails=1&limit=1&polygon_svg=1"

    def get_coords(self, address: str) -> tuple:
        """
        lat, long
        """
        coords = (None, None)

        ilogger.info(f'COORDS REQUEST: {address}')

        url = self.URL.format(address=quote_plus(address))

        ilogger.info(url)

        try:
            response = requests.get(url, timeout=2)
        except requests.exceptions.Timeout as e:
            ilogger.exception(e)
            return None, None

        ilogger.info(f'RESPONSE : {response.json()}')

        if response.json():
            try:
                coords = response.json()[0]['lat'], response.json()[0]['lon']
            except Exception as e:
                ilogger.exception(e)
            else:
                ilogger.info(f'COORDS RESULT : {coords}')

        return coords
