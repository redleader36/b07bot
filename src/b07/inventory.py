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

import sys
import inspect

from b07.log import debug, error

import b07.portals
import b07.gear

class Inventory(object):
    def __init__(self):
        self.items = {}
        self.stats = {}
        self.last_query_timestamp = -1

    def process_result(self, result):
        if result.has_key('result'):
            self.last_query_timestamp = result['result']

        if result.has_key('gameBasket'):
            self.process_game_basket(result['gameBasket'])

    def process_game_basket(self, game_basket):
        if 'deletedEntityGuids' in game_basket:
            for guid in game_basket['deletedEntityGuids']:
                try:
                    item = self.items[guid]
                    item.remove()
                except KeyError:
                    pass

        if 'inventory' in game_basket:
            for item in game_basket['inventory']:
                GameEntity.fromjs(self, item)

class GameEntity(object):

    @classmethod
    def fromjs(klass, inventory, js):
        global resource_converters

        guid = js[0]

        if inventory.items.has_key(guid):
            return inventory.items[guid]
        
        resource_type = None
        resource_key = None
        for key in ['resourceWithLevels', 'resource', 'modResource']:
            if js[2].has_key(key):
                resource_type = js[2][key]['resourceType']
                resource_key = key
                break
        
        if resource_type is None:
            error('unable to interpret item: {}'.format(js))
            return

        if not resource_converters.has_key(resource_type):
            error('don\'t know how to convert: {}'.format(js))
            return

        resource_converters[resource_type].fromjs2(inventory, guid, js[2])

    def __init__(self, inventory, guid):
        self.guid = guid
        self.inventory = inventory
        self.inventory.items[guid] = self

    def remove(self):
        del self.inventory.items[self.guid]

class PortalKey(GameEntity):
    resource_type = 'PORTAL_LINK_KEY'
    key_count = 0

    @classmethod
    def fromjs2(klass, inventory, guid, js2):
        entity = b07.gear.Gear.catalogGear(js2['resource'])
        portal = b07.portals.Portal.fromPortalCoupler(js2['portalCoupler'])
        klass(inventory, guid, portal)

    def __init__(self, inventory, guid, portal):
        super(PortalKey, self).__init__(inventory, guid)
        self.portal = portal
        self.portal.keys[guid] = self
        self.key_count += 1

    def remove(self):
        super(PortalKey, self).remove()
        del self.portal.keys[guid]
        self.key_count -= 1

class LevelEntity(GameEntity):
    @classmethod
    def fromjs2(klass, inventory, guid, js2):
        entity = b07.gear.Gear.catalogGear(js2['resourceWithLevels'])
        klass(inventory, guid, js2['resourceWithLevels']['level'])

    def __init__(self, inventory, guid, level):
        super(LevelEntity, self).__init__(inventory, guid)
        self.level = level
        
class PortalMod(GameEntity):
    @classmethod
    def fromjs2(klass, inventory, guid, js2):
        entity = b07.gear.Gear.catalogGear(js2['modResource'])
        klass(inventory, guid, js2['modResource']['rarity'])

    def __init__(self, inventory, guid, rarity):
        super(PortalMod, self).__init__(inventory, guid)
        self.rarity = rarity

class Burster(LevelEntity):
    resource_type = 'EMP_BURSTER'

class Resonator(LevelEntity):
    resource_type = 'EMITTER_A'
        
class PowerCube(LevelEntity):
    resource_type = 'POWER_CUBE'

class Media(LevelEntity):
    resource_type = 'MEDIA'

class Shield(PortalMod):
    resource_type = 'RES_SHIELD'

class ForceAmp(PortalMod):
    resource_type = 'FORCE_AMP'

class HeatSink(PortalMod):
    resource_type = 'HEATSINK'

class LinkAmplifier(PortalMod):
    resource_type = 'LINK_AMPLIFIER'

class MultiHack(PortalMod):
    resource_type = 'MULTIHACK'

class Turret(PortalMod):
    resource_type = 'TURRET'

class FlipCard(GameEntity):
    resource_type = 'FLIP_CARD'

    @classmethod
    def fromjs2(klass, inventory, guid, js2):
        entity = b07.gear.Gear.catalogGear(js2['flipCard'])
        if js2['flipCard']['flipCardType'] == 'ADA':
            Ada(inventory, guid)

        elif js2['flipCard']['flipCardType'] == 'JARVIS':
            Jarvis(inventory, guid)

        else:
            error('Unknown flip card: {}'.format(js2))

    def __init__(self, inventory, guid):
        super(FlipCard, self).__init__(inventory, guid)
        
class Ada(FlipCard):
    def __init__(self, inventory, guid):
        super(Ada, self).__init__(inventory, guid)
    
class Jarvis(FlipCard):
    def __init__(self, inventory, guid):
        super(Jarvis, self).__init__(inventory, guid)

resource_converters = {k[1].resource_type: k[1] for k in inspect.getmembers(sys.modules[__name__]) if (inspect.isclass(k[1]) and
                                                                                                       issubclass(k[1], GameEntity) and
                                                                                                       hasattr(k[1], 'resource_type'))}

