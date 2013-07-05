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

import datetime
import os

from b07.log import info

class Gear(object):
    gear = {'bt':0, 'rt':0, 'pt':0, 'et':0, 'st':0, 'ft':0, 'ht':0, 'lt':0, 'mt':0, 'tt':0, 'ct':0, 'keyt':0, "t":0}
    gear_types = {"EMP_BURSTER": 'b',
             "EMITTER_A": 'r',
             "POWER_CUBE": 'p',
             "MEDIA": 'e',
             "RES_SHIELD": 's',
             "FORCE_AMP": 'f',
             "HEATSINK": 'h',
             "LINK_AMPLIFIER": 'l',
             "MULTIHACK": 'm',
             "TURRET": 't',
             "FLIP_CARD": 'c',
             "PORTAL_LINK_KEY": "key"}
    levels = [1, 2, 3, 4, 5, 6, 7, 8]
    rarities = ["COMMON","RARE","VERY_RARE"]
    flips = ["ADA","JARVIS"]
    
    for level_entity in ['b','r','p','e']:
        for level in levels:
            key = level_entity+str(level)
            gear[key] = 0
    for mod in ['s','f','h','l','m','t']:
        for rarity in rarities:
            key = mod+rarity
            gear[key] = 0
    for flip in flips:
        key = "c"+flip
        gear[key] = 0
    
    @classmethod
    def catalogGear(klass, js):
        print js
        
        curkey = None
        resource_type = None
        typ = None
        if "flipCardType" in js.keys():
            typ = klass.gear_types["FLIP_CARD"]
            curkey = "%s%s" % (typ, js['flipCardType'])
        else:
            resource_type = js['resourceType']
            typ = klass.gear_types[resource_type]
            if "level" in js.keys():
                curkey = "%s%d" % (typ, js['level'])
            elif "rarity" in js.keys():
                curkey = "%s%s" % (typ, js['rarity'])
        klass.gear['t'] += 1
        klass.gear[typ+'t'] += 1
        if curkey is not None:
            klass.gear[curkey] += 1

def loggear():
    items = Gear.gear
    
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("|     Item      |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  Total  |")
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("| Bursters      | %(b1)3d | %(b2)3d | %(b3)3d | %(b4)3d | %(b5)3d | %(b6)3d | %(b7)3d | %(b8)3d |   %(bt)4d  |" % items)
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("| Resonators    | %(r1)3d | %(r2)3d | %(r3)3d | %(r4)3d | %(r5)3d | %(r6)3d | %(r7)3d | %(r8)3d |   %(rt)4d  |" % items)
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("| Power Cubes   | %(p1)3d | %(p2)3d | %(p3)3d | %(p4)3d | %(p5)3d | %(p6)3d | %(p7)3d | %(p8)3d |   %(pt)4d  |" % items)
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("| Media         | %(e1)3d | %(e2)3d | %(e3)3d | %(e4)3d | %(e5)3d | %(e6)3d | %(e7)3d | %(e8)3d |   %(et)4d  |" % items)
    info("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|")
    info("|      Mod            | Common    | Rare      | Very Rare       |  Total  |")
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Shields             |   %(sCOMMON)3d     |    %(sRARE)3d    |       %(sVERY_RARE)3d       |  %(st)4d   |" % items)
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Force Amplifiers    |   %(fCOMMON)3d     |    %(fRARE)3d    |       %(fVERY_RARE)3d       |  %(ft)4d   |" % items)
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Heatsinks           |   %(hCOMMON)3d     |    %(hRARE)3d    |       %(hVERY_RARE)3d       |  %(ht)4d   |" % items)
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Link Amplifiers     |   %(lCOMMON)3d     |    %(lRARE)3d    |       %(lVERY_RARE)3d       |  %(lt)4d   |" % items)
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Multihacks          |   %(mCOMMON)3d     |    %(mRARE)3d    |       %(mVERY_RARE)3d       |  %(mt)4d   |" % items)
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Turrets             |   %(tCOMMON)3d     |    %(tRARE)3d    |       %(tVERY_RARE)3d       |  %(tt)4d   |" % items)
    info("|---------------------+-----------+-----------+-----------------+---------|")
    info("| Viruses             |         ADA - %(cADA)3d, JARVIS - %(cJARVIS)3d         |  %(ct)4d   |" % items)
    info("|---------------------+-----------------------------------------+---------|")
    info("| TOTAL NUMBER OF ITEMS (Inventory cap is 2000 items) Keys: %(keyt)3d |  %(t)4d   |" % items)
    info("|---------------------------------------------------------------+---------|")
    
def writeGear(alias):
    items = Gear.gear
    g = open(os.path.expanduser("~/"+alias+"_gear.txt"),"w")
    
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    g.write("|     Item      |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  Total  |\n")
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    g.write("| Bursters      | %(b1)3d | %(b2)3d | %(b3)3d | %(b4)3d | %(b5)3d | %(b6)3d | %(b7)3d | %(b8)3d |   %(bt)4d  |\n" % items)
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    g.write("| Resonators    | %(r1)3d | %(r2)3d | %(r3)3d | %(r4)3d | %(r5)3d | %(r6)3d | %(r7)3d | %(r8)3d |   %(rt)4d  |\n" % items)
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    g.write("| Power Cubes   | %(p1)3d | %(p2)3d | %(p3)3d | %(p4)3d | %(p5)3d | %(p6)3d | %(p7)3d | %(p8)3d |   %(pt)4d  |\n" % items)
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    g.write("| Media         | %(e1)3d | %(e2)3d | %(e3)3d | %(e4)3d | %(e5)3d | %(e6)3d | %(e7)3d | %(e8)3d |   %(et)4d  |\n" % items)
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    g.write("|      Mod            | Common    | Rare      | Very Rare       |  Total  |\n")
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    g.write("| Shields             |   %(sCOMMON)3d     |    %(sRARE)3d    |       %(sVERY_RARE)3d       |  %(st)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    g.write("| Force Amplifiers    |   %(fCOMMON)3d     |    %(fRARE)3d    |       %(fVERY_RARE)3d       |  %(ft)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    g.write("| Heatsinks           |   %(hCOMMON)3d     |    %(hRARE)3d    |       %(hVERY_RARE)3d       |  %(ht)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    g.write("| Link Amplifiers     |   %(lCOMMON)3d     |    %(lRARE)3d    |       %(lVERY_RARE)3d       |  %(lt)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    g.write("| Multihacks          |   %(mCOMMON)3d     |    %(mRARE)3d    |       %(mVERY_RARE)3d       |  %(mt)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    g.write("| Turrets             |   %(tCOMMON)3d     |    %(tRARE)3d    |       %(tVERY_RARE)3d       |  %(tt)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    g.write("| Viruses             |         ADA - %(cADA)3d, JARVIS - %(cJARVIS)3d         |  %(ct)4d   |\n" % items)
    g.write("|---------------------+-----------------------------------------+---------|\n")
    g.write("| TOTAL NUMBER OF ITEMS (Inventory cap is 2000 items) Keys: %(keyt)3d |  %(t)4d   |\n" % items)
    g.write("|---------------------------------------------------------------+---------|\n")
    g.close()
    
