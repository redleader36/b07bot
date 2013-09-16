# - mode: python; coding: utf-8 -*-

# b07 bot - ingress information bot
# Copyright © 2013 b07@tormail.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ConfigParser
import cookielib
import urllib
import json
import datetime
import os

from twisted.web.client import Agent
from twisted.web.client import CookieAgent
from twisted.web.client import ContentDecoderAgent
from twisted.web.client import GzipDecoder
from twisted.web.http_headers import Headers
from twisted.web.client import HTTPConnectionPool
from twisted.internet import defer

from b07.log import trace
from b07.log import debug
from b07.log import info
from b07.log import warning
from b07.log import error
from b07.log import critical
from b07.log import log_failure
from b07.log import CRITICAL
from b07.log import versionCheck

import b07.utils
import b07.inventory
import b07.portals

class API(object):

    class URLS:
        CLIENT_LOGIN = 'https://www.google.com/accounts/ClientLogin'
        SERVICE_LOGIN = 'https://accounts.google.com/ServiceLoginAuth'
        APPENGINE =  'https://appengine.google.com'
        GAME_API = 'https://betaspike.appspot.com'
        INGRESS =  'http://www.ingress.com'

    class PATHS:
        LOGIN = '/_ah/login'
        CONFLOGIN = '/_ah/conflogin'
        class API:
            HANDSHAKE =  '/handshake'
            DROP_ITEM = '/rpc/gameplay/dropItem'
            RECYCLE = '/rpc/gameplay/recycleItem'
            SAY = '/rpc/player/say'
            INVENTORY =  '/rpc/playerUndecorated/getInventory'
            PROFILE = '/rpc/playerUndecorated/getPlayerProfile'
            PLEXTS = '/rpc/playerUndecorated/getPaginatedPlexts'
        class INTEL:
            BASE = '/intel'
            PLEXTS = '/rpc/dashboard.getPaginatedPlextsV2'

    HANDSHAKE_PARAMS = {'nemesisSoftwareVersion' : '2013-09-10T22:08:32Z 904499d6f84a opt',
                        'deviceSoftwareVersion' : '4.1.1'}

    def __init__(self, reactor, email, password):
        self.reactor = reactor
        self.email = email
        self.password = password
        
        # Set up an agent for sending HTTP requests.  Uses cookies
        # (part of the authentication), persistent HTTP connection
        # pool, automatic content decoding (gzip)

        # container to keep track of cookies
        self.cookiejar = cookielib.CookieJar()

        # HTTP persistent connection pool
        self.pool = HTTPConnectionPool(self.reactor, persistent = True)
        # for some reason, using >1 connection per host fails
        self.pool.maxPersistentPerHost = 1

        self.agent = ContentDecoderAgent(CookieAgent(Agent(self.reactor,
                                                           pool = self.pool),
                                                     self.cookiejar),
                                         [('gzip', GzipDecoder)])

        # this is the token that is used to authenticate API requests
        self.xsrf_token = None
        self.auth_token = None
        
        # who we are
        self.player_nickname = None
        self.player_guid = None
        self.team = None
        self.ap = None
        self.level = None
        self.start_date = None
        self.new_version = False

        # for keeping track of item inventory
        self.inventory = b07.inventory.Inventory()

        # for keeping track of API requests that are delayed until
        # authentication has completed
        self._deferred_api_requests = []

        # for keeping track of periodic inventory refreshes
        self._periodic_inventory_refresh_delayedcall = None

        # list of functions to call every time inventory is refreshed
        self._on_inventory_refreshed = []

        # do an immediate profile refresh
        self._first_profile_ready = self._defer_until_authenticated(self._profile0, (), {})

        # do an immediate inventory refresh
        self._first_inventory_ready = self._defer_until_authenticated(self._inventory0, (), {})

        # start the authentication process
        self.reactor.callLater(0, self._authenticate0)

    def refreshInventory(self):
        """Manually start an inventory refresh."""

        return self._defer_until_authenticated(self._inventory0, (), {})

    def refreshProfile(self):
        """Manually start a profile refresh."""

        return self._defer_until_authenticated(self._profile0, (), {})


    def onInventoryRefreshed(self, callback, *args, **kw):
        self._on_inventory_refreshed.append((callback, args, kw))

    def err(self, failure):
        log_failure(failure)
        
    def getInventory(self):
        return self.inventory

    def _defer_until_authenticated(self, func, args, kw):
        kw['finished'] = defer.Deferred()

        if self.xsrf_token is None:
            self._deferred_api_requests.append((func, args, kw))

        else:
            self.reactor.callLater(0, func, *args, **kw)
        
        return kw['finished']

    def _process_deferred_api_requests(self):
        while self._deferred_api_requests:
            func, args, kw = self._deferred_api_requests.pop(0)
            self.reactor.callLater(0, func, *args, **kw)

    def _authenticate0(self):
        auth_params = {'Email': self.email,
                       'Passwd': self.password,
                       'service': 'ah',
                       'source': 'IngressBot',
                       'accountType': 'HOSTED_OR_GOOGLE'}

        body = b07.utils.StringProducer(urllib.urlencode(auth_params))
        trace('_authenticate0 {}'.format(urllib.urlencode(auth_params)))
        d = self.agent.request('POST',
                               self.URLS.CLIENT_LOGIN,
                               Headers({'User-Agent' : ['Nemesis (gzip)'],
                                        'Content-Type': ['application/x-www-form-urlencoded'],
                                        'Accept-Charset': ['utf-8']}),
                               body)
        d.addCallback(self._authenticate1)
        d.addErrback(self.err)

    def _authenticate1(self, response):
        finished = defer.Deferred()
        finished.addCallback(self._authenticate2, response.code)
        lp = b07.utils.LoginProtocol(finished)
        response.deliverBody(lp)

    def _authenticate2(self, result, code):
        if code == 200:
            try:
                self.auth_token = result['Auth']

            except KeyError:
                critical('Authentication failed: Bad Response')

        elif code == 403:
            error = result['Error']
        
            if error == 'BadAuthentication':
                critical('Authentication failed: Username or password wrong')

            elif error == 'NotVerified':
                critical('Authentication failed: Account email address has not been verified')

            elif error == 'TermsNotAgreed':
                critical('Authentication failed: User has not agreed to Googles terms of service')

            elif error == 'CaptchaRequired':
                critical('Authentication failed: CAPTCHA required')

            elif error == 'AccountDeleted':
                critical('Authentication failed: User account has been deleted')

            elif error == 'AccountDisabled':
                critical('Authentication failed: User account has been disabled')

            elif error == 'ServiceDisabled':
                critical('Authentication failed: Service disabled')

            elif error == 'ServiceUnavailable':
                critical('Authentication failed: Service unavailable')

            else:
                critical('Authentication failed: Unknown reason')

        else:
            critical('Authentication failed: Bad response')

        trace('_authenticate2 {}'.format(self.auth_token))
        d = self.agent.request('GET',
                               self.URLS.GAME_API + self.PATHS.LOGIN + '?' + urllib.urlencode({'auth' : self.auth_token}),
                               Headers({'User-Agent' : ['Nemesis (gzip)'],
                                        'Accept-Charset': ['utf-8']}),
                               None)
        d.addCallback(self._authenticate3)
        d.addErrback(self.err)

    def _authenticate3(self, response):
        trace('_authenticate3 {}'.format(response.code))
        for cookie in self.cookiejar:
            trace('_authenticate3 {}'.format(cookie))

        urlParams = {'json' : json.dumps(self.HANDSHAKE_PARAMS)}
        d = self.agent.request('GET',
                               self.URLS.GAME_API + self.PATHS.API.HANDSHAKE + '?' + urllib.urlencode({'json': json.dumps(self.HANDSHAKE_PARAMS)}),
                               Headers({'User-Agent' : ['Nemesis (gzip)'],
                                        'Accept-Charset': ['utf-8'],
                                        'Cache-Control': ['max-age=0']}),
                               None)
        d.addCallback(self._authenticate4)
        d.addErrback(self.err)

    def _authenticate4(self, response):
        trace('_authenticate4 {}'.format(response.code))

        if response.code == 200:
            finished = defer.Deferred()
            finished.addCallback(self._authenticate5)
            finished.addErrback(self.err)
            jp = b07.utils.JsonProtocol(finished)
            response.deliverBody(jp)

        else:
            critical('Got response code {} after attempting handshake!'.format(response.code))

    def _authenticate5(self, result):
        trace('_authenticate5 {}'.format(result))

        result = result['result']

        if 'xsrfToken' not in result:
            critical('Authentication with Ingress severs failed for unknown reason')

        self.xsrf_token = str(result['xsrfToken'])
        self.player_nickname = result['nickname']
        self.player_guid = result['playerEntity'][0]
        self.team = result['playerEntity'][2]['controllingTeam']['team']
        self.ap = result['playerEntity'][2]['playerPersonal']['ap']
        self.level = result['playerEntity'][2]['playerPersonal']['clientLevel']
        start_date = result['storage']['mission_complete_0']
        self.start_date = datetime.datetime.fromtimestamp(int(start_date.split(':delim:')[1])/1000)

        debug('XSRF Token:      {}'.format(self.xsrf_token))
        debug('Player GUID:     {}'.format(self.player_guid))
        info('Player nickname: {}'.format(self.player_nickname))
        info('Faction:         {}'.format(self.team))
        info('AP:              {}'.format(self.ap))
        info('Level:           {}'.format(self.level))
        info('Start Date:      {}'.format(self.start_date))
        debug('Player info:     {}'.format(result))
        
        with open(os.path.expanduser("~/{}_config.cfg".format(self.player_nickname)),"w") as file:
            json.dump(result, file, indent=1)
        self.new_version = versionCheck(result['serverVersion'], self.player_nickname)
        
        self._process_deferred_api_requests()

    def _setup_periodic_inventory_refresh(self, result):
        self._periodic_inventory_refresh_delayedcall = self.reactor.callLater(300, self._periodic_inventory_refresh0)

    def _periodic_inventory_refresh0(self):
        finished = self._defer_until_authenticated(self._inventory0, (), {})
        finished.addCallback(self._periodic_inventory_refresh1)

    def _periodic_inventory_refresh1(self, result):
        self._periodic_inventory_refresh_delayedcall = self.reactor.callLater(300, self._periodic_inventory_refresh0)
    
    def _inventory0(self, finished):
        debug('Requesting inventory from server...')
        body = b07.utils.StringProducer(json.dumps({'params' : {'lastQueryTimestamp': self.inventory.last_query_timestamp}}))
        d = self.agent.request('POST',
                               self.URLS.GAME_API + self.PATHS.API.INVENTORY,
                               Headers({'User-Agent' : ['Nemesis (gzip)'],
                                        'Content-Type': ['application/json;charset=UTF-8'],
                                        'X-XsrfToken': [self.xsrf_token]}),
                               body)
                                    
        d.addCallback(self._inventory1, finished)
        d.addErrback(self.err)

    def _inventory1(self, response, finished):
        if response.code == 500:
            error('Got a 500 SERVER ERROR trying to get the inventory!')

        elif response.code == 200:
            debug('Got 200 OK response to inventory request')
            d = defer.Deferred()
            d.addCallback(self._inventory2, finished)
            jp = b07.utils.JsonProtocol(d)
            response.deliverBody(jp)

        else:
            error('Don\'t know what to do with {} code in response to inventory request!'.format(response.code))

    def _inventory2(self, result, finished):
        self.inventory.process_result(result)
        finished.callback(self.inventory)
        for callback, args, kw in self._on_inventory_refreshed:
            self.reactor.callLater(0, callback, self.inventory, *args, **kw)

    def _profile0(self, finished):
        debug('Requesting profile from server...')
        body = b07.utils.StringProducer(json.dumps({'params' : [self.player_nickname]}))
        d = self.agent.request('POST',
                               self.URLS.GAME_API + self.PATHS.API.PROFILE,
                               Headers({'User-Agent' : ['Nemesis (gzip)'],
                                        'Content-Type': ['application/json;charset=UTF-8'],
                                        'X-XsrfToken': [self.xsrf_token]}),
                               body)

        d.addCallback(self._profile1, finished)
        d.addErrback(self.err)

    def _profile1(self, response, finished):
        if response.code == 500:
            error('Got a 500 SERVER ERROR trying to get the profile!')

        elif response.code == 200:
            debug('Got 200 OK response to profile request')
            d = defer.Deferred()
            d.addCallback(self._profile2, finished)
            jp = b07.utils.JsonProtocol(d)
            response.deliverBody(jp)

        else:
            error('Don\'t know what to do with {} code in response to profile request!'.format(response.code))

    def _profile2(self, result, finished):
        with open(os.path.expanduser("~/{}_profile.json".format(self.player_nickname)),"w") as file:
            json.dump(result, file, indent=1)

