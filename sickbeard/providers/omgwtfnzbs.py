# Author: Jordon Smith <smith@jordon.me.uk>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard. If not, see <http://www.gnu.org/licenses/>.

import urllib
import generic
import sickbeard

from sickbeard import tvcache
from sickbeard import helpers
from sickbeard import classes
from sickbeard import logger
from sickbeard.exceptions import ex, AuthException
from sickbeard import show_name_helpers
from datetime import datetime

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree

try:
    import json
except ImportError:
    from lib import simplejson as json


class OmgwtfnzbsProvider(generic.NZBProvider):
    def __init__(self):
        generic.NZBProvider.__init__(self, "omgwtfnzbs")
        self.enabled = False
        self.username = None
        self.api_key = None
        self.cache = OmgwtfnzbsCache(self)
        self.url = 'https://omgwtfnzbs.org/'
        self.supportsBacklog = True

    def isEnabled(self):
        return self.enabled

    def _checkAuth(self):

        if not self.username or not self.api_key:
            raise AuthException("Your authentication credentials for " + self.name + " are missing, check your config.")

        return True

    def _checkAuthFromData(self, parsed_data, is_XML=True):

        if parsed_data is None:
            return self._checkAuth()

        if is_XML:
            # provider doesn't return xml on error
            return True
        else:
            parsedJSON = parsed_data

            if 'notice' in parsedJSON:
                description_text = parsedJSON.get('notice')

                if 'information is incorrect' in parsedJSON.get('notice'):
                    logger.log(u"Incorrect authentication credentials for " + self.name + " : " + str(description_text),
                               logger.DEBUG)
                    raise AuthException(
                        "Your authentication credentials for " + self.name + " are incorrect, check your config.")

                elif '0 results matched your terms' in parsedJSON.get('notice'):
                    return True

                else:
                    logger.log(u"Unknown error given from " + self.name + " : " + str(description_text), logger.DEBUG)
                    return False

            return True

    def _get_season_search_strings(self, ep_obj):
        return [x for x in show_name_helpers.makeSceneSeasonSearchString(self.show, ep_obj)]

    def _get_episode_search_strings(self, ep_obj, add_string=''):
        return [x for x in show_name_helpers.makeSceneSearchString(self.show, ep_obj)]

    def _get_title_and_url(self, item):
        return (item['release'], item['getnzb'])

    def _doSearch(self, search, show=None, retention=0):

        self._checkAuth()

        params = {'user': self.username,
                  'api': self.api_key,
                  'eng': 1,
                  'catid': '19,20',  # SD,HD
                  'retention': sickbeard.USENET_RETENTION,
                  'search': search}

        if retention or not params['retention']:
            params['retention'] = retention

        search_url = 'https://api.omgwtfnzbs.org/json/?' + urllib.urlencode(params)
        logger.log(u"Search url: " + search_url, logger.DEBUG)

        data = self.getURL(search_url, json=True)

        if not data:
            logger.log(u"No data returned from " + search_url, logger.ERROR)
            return []

        if self._checkAuthFromData(data, is_XML=False):

            results = []

            for item in data:
                if 'release' in item and 'getnzb' in item:
                    results.append(item)

            return results

        return []

    def findPropers(self, search_date=None):
        search_terms = ['.PROPER.', '.REPACK.']
        results = []

        for term in search_terms:
            for item in self._doSearch(term, retention=4):
                if 'usenetage' in item:

                    title, url = self._get_title_and_url(item)
                    try:
                        result_date = datetime.fromtimestamp(item['usenetage'])
                    except TypeError:
                        result_date = None

                    if result_date:
                        results.append(classes.Proper(title, url, result_date))

        return results


class OmgwtfnzbsCache(tvcache.TVCache):
    def __init__(self, provider):
        tvcache.TVCache.__init__(self, provider)
        self.minTime = 20

    def _getRSSData(self):
        params = {'user': provider.username,
                  'api': provider.api_key,
                  'eng': 1,
                  'catid': '19,20'}  # SD,HD

        rss_url = 'https://rss.omgwtfnzbs.org/rss-download.php?' + urllib.urlencode(params)

        logger.log(self.provider.name + u" cache update URL: " + rss_url, logger.DEBUG)

        return self.getRSSFeed(rss_url)

    def _checkAuth(self, data):
        return self.provider._checkAuthFromData(data)

provider = OmgwtfnzbsProvider()
