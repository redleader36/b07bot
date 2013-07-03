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

import os
import ConfigParser
import argparse
import datetime

from twisted.internet import reactor

from b07.log import setup
from b07.log import TRACE
from b07.log import INFO
from b07.log import info
from b07.inventory import Ada, Jarvis

fromFile = False
# it's very important to set up logging very early in the life of an
# application...

import b07.api
import b07.portals

def logportals(inventory, reactor):
    now = datetime.datetime.now()
    inv_count = 0
    b07.portals.logportals()
    bursters = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0}
    resonators = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0}
    pubes = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0}
    media = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0}
    shields = {"COMMON":0,"RARE":0,"VERY_RARE":0}
    force_amps = {"COMMON":0,"RARE":0,"VERY_RARE":0}
    heatsinks = {"COMMON":0,"RARE":0,"VERY_RARE":0}
    link_amps = {"COMMON":0,"RARE":0,"VERY_RARE":0}
    multihacks = {"COMMON":0,"RARE":0,"VERY_RARE":0}
    turrets = {"COMMON":0,"RARE":0,"VERY_RARE":0}
    flip_cards = {"ADA":0,"JARVIS":0}
    # print inventory.items
    for item in inventory.items.keys():
        inv_count += 1
        if inventory.items[item].resource_type == "EMP_BURSTER":
            bursters[inventory.items[item].level]+=1
        elif inventory.items[item].resource_type == "EMITTER_A":
            resonators[inventory.items[item].level]+=1
        elif inventory.items[item].resource_type == "POWER_CUBE":
            pubes[inventory.items[item].level]+=1
        elif inventory.items[item].resource_type == "MEDIA":
            media[inventory.items[item].level]+=1
        elif inventory.items[item].resource_type == "RES_SHIELD":
            shields[inventory.items[item].rarity]+=1
        elif inventory.items[item].resource_type == "FORCE_AMP":
            force_amps[inventory.items[item].rarity]+=1
        elif inventory.items[item].resource_type == "HEATSINK":
            heatsinks[inventory.items[item].rarity]+=1
        elif inventory.items[item].resource_type == "LINK_AMPLIFIER":
            link_amps[inventory.items[item].rarity]+=1
        elif inventory.items[item].resource_type == "MULTIHACK":
            multihacks[inventory.items[item].rarity]+=1
        elif inventory.items[item].resource_type == "TURRET":
            turrets[inventory.items[item].rarity]+=1
        elif inventory.items[item].resource_type == "FLIP_CARD":
            if type(inventory.items[item]) == Ada:
                flip_cards["ADA"]+=1
            else:
                flip_cards["JARVIS"]+=1
    info("Bursters".format(now))
    for item_level in sorted(bursters.keys()):
        info("Level "+str(item_level)+": "+str(bursters[item_level]).format(now))
    info("Resonators".format(now))
    for item_level in sorted(resonators.keys()):
        info("Level "+str(item_level)+": "+str(resonators[item_level]).format(now))
    info("Pubes".format(now))
    for item_level in sorted(pubes.keys()):
        info("Level "+str(item_level)+": "+str(pubes[item_level]).format(now))
    info("Media".format(now))
    for item_level in sorted(media.keys()):
        info("Level "+str(item_level)+": "+str(media[item_level]).format(now))
    info("Shields".format(now))
    for item_level in sorted(shields.keys()):
        info(str(item_level)+": "+str(shields[item_level]).format(now))
    info("Force Amplifiers".format(now))
    for item_level in sorted(force_amps.keys()):
        info(str(item_level)+": "+str(force_amps[item_level]).format(now))
    info("Heatsinks".format(now))
    for item_level in sorted(heatsinks.keys()):
        info(str(item_level)+": "+str(heatsinks[item_level]).format(now))
    info("Link Amplifiers".format(now))
    for item_level in sorted(link_amps.keys()):
        info(str(item_level)+": "+str(link_amps[item_level]).format(now))
    info("Multihacks".format(now))
    for item_level in sorted(multihacks.keys()):
        info(str(item_level)+": "+str(multihacks[item_level]).format(now))
    info("Turrets".format(now))
    for item_level in sorted(turrets.keys()):
        info(str(item_level)+": "+str(turrets[item_level]).format(now))
    info("Viruses".format(now))
    for item_level in sorted(flip_cards.keys()):
        info(str(item_level)+": "+str(flip_cards[item_level]).format(now))
    info("Total Items: "+str(inv_count).format(now))

    # all of the above code will hopefully just have a function call for it
    #b07.gear.loggear()
    reactor.stop()

def main():
    (email, password) = parseArguments()
    if fromFile:
        config = ConfigParser.ConfigParser()
        config.read(os.path.expanduser('~/.b07'))
        email = config.get('ingress','email')
        password = config.get('ingress','password')

    now = datetime.datetime.now()

    # This is a check for checking which email is being used
    info('email: '+ email.format(now))

    # Password is a debug message in the end, just to ensure proper authentication
    #info('password: '+password.format(now))

    api = b07.api.API(reactor,
                      email,
                      password)
    api.onInventoryRefreshed(logportals, reactor)

    reactor.run()

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email-address", dest="email", action="store", help="email address")
    parser.add_argument("-p", "--password", dest="password", action="store", help="password")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", default=False)
    parser.add_argument("-f", "--from-file", dest="config", action="store_true", default=False)

    args = parser.parse_args()

    global fromFile
    if args.email is None or args.password is None:
        args.config = True

    fromFile = args.config

    # it's very important to set up logging very early in the life of an
    # application...

    if args.debug:
        setup(reactor, TRACE)
    else:
        setup(reactor, INFO)
    
    return(args.email, args.password)

if __name__ == '__main__':
    main()

