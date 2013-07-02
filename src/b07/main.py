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

from twisted.internet import reactor

from b07.log import setup
from b07.log import INFO

setup(reactor, INFO)

import b07.api
import b07.portals

def logportals(inventory, reactor):
    b07.portals.logportals()
    reactor.stop()

def main():
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.b07'))
    api = b07.api.API(reactor,
                      config.get('ingress', 'email'),
                      config.get('ingress', 'password'))
    api.onInventoryRefreshed(logportals, reactor)

    reactor.run()

if __name__ == '__main__':
    main()
