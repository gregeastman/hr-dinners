import utility
from database import dataconnect
from calendar import month_name
from datetime import date
from mod_python import util


def index(req):
    user = utility.getUser(req)
    first = utility.getDate(req)
    next = utility.getNextMonth(first)
    
    dbconn = dataconnect()
    userInfo = dbconn.getUser(user)
    if userInfo == None or not userInfo.isadmin:
        del dbconn
        util.redirect(req, "./")
        return
    hosts = dbconn.getHosts(first, next)
    #TODO: find the number of hosts required per date
    del dbconn
    
    s = utility.buildTemplate() #%(title)s %(htmlbody)s are the bits to be filled in
    title = "%(monthName)s %(year)s Host Requirements Per Day" % {'monthName': month_name[first.month], 'year': first.year }
    body = """\
<h2>%(title)s</h2>
%(navigation)s
<table border=1>
%(rows)s
</table>
""" 
    rows = """\
    <tr>
        <th>Date</th>
        <th>Number of Hosts Required</th>
"""    

    for i in range(first.toordinal(), next.toordinal()):
        d = date.fromordinal(i)
        hostsNeeded = utility.getNumHostsNeeded(d, hosts)
        row = """\
    <tr>
        <td>%(date)s</td>
        <td>%(hosts)s</td>
    </tr>
""" % {'date': d.strftime("%A, %B %d"), 'hosts': hostsNeeded }

        rows += row         
        
        

    body = body % {'title': title, 'navigation': utility.getNavigation(first, './admin'), 'month': first.month, 'year': first.year, 'rows': rows }
    s = s % {'title': title, 'htmlbody': body }
    
    return s
