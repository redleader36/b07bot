import MySQLdb
import ConfigParser
import os
from b07.log import info

def getDatabase(configFile):
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser(configFile))
    hostname = config.get('statisticsdb','hostname')
    database = config.get('statisticsdb','database')
    username = config.get('statisticsdb','username')
    password = config.get('statisticsdb','password')
    try:
        db = MySQLdb.connect(host=hostname,user=username,passwd=password,db=database)
    except:
        db = None
    return db
    
def getPlayerID(db,player):
    cur = db.cursor()
    
    #search for player
    cur.execute("SELECT id FROM players WHERE agentname = %s",(player.player_nickname))
    player_id = 0
    if cur.rowcount == 0:
        #need to insert player into the database
        cur.execute("INSERT INTO players (agentname,AP,level,faction) VALUES (%s,%s,%s,%s)",(player.player_nickname,player.ap,player.level,player.team))
        if cur.rowcount == 1:
            cur.execute("SELECT id FROM players WHERE agentname = %s",(player.player_nickname))
            player_id = int(cur.fetchone()[0])
            db.commit()
    else:
        player_id = int(cur.fetchone()[0])
        cur.execute("UPDATE players SET AP = %s, level = %s, faction = %s WHERE id = %s",(player.ap,player.level,player.team,player_id))
        if cur.rowcount == 1:
            db.commit()
    return player_id
    
def updateStats(db,player,gear,player_id):
    cur = db.cursor()
    #we now have the player, so let's add a timepoint
    cur.execute("SELECT time_point FROM time_points WHERE player_id = %s ORDER BY time_point DESC", player_id)
    if cur.rowcount == 0:
        #need to start the first time point
        cur.execute("INSERT INTO time_points (player_id,time_point,AP,Level,itemCount) VALUES (%s,%s,%s,%s,%s)",(player_id,1,player.ap,player.level,gear['t']))
        if cur.rowcount == 1:
            db.commit()
    else:
        #already have at least one time point
        max_point = int(cur.fetchone()[0])
        cur.execute("INSERT INTO time_points (player_id,time_point,AP,Level,itemCount) VALUES (%s,%s,%s,%s,%s)",(player_id,max_point+1,player.ap,player.level,gear['t']))
        if cur.rowcount == 1:
            db.commit()
