import ConfigParser
from datetime import datetime
from datetime import date
import os

class user:
    def __init__(self, row):
        self.id = row.id
        self.tlgid = row.tlgid
        self.username = row.username
        self.firstname = row.firstname
        self.lastname = row.lastname
        self.email = row.email
        self.cellphone = row.cellphone
        self.isadmin = row.isadmin
        
    
    def __del__(self):
        del self.id
        del self.tlgid
        del self.username
        del self.firstname
        del self.lastname
        del self.email
        del self.cellphone
        del self.isadmin
        


def getDate(httpvar):
    month = httpvar.getValue("month")
    year = httpvar.getValue("year")
    
    first = ''
    if month and year:
        s = "%(year)s-%(month)s" % {'year': year, 'month': month}
        #TODO: add error trapping to make sure parameters are sane
        first = datetime.strptime(s, "%Y-%m").date() #date of first of the month
    else:
        first = date.today()
        first = first.toordinal() - first.day + 1
        first = date.fromordinal(first)
    return first



def getUser(req):
    user = req.user
    if not user:
        config = ConfigParser.ConfigParser()
        configFile = os.path.dirname(__file__) + "/../../main.cfg"
        config.read(configFile)
        user = config.get("Main", "defaultuser")
    return user.lower()

def getClass(httpvar):
    classType = httpvar.getValue("class")
    if classType == None:
        classType = 1
    return int(classType)

def getNextMonth(d):
    month = d.month
    year = d.year
    year = year + (month / 12)
    month = (month % 12) + 1
    s = "%(year)s-%(month)s" % {'year': year, 'month': month}
    return datetime.strptime(s, "%Y-%m").date()
    
def getPrevMonth(d):
    month = d.month
    year = d.year
    if month == 1:
        year -= 1
        month = 12
    else:
        month -= 1
    s = "%(year)s-%(month)s" % {'year': year, 'month': month}
    return datetime.strptime(s, "%Y-%m").date()


def isDateReadOnly(d, hosts, classType):
    if getNumHostsNeeded(d, hosts, classType) == 0:
        return 1
    return 0

def getNumHostsNeeded(d, hosts, classType):
    #TODO: make less hacky so that classTypes aren't hard-coded
    if d.weekday() == 4: #Friday
        if classType == 1:
            return 0
        else:
            return 1
    elif d.weekday() == 5: #Saturday
        return 0
    elif d.weekday() == 6:  #Sunday
        if classType == 1:
            return 2
        else:
            return 0
    return 1


def buildTemplate():
    s = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>%(title)s</title>
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="-1" />
</head>
<body>
%(htmlbody)s
</body>
</html>
"""
    return s



def getNavigation(d, page, classType):
    prev = getPrevMonth(d)
    next = getNextMonth(d)
    s = """\
<a href="%(page)s?class=%(classType)s&month=%(pmon)s&year=%(pyear)s">&lt;&lt;Previous Month</a>&nbsp;&nbsp;&nbsp;&nbsp;<a href="%(page)s?class=%(classType)s&month=%(nmon)s&year=%(nyear)s">Next Month&gt;&gt;</a>
<br /><br />
""" % {'page': page, 'classType': classType, 'pmon': prev.month, 'pyear': prev.year, 'nmon': next.month, 'nyear': next.year }
    return s

def expandUsernames(li, date):
    ret = ""
    emails = ""
    email = ""
    for element in li:
        if ret:
            ret += "<br />"
        user = """\
<a href="http://guru/Staff/EmployeeProfile.aspx?id=%(tlg)s">%(fullname)s</a>%(cellphone)s"""
        cellphone = "";
        if element.cellphone != "":
            cellphone = ": " + element.cellphone
        user = user % {"tlg": element.tlgid, "fullname": element.firstname + " " + element.lastname, "cellphone": cellphone }
        ret += user
        if emails:
            emails +=";"
        emails += element.email
    if emails:
        email = """\
<a href="mailto:%(emails)s?subject=Candidate Dinner On %(date)s"><b>[Email All]</b></a>"""
        email = email % {"emails": emails, "date": date }
    if ret:
        ret += "<br /><br />"
    ret += email
    return ret


def expandList(li):
    li.sort()
    ret = ""
    for element in li:
        if ret:
            ret += "<br />"
        ret += element
    return ret

