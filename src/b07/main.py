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
    bursters = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, "total":0}
    resonators = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, "total":0}
    pubes = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, "total":0}
    media = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, "total":0}
    shields = {"COMMON":0,"RARE":0,"VERY_RARE":0, "total":0}
    force_amps = {"COMMON":0,"RARE":0,"VERY_RARE":0, "total":0}
    heatsinks = {"COMMON":0,"RARE":0,"VERY_RARE":0, "total":0}
    link_amps = {"COMMON":0,"RARE":0,"VERY_RARE":0, "total":0}
    multihacks = {"COMMON":0,"RARE":0,"VERY_RARE":0, "total":0}
    turrets = {"COMMON":0,"RARE":0,"VERY_RARE":0, "total":0}
    flip_cards = {"ADA":0,"JARVIS":0, "total":0}
    # print inventory.items
    for item in inventory.items.keys():
        inv_count += 1
        if inventory.items[item].resource_type == "EMP_BURSTER":
            bursters[inventory.items[item].level]+=1
            bursters["total"] += 1
        elif inventory.items[item].resource_type == "EMITTER_A":
            resonators[inventory.items[item].level]+=1
            resonators["total"] += 1
        elif inventory.items[item].resource_type == "POWER_CUBE":
            pubes[inventory.items[item].level]+=1
            pubes["total"] += 1
        elif inventory.items[item].resource_type == "MEDIA":
            media[inventory.items[item].level]+=1
            media["total"] += 1
        elif inventory.items[item].resource_type == "RES_SHIELD":
            shields[inventory.items[item].rarity]+=1
            shields["total"] += 1
        elif inventory.items[item].resource_type == "FORCE_AMP":
            force_amps[inventory.items[item].rarity]+=1
            force_amps["total"] += 1
        elif inventory.items[item].resource_type == "HEATSINK":
            heatsinks[inventory.items[item].rarity]+=1
            heatsinks["total"] += 1
        elif inventory.items[item].resource_type == "LINK_AMPLIFIER":
            link_amps[inventory.items[item].rarity]+=1
            link_amps["total"] += 1
        elif inventory.items[item].resource_type == "MULTIHACK":
            multihacks[inventory.items[item].rarity]+=1
            multihacks["total"] += 1
        elif inventory.items[item].resource_type == "TURRET":
            turrets[inventory.items[item].rarity]+=1
            turrets["total"] += 1
        elif inventory.items[item].resource_type == "FLIP_CARD":
            flip_cards["total"] += 1
            if type(inventory.items[item]) == Ada:
                flip_cards["ADA"]+=1
            else:
                flip_cards["JARVIS"]+=1
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("|     Item      |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  Total  |")
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("| Bursters      | %3d | %3d | %3d | %3d | %3d | %3d | %3d | %3d |   %4d  |" % (bursters[1],bursters[2],bursters[3],bursters[4],bursters[5],bursters[6],bursters[7],bursters[8],bursters["total"]))
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("| Resonators    | %3d | %3d | %3d | %3d | %3d | %3d | %3d | %3d |   %4d  |" % (resonators[1],resonators[2],resonators[3],resonators[4],resonators[5],resonators[6],resonators[7],resonators[8],resonators["total"]))
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("| Power Cubes   | %3d | %3d | %3d | %3d | %3d | %3d | %3d | %3d |   %4d  |" % (pubes[1],pubes[2],pubes[3],pubes[4],pubes[5],pubes[6],pubes[7],pubes[8],pubes["total"]))
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("| Media         | %3d | %3d | %3d | %3d | %3d | %3d | %3d | %3d |   %4d  |" % (media[1],media[2],media[3],media[4],media[5],media[6],media[7],media[8],media["total"]))
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("|      Mod            | Common    | Rare      | Very Rare       |  Total  |")
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Shields             |   %3d     |    %3d    |       %3d       |  %4d   |" % (shields["COMMON"], shields["RARE"], shields["VERY_RARE"], shields["total"]))
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Force Amplifiers    |   %3d     |    %3d    |       %3d       |  %4d   |" % (force_amps["COMMON"], force_amps["RARE"], force_amps["VERY_RARE"], force_amps["total"]))
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Heatsinks           |   %3d     |    %3d    |       %3d       |  %4d   |" % (heatsinks["COMMON"], heatsinks["RARE"], heatsinks["VERY_RARE"], heatsinks["total"]))
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Link Amplifiers     |   %3d     |    %3d    |       %3d       |  %4d   |" % (link_amps["COMMON"], link_amps["RARE"], link_amps["VERY_RARE"], link_amps["total"]))
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Multihacks          |   %3d     |    %3d    |       %3d       |  %4d   |" % (multihacks["COMMON"], multihacks["RARE"], multihacks["VERY_RARE"], multihacks["total"]))
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Turrets             |   %3d     |    %3d    |       %3d       |  %4d   |" % (turrets["COMMON"], turrets["RARE"], turrets["VERY_RARE"], turrets["total"]))
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("Viruses")
    for item_level in sorted(flip_cards.keys()):
        info("\t"+str(item_level)+": "+str(flip_cards[item_level]))
    info("Total Items: "+str(inv_count))

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

