from geastman.web.httpvars import httpvars
import utility
from database import dataconnect
from calendar import month_name
from datetime import date


def index(req):
    #user = utility.getUser(req)
    httpvar = httpvars(req)
    classType = utility.getClass(httpvar)
    first = utility.getDate(httpvar)
    next = utility.getNextMonth(first)
    
    dbconn = dataconnect()
    className = dbconn.getClassName(classType)
    available = dbconn.getAvailable(first, next, classType)
    status = dbconn.getReportable(classType)
    del dbconn
    
    s = utility.buildTemplate() #%(title)s %(htmlbody)s are the bits to be filled in
    title = "%(monthName)s %(year)s %(className)s Availability Summary" % {'monthName': month_name[first.month], 'year': first.year, 'className': className }
    body = """\
<h2>%(title)s</h2>
<h4><a href="./?class=%(class)s&month=%(month)s&year=%(year)s">Fill Out Personal Availability For The Month</a></h4>
%(navigation)s
<table border=1>
%(rows)s
</table>
""" 
    rows = """\
    <tr>
        <th>Date</th>
"""
    for k, v in status.iteritems():
        rows += """\
        <th>%(v)s</th>
""" % {'v': v }
    rows += """\
    </tr>
"""     

    for i in range(first.toordinal(), next.toordinal()):
        d = date.fromordinal(i)
        row = """\
    <tr>
        <td>%(date)s</td>
""" % {'date': d.strftime("%A, %B %d") }
        for k, v in status.iteritems():
            row += """\
        <td>%(val)s</td>
"""
            val = '&nbsp;'
            if available.has_key(i):
                if available[i].has_key(k):
                    val = utility.expandUsernames(available[i][k], d.strftime("%A, %B %d"))
            row = row % {'val': val }
        row += """\
    </tr>
"""
        rows += row         
        
        

    body = body % {'title': title, 'navigation': utility.getNavigation(first, './summary', classType), 'month': first.month, 'year': first.year, 'class': classType, 'rows': rows }
    s = s % {'title': title, 'htmlbody': body }
    
    return s
