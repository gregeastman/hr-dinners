import ConfigParser
import pyodbc
import os
from utility import user

class dataconnect:
    def __init__(self):
        self._config = ConfigParser.ConfigParser()
        file = os.path.dirname(__file__) + "/../../main.cfg"
        self._config.read(file)
        conn = self._config.get("Main", "localdb")
        self._conn = pyodbc.connect(conn)
    
    def __del__(self):
        self._conn.close()
        del self._config

    def assignHost(self, userid, date):
        query = 'SELECT assignhost(?, ?)'
        cursor = self._conn.cursor()
        cursor.execute(query, userid, date)
        row = cursor.fetchone()
        cursor.close()
        self._conn.commit()
        if row.assignhost == "0": return False
        return True

    def getSelectable(self):
        status = {}
        query = 'SELECT id, name FROM getselectable()'
        cursor = self._conn.cursor()
        cursor.execute(query)
        for row in cursor:
            status[row.id] = row.name
        cursor.close()
        return status

    def getReportable(self):
        status = {}
        query = 'SELECT id, name FROM getreportable()'
        cursor = self._conn.cursor()
        cursor.execute(query)   
        for row in cursor:
            status[row.id] = row.name
        status["assigned"] = "Assigned" # create pseudo assigned status that users in other statuses can also be in
        cursor.close()
        return status   

    def getAvailable(self, first, next):
        available = {}
        unavailable = self._config.getint("Main", "unavailable")
        query = 'SELECT * FROM getavailable(?, ?)'
        cursor = self._conn.cursor()
        cursor.execute(query, first, next)
        for row in cursor:
            day = row.day.toordinal()
            if not available.has_key(day):
                available[day] = {}
            if row.status != unavailable:
                if not available[day].has_key(row.status):
                    available[day][row.status] = []
                userInfo = user(row) #TODO: don't duplicate storage of this
                available[day][row.status].append(userInfo)
            assigned = row.assigned
            if assigned == None:
                assigned = 0
            else:
                assigned = int(row.assigned)
            if assigned: #treat assigned as a pseudo status
                if not available[day].has_key("assigned"):
                    available[day]["assigned"] = []
                userInfo = user(row) #TODO: don't duplicate storage of this
                available[day]["assigned"].append(userInfo)        
        cursor.close()
        return available

    def getAvailability(self, userid, first, next):
        availability = {}
        query = 'SELECT day, status FROM getavailability(?, ?, ?)'
        cursor = self._conn.cursor()
        cursor.execute(query, userid, first, next)
        for row in cursor:
            availability[row.day.toordinal()]=row.status
        cursor.close()
        return availability

    def updateAvailability(self, userid, date, status):
        query = 'SELECT updateavailability(?, ?, ?)'
        cursor = self._conn.cursor()
        cursor.execute(query, userid, date, status)
        row = cursor.fetchone()
        cursor.close()
        self._conn.commit()
        if row.updateavailability == "0": return False
        return True
        

    def getHosts(self, first, next):
        hosts = {}
        query = 'SELECT day, hosts FROM gethosts(?, ?)'
        cursor = self._conn.cursor()
        cursor.execute(query, first, next)
        cursor.close()
        return hosts

    def updateHosts(self, date, hosts):
        query = 'SELECT updatehosts(?, ?)'
        cursor = self._conn.cursor()
        cursor.execute(query, date, hosts)
        cursor.close()
        self._conn.commit()
    
    def getUser(self, username):
        userInfo = None
        query = 'SELECT * FROM getuser(?)'
        cursor = self._conn.cursor()
        cursor.execute(query, username)
        row = cursor.fetchone()
        if row != None: userInfo = user(row)
        cursor.close()
        return userInfo

