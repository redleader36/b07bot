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
    ghtml = open(os.path.expanduser("~/"+alias+"_gear.html"),"w")
    ghtml.write('<table border="1">\n')
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    ghtml.write("<tr>\n<th>Item</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>Total</th>\n</tr>\n")
    g.write("|     Item      |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  Total  |\n")
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    ghtml.write("<tr>\n<td>Bursters</td><td>%(b1)d</td><td>%(b2)d</td><td>%(b3)d</td><td>%(b4)d</td><td>%(b5)d</td><td>%(b6)d</td><td>%(b7)d</td><td>%(b8)d</td><td>%(bt)d</td>\n</tr>\n" % items)
    g.write("| Bursters      | %(b1)3d | %(b2)3d | %(b3)3d | %(b4)3d | %(b5)3d | %(b6)3d | %(b7)3d | %(b8)3d |   %(bt)4d  |\n" % items)
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    ghtml.write("<tr>\n<td>Resonators</td><td>%(r1)d</td><td>%(r2)d</td><td>%(r3)d</td><td>%(r4)d</td><td>%(r5)d</td><td>%(r6)d</td><td>%(r7)d</td><td>%(r8)d</td><td>%(rt)d</td>\n</tr>\n" % items)
    g.write("| Resonators    | %(r1)3d | %(r2)3d | %(r3)3d | %(r4)3d | %(r5)3d | %(r6)3d | %(r7)3d | %(r8)3d |   %(rt)4d  |\n" % items)
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    ghtml.write("<tr>\n<td>Power Cubes</td><td>%(p1)d</td><td>%(p2)d</td><td>%(p3)d</td><td>%(p4)d</td><td>%(p5)d</td><td>%(p6)d</td><td>%(p7)d</td><td>%(p8)d</td><td>%(pt)d</td>\n</tr>\n" % items)
    g.write("| Power Cubes   | %(p1)3d | %(p2)3d | %(p3)3d | %(p4)3d | %(p5)3d | %(p6)3d | %(p7)3d | %(p8)3d |   %(pt)4d  |\n" % items)
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    ghtml.write("<tr>\n<td>Media</td><td>%(e1)d</td><td>%(e2)d</td><td>%(e3)d</td><td>%(e4)d</td><td>%(e5)d</td><td>%(e6)d</td><td>%(e7)d</td><td>%(e8)d</td><td>%(et)d</td>\n</tr>\n" % items)
    g.write("| Media         | %(e1)3d | %(e2)3d | %(e3)3d | %(e4)3d | %(e5)3d | %(e6)3d | %(e7)3d | %(e8)3d |   %(et)4d  |\n" % items)
    g.write("|---------------+-----+-----+-----+-----+-----+-----+-----+-----+---------|\n")
    ghtml.write('<tr>\n<th colspan="2">Mod</th><th colspan="2">Common</th><th colspan="2">Rare</th><th colspan="3">Very Rare</th><th>Total</th>\n</tr>\n')
    g.write("|      Mod            | Common    | Rare      | Very Rare       |  Total  |\n")
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    ghtml.write('<tr>\n<td colspan="2">Shields</td><td colspan="2">%(sCOMMON)d</td><td colspan="2">%(sRARE)d</td><td colspan="3">%(sVERY_RARE)d</td><td>%(st)d</td>\n</tr>\n' % items)
    g.write("| Shields             |   %(sCOMMON)3d     |    %(sRARE)3d    |       %(sVERY_RARE)3d       |  %(st)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    ghtml.write('<tr>\n<td colspan="2">Force Amplifiers</td><td colspan="2">%(fCOMMON)d</td><td colspan="2">%(fRARE)d</td><td colspan="3">%(fVERY_RARE)d</td><td>%(ft)d</td>\n</tr>\n' % items)
    g.write("| Force Amplifiers    |   %(fCOMMON)3d     |    %(fRARE)3d    |       %(fVERY_RARE)3d       |  %(ft)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    ghtml.write('<tr>\n<td colspan="2">Heatsinks</td><td colspan="2">%(hCOMMON)d</td><td colspan="2">%(hRARE)d</td><td colspan="3">%(hVERY_RARE)d</td><td>%(ht)d</td>\n</tr>\n' % items)
    g.write("| Heatsinks           |   %(hCOMMON)3d     |    %(hRARE)3d    |       %(hVERY_RARE)3d       |  %(ht)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    ghtml.write('<tr>\n<td colspan="2">Link Amplifiers</td><td colspan="2">%(lCOMMON)d</td><td colspan="2">%(lRARE)d</td><td colspan="3">%(lVERY_RARE)d</td><td>%(lt)d</td>\n</tr>\n' % items)
    g.write("| Link Amplifiers     |   %(lCOMMON)3d     |    %(lRARE)3d    |       %(lVERY_RARE)3d       |  %(lt)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    ghtml.write('<tr>\n<td colspan="2">Multihacks</td><td colspan="2">%(mCOMMON)d</td><td colspan="2">%(mRARE)d</td><td colspan="3">%(mVERY_RARE)d</td><td>%(mt)d</td>\n</tr>\n' % items)
    g.write("| Multihacks          |   %(mCOMMON)3d     |    %(mRARE)3d    |       %(mVERY_RARE)3d       |  %(mt)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    ghtml.write('<tr>\n<td colspan="2">Turrets</td><td colspan="2">%(tCOMMON)d</td><td colspan="2">%(tRARE)d</td><td colspan="3">%(tVERY_RARE)d</td><td>%(tt)d</td>\n</tr>\n' % items)
    g.write("| Turrets             |   %(tCOMMON)3d     |    %(tRARE)3d    |       %(tVERY_RARE)3d       |  %(tt)4d   |\n" % items)
    g.write("|---------------------+-----------+-----------+-----------------+---------|\n")
    ghtml.write('<tr>\n<td colspan="2">Viruses</td><td colspan="7">ADA - %(cADA)d, JARVIS - %(cJARVIS)d</td><td>%(ct)d</td>\n</tr>\n' % items)
    g.write("| Viruses             |         ADA - %(cADA)3d, JARVIS - %(cJARVIS)3d         |  %(ct)4d   |\n" % items)
    g.write("|---------------------+-----------------------------------------+---------|\n")
    ghtml.write('<tr>\n<td colspan="9">TOTAL NUMBER OF ITEMS (Inventory cap is 2000 items) Keys: %(keyt)d</td><td>%(t)d</td>\n</tr>\n' % items)
    g.write("| TOTAL NUMBER OF ITEMS (Inventory cap is 2000 items) Keys: %(keyt)3d |  %(t)4d   |\n" % items)
    g.write("|---------------------------------------------------------------+---------|\n")
    ghtml.write("</table>\n")
    g.close()
    ghtml.close()
