# -*- mode: python; coding: utf-8 -*-

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

#GPS conversions
#010a4a45,04abff21 -> 17.443988,78.377658
#027bab59,fa8b43d1 -> 41.659783,-91.536543  

import datetime

from b07.log import info

class Portal(object):
    portals = {}

    @classmethod
    def fromPortalCoupler(klass, js):
        guid = js['portalGuid']
        print js
        if guid in klass.portals:
            return klass.portals[guid]
        return klass(guid,
                     js['portalTitle'],
                     js['portalLocation'],
                     js['portalAddress'],
                     js['portalImageUrl'])

    def __init__(self, guid, title, location, address, image_url):
        self.guid = guid
        self.title = title
        self.location = location
        self.address = address
        self.image_url = image_url
        self.keys = {}
        self.portals[guid] = self

def jsonlist():
    keys = Portal.portals.keys()
    keys.sort(lambda a, b: cmp(Portal.portals[a].title, Portal.portals[b].title))

    l = []
    for key in keys:
        portal = Portal.portals[key]
        l.append({'guid': portal.guid,
                  'title': portal.title,
                  'location': portal.location,
                  'address': portal.address,
                  'image_url': portal.image_url,
                  'keys': len(portal.keys)})

    return {'portals': l}

# for debugging purposes, log a list of portals we know about
def logportals():
    key_titles = {}
    keys = Portal.portals.keys()
    keys.sort(lambda a, b: cmp(Portal.portals[a].title, Portal.portals[b].title))
    now = datetime.datetime.now()
    info('---vvvv Portals known as of {} vvvv---'.format(now))
    for key in keys:
	portal = Portal.portals[key]
        try:
            key_titles[portal.title] += 1
        except KeyError:
            key_titles[portal.title] = 1
    for key in keys:
        portal = Portal.portals[key]
        if key_titles[portal.title] > 1:
            info('{} ({}): {}'.format(portal.title.encode('ascii','ignore'), portal.address, len(portal.keys)))
        else:
            info('{}: {}'.format(portal.title.encode('ascii','ignore'), len(portal.keys)))
    info('---^^^^ Portals known as of {} ^^^^---'.format(now))
