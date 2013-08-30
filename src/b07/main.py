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
import shutil

from twisted.internet import reactor

from b07.log import setup
from b07.log import TRACE
from b07.log import trace
from b07.log import INFO
from b07.log import info
from b07.inventory import Ada, Jarvis
from b07.mailer import emailKMLFile
from b07.mailer import emailVersionUpdate

fromFile = False
writeConfig = False
nickname = "test"
email = ""
password = ""
server = {}
database = {}
api = None
gear = None
settings = {"mail":False, "gear":True, "keys":True, "log":False}
file = ""

import b07.api
import b07.portals
#import b07.database

def logStatistics(player,filename):
    db = b07.database.getDatabase(filename)
    player_id = b07.database.getPlayerID(db,player)
    b07.database.updateStats(db,player,b07.gear.Gear.gear,player_id)
    db.close

def logportals(inventory, reactor):
    now = datetime.datetime.now()
    inv_count = 0
    # Print out keys and counts
    filename = file
    if writeConfig:
        filename = "~/.b07_"+api.player_nickname
        createConfigFile(filename)
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
        emailKMLFile(api.player_nickname,api.email,filename)
    if settings["log"]:
        logStatistics(api,filename)
    if api.new_version:
        emailVersionUpdate(api.player_nickname,api.email,filename)
    shutil.copy2(os.path.expanduser("~/{}_config.cfg".format(api.player_nickname)),os.path.expanduser("~/{}_config_old.cfg".format(api.player_nickname)))
    reactor.stop()

def main():
    parseArguments()
    global email, password, server, writeConfig
    config = ConfigParser.ConfigParser()
    if fromFile:
        try:
            config.read(os.path.expanduser(file))
            email = config.get('ingress','email')
            password = config.get('ingress','password')
        except ConfigParser.NoSectionError: #if ~/.b07 doesn't exist
        
            writeConfig = True
            server = {}
            info("Please enter your ingress e-mail address: ")
            email = raw_input()
            info("Please enter your ingress e-mail password: ")
            password = raw_input()
            info("Do you have an email server you want to use? y/n")
            response = raw_input()
            
            if response.lower() == "y" or response.lower() == "yes":
                info("email server hostname: ")
                server["hostname"] = raw_input()
                info("email server port: ")
                server["port"] = str(raw_input())
                info("email server email account: ")
                server["email"] = raw_input()
                info("email server email account password: ")
                server["password"] = raw_input()
                
            else:
                server["hostname"] = "smtp.gmail.com"
                server["port"] = "587"
                server["email"] = email
                server["password"] = password
            info("You will not enter the database information (if you do not use -l, then this is not needed)")
            info("As of right now, the database needs to be a mysql database")
            info("Please enter the database hostname (used for -l): ")
            database["hostname"] = raw_input()
            info("Please enter the database username (used for -l): ")
            database["username"] = raw_input()
            info("Please enter the database name (used for -l): ")
            database["database"] = raw_input()
            info("Please enter the database password (used for -l): ")
            database["password"] = raw_input()
            
            createConfigFile(file)
            
            
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
    parser.add_argument("-l", "--log-stats", dest="log", action="store_true", default=False, help="Store AP Statistics into a database")

    args = parser.parse_args()
    global fromFile, file, email, password
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
    settings["log"] = args.log
    info("{}".format(settings))
    email = args.email
    password = args.password
    
def createConfigFile(file_to_write):
    config = ConfigParser.ConfigParser()
    config.add_section("ingress")
    config.set("ingress","email",email)
    config.set("ingress","password",password)
    config.add_section("emailserver")
    config.set("emailserver","hostname",server["hostname"])
    config.set("emailserver","port",server["port"])
    config.set("emailserver","email",server["email"])
    config.set("emailserver","password",server["password"])
    config.add_section("statisticsdb")
    config.set("statisticsdb","hostname",database["hostname"])
    config.set("statisticsdb","username",database["username"])
    config.set("statisticsdb","password",database["password"])
    config.set("statisticsdb","database",database["database"])
    with open(os.path.expanduser(file_to_write), 'wb') as configfile:
        config.write(configfile)
    

if __name__ == '__main__':
    main()

