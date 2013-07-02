# -*- mode: python; coding: utf-8 -*-

import datetime

from b07.log import info

class Portal(object):
    portals = {}

    @classmethod
    def fromPortalCoupler(klass, js):
        guid = js['portalGuid']
        if guid in klass.portals:
            return klass.portals[guid]
        return klass(guid, js['portalTitle'], js['portalLocation'], js['portalAddress'], js['portalImageUrl'])

    def __init__(self, guid, title, location, address, image_url):
        self.guid = guid
        self.title = title
        self.location = location
        self.address = address
        self.image_url = image_url
        self.keys = {}
        self.portals[guid] = self

def logportals():
    keys = Portal.portals.keys()
    keys.sort(lambda a, b: cmp(Portal.portals[a].title, Portal.portals[b].title))
    now = datetime.datetime.now()
    info('---vvvv Portals known as of {} vvvv---'.format(now))
    for key in keys:
        portal = Portal.portals[key]
        if portal.title == 'US Post Office':
            info('{} ({}): {}'.format(portal.title, portal.address, len(portal.keys)))
        else:
            info('{}: {}'.format(portal.title, len(portal.keys)))
    info('---^^^^ Portals known as of {} ^^^^---'.format(now))
