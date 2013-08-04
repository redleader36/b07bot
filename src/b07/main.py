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
nickname = "test"
api = None
settings = {"mail":False, "gear":True, "keys":True}

import b07.api
import b07.portals

def logportals(inventory, reactor):
    now = datetime.datetime.now()
    inv_count = 0
    # Print out keys and counts
    b07.portals.writeKMLFile(api.player_nickname)
    b07.gear.writeGear(api.player_nickname)
    if settings["keys"]:
        b07.portals.logportals()
    # write KML file
    # print out gear
    if settings["gear"]:
        b07.gear.loggear()
    # Email KML file
    if settings["mail"]:
        b07.portals.emailKMLFile(api.player_nickname,api.email)
    reactor.stop()

def main():
    (email, password, file) = parseArguments()
    if fromFile:
        config = ConfigParser.ConfigParser()
        config.read(os.path.expanduser(file))
        email = config.get('ingress','email')
        password = config.get('ingress','password')

    now = datetime.datetime.now()

    # This is a check for checking which email is being used
    info('email: '+ email.format(now))

    # Password is a debug message in the end, just to ensure proper authentication
    #info('password: '+password.format(now))
    global api
    api = b07.api.API(reactor,
                      email,
                      password)

    api.onInventoryRefreshed(logportals, reactor)

    reactor.run()

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email-address", dest="email", action="store", help="e-mail used to log into ingress")
    parser.add_argument("-p", "--password", dest="password", action="store", help="password for your e-mail")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", default=False, help="Debug output")
    parser.add_argument("-f", "--from-file", dest="fromFile", action="store", help="Config postfix for the user you want to do (e.g. WillWheaton is ~/.b07_WillWheaton)")
    parser.add_argument("-m", "--mail", dest="mail", action="store_true", default=False, help="Use -m if you want the system to email you a kml file of your keys")
    parser.add_argument("-g", "--no-gear", dest="gear", action="store_false", default=True, help="Use -g if you don't want the system to output your gear to the screen")
    parser.add_argument("-k", "--no-keys", dest="keys", action="store_false", default=True, help="Use -m if you don't want the system to output your keys to the system")

    args = parser.parse_args()
    global fromFile
    file = "~/.b07"
    if args.email is None or args.password is None:
        fromFile = True
    if fromFile:
        if not args.fromFile is None:
            file = "~/.b07_"+args.fromFile
    # it's very important to set up logging very early in the life of an
    # application...

    if args.debug:
        setup(reactor, TRACE)
    else:
        setup(reactor, INFO)
    
    settings["mail"] = args.mail
    settings["keys"] = args.keys
    settings["gear"] = args.gear
    info("{}".format(settings))
    return(args.email, args.password, file)

if __name__ == '__main__':
    main()

