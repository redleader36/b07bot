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
nickname = "test"
api = None

import b07.api
import b07.portals

def logportals(inventory, reactor):
    now = datetime.datetime.now()
    inv_count = 0
    b07.portals.logportals()
    b07.portals.writeKMLFile(api.player_nickname)
    b07.gear.loggear()
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
    global api
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

