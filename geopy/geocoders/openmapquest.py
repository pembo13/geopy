"""
:class:`.OpenMapQuest` geocoder.
"""

from geopy.compat import urlencode

from geopy.geocoders.base import Geocoder
from geopy.util import logger


class OpenMapQuest(Geocoder): # pylint: disable=W0223
    """
    Geocoder using MapQuest Open Platform Web Services. Documentation at:
        http://developer.mapquest.com/web/products/open/geocoding-service
    """

    def __init__(self, api_key=None, format_string=None, scheme='https', proxies=None):
        """
        Initialize an Open MapQuest geocoder with location-specific
        address information. No API Key is needed by the Nominatim based
        platform.

        :param string format_string: String containing '%s' where
            the string to geocode should be interpolated before querying
            the geocoder. For example: '%s, Mountain View, CA'. The default
            is just '%s'.

        :param string scheme: Use 'https' or 'http' as the API URL's scheme.
            Default is https. Note that SSL connections' certificates are not
            verified.

            .. versionadded:: 0.96.1

        :param dict proxies: If specified, routes this geocoder's requests
            through the specified proxy. E.g., {"https": "192.0.2.0"}. For
            more information, see documentation on
            :class:`urllib2.ProxyHandler`.

            .. versionadded:: 0.96.0
        """
        super(OpenMapQuest, self).__init__(format_string, scheme, proxies)
        self.api_key = api_key or ''
        self.api = "%s://open.mapquestapi.com/nominatim/v1/search" \
                    "?format=json" % self.scheme

    def geocode(self, query, exactly_one=True): # pylint: disable=W0221
        """
        Geocode a location query.

        :param string query: The address or query you wish to geocode.

        :param bool exactly_one: Return one result or a list of results, if
            available.
        """
        super(OpenMapQuest, self).geocode(query)
        params = {
            'q': self.format_string % query
        }
        if exactly_one:
            params['maxResults'] = 1
        url = "&".join((self.api, urlencode(params)))

        logger.debug("%s.geocode: %s", self.__class__.__name__, url)
        return self._parse_json(self._call_geocoder(url), exactly_one)

    @classmethod
    def _parse_json(cls, resources, exactly_one=True):
        """
        Parse display name, latitude, and longitude from an JSON response.
        """
        if not len(resources): # pragma: no cover
            return None
        if exactly_one:
            return cls.parse_resource(resources[0])
        else:
            return [cls.parse_resource(resource) for resource in resources]

    @classmethod
    def parse_resource(cls, resource):
        """
        Return location and coordinates tuple from dict.
        """
        location = resource['display_name']

        latitude = resource['lat'] or None
        longitude = resource['lon'] or None
        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)

        return (location, (latitude, longitude))
