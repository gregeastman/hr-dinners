#!/usr/bin/env python
"""
Nightly script to update the user database
"""

'''
Created on Jan 10, 2011

@author: greg
'''

import sys
import getopt
import pyodbc
import ConfigParser
import os
from geastman.util import nameformatter

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    configfile = None #initialize configfile to null
    errMsg = None
    if argv is None:
        argv = sys.argv
    try:
        try:
            #for short parameters, follow parameter with colon to indicate it takes a parameter
            #for long parameters, follow parameter with = to indicate it takes a parameter
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
            raise Usage(msg)
        #process options
        for o in opts: #No need to get a as no options take arguments
            if o in ("-h", "--help"):
                print __doc__
            #process other options
        #process arguments:
        for arg in args:
            if configfile == None:
                configfile = arg #argument is what configfile to use - only uses the first one
        
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
    output = None
    try:
        output = open("C:/Users/geastman/Documents/SQL/user_update.sql", "w")
    except:
        pass
    config = ConfigParser.ConfigParser()
    if configfile == None:
        configfile = os.path.dirname(__file__) + "/../../main.cfg"
    config.read(configfile)
    track = pyodbc.connect(config.get("Main", "trackdb"))
    local = pyodbc.connect(config.get("Main", "localdb"))
    trkcurs = track.cursor()
    lclcurs = local.cursor()
    query = """\
SELECT 
    USER_NUMBER, SYSTEM_LOGIN, USER_NAME_EXT, EMAIL, STATUS_CAT 
FROM
    EMP.EMPLOYEE_BASIC_INFO  
ORDER BY 
    USER_NUMBER
"""
    trkcurs.execute(query)
    for row in trkcurs:
        tlgID = row.USER_NUMBER
        username = row.SYSTEM_LOGIN
        if username != None:
            username = username.lower()
        fullname = row.USER_NAME_EXT
        firstname = ""
        lastname = ""
        status = False
        if row.STATUS_CAT == 1:
            status = True
        if fullname != None:
            names = fullname.split(",")
            firstname = ""
            lastname = ""
            try:
                lastname = names[0].strip()
                firstname = names[1].strip()
            except:
                pass
            nameObj = nameformatter.Name(firstname, lastname)
            firstname = nameObj.first
            lastname = nameObj.last
        email = row.EMAIL
        if email != None:
            email = email.lower()
        try:
            lclcurs.execute("SELECT updateuser(?, ?, ?, ?, ?, ?)", tlgID, username, firstname, lastname, email, status)
        except:
            if errMsg != None:
                errMsg = errMsg + " "
            else:
                errMsg = ""
            errMsg = errMsg + "Cannot update " + str(tlgID) + str(username) + str(firstname) + str(lastname) + str(email) + str(status)
        if output != None:
            query = "SELECT updateuser(%(tlgID)s, %(username)s, %(firstname)s, %(lastname)s, %(email)s, %(status)s);\n"
            try:
                query = query % {"tlgID": _prepStr(tlgID), "username": _prepStr(username), "firstname": _prepStr(firstname), "lastname": _prepStr(lastname), "email": _prepStr(email), "status": str(status) }
            except:
                query = None
            if query != None:
                output.write(query)
    lclcurs.close()
    trkcurs.close()
    local.commit()
    local.close()
    track.close()
    if output != None:
        output.close()
    return errMsg
        
def _prepStr(inputString):
    outputString = ""
    if inputString != None:
        outputString = inputString.replace("'", "\\'")
    return "'" + outputString + "'"

if __name__ == "__main__":
    sys.exit(main())
    
    