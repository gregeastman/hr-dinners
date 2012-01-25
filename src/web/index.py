from geastman.web.httpvars import httpvars
import utility
from database import dataconnect
from datetime import date
from calendar import month_name


def index(req):
    user = utility.getUser(req)
    
    httpvar = httpvars(req)
    classType = utility.getClass(httpvar)
    first = utility.getDate(httpvar)
    next = utility.getNextMonth(first)
    
    
    dbconn = dataconnect()
    className = dbconn.getClassName(classType)
    status = dbconn.getSelectable(classType)
    userInfo = dbconn.getUser(user)
    if userInfo != None:
        availability = dbconn.getAvailability(userInfo.id, first, next, classType)
    hosts = dbconn.getHosts(first, next)
    unavailable = dbconn.getUnavailableStatus(classType)
    del dbconn
    
    s = utility.buildTemplate() #%(title)s %(htmlbody)s are the bits to be filled in
    title = "%(monthName)s %(year)s %(className)s Availability" % {'monthName': month_name[first.month], 'year': first.year, 'className': className }
    body = """\
<h2>%(title)s</h2>
"""
    if classType == 1:
        body = body + """\
<h4><font color="#800000">Please consider signing up for Sunday.  This is the nicest day for candidates since they are able to fly in on Sunday, interview on Monday morning, and fly back Monday evening while only missing one day of the work week.  It's not ideal for hosts, but please help if you can to distribute the load.</font></h4>"""
    body = body + """\
<h4><a href="./summary?class=%(class)s&month=%(month)s&year=%(year)s">All Host Summary Report For The Month</a></h4>
%(navigation)s
%(form)s
"""
    form = ""
    if userInfo == None:
        form = "<h3>User not in approved user database. Contact administrator for assistance.</h3>"
    else:
        form = """\
<form action="./update" method="post">
    <table border=1>
        <tr>
            <th>Date</th>
            <th colspan=%(numChoices)s>Availability</th>
        </tr>
%(tableData)s
    </table>
    <br />
    <input type="hidden" name="month" value="%(month)s" />
    <input type="hidden" name="year" value="%(year)s" />
    <input type="hidden" name="class" value="%(class)s" />
    <input type="submit" value="Update Availability" />
</form>
"""
        tableData = ''
        for i in range(first.toordinal(), next.toordinal()):
            d = date.fromordinal(i)
            readOnly = utility.isDateReadOnly(d, hosts, classType)
            disabled = ''
            if readOnly:
                disabled = 'disabled="disabled" '
            choice = unavailable #set default to be unavailable
            if availability.has_key(i):
                choice = availability[i]
            
            tableData = tableData + """\
        <tr>
            <td>%(date)s</td>
%(choices)s
        </tr>
"""
            choices = ''
            for k, v in status.iteritems():
                checked=''
                if k == choice:
                    checked='checked="checked" '
                choices = choices + """\
                <td><input type="radio" name="availability[%(index)s]" value="%(value)s" %(checked)s%(readOnly)s/>%(title)s</td>
    """ % {'index': i, 'readOnly': disabled, 'value': k, 'title': v, 'checked': checked }
            
            tableData = tableData % {'date': d.strftime("%A, %B %d"), 'choices': choices }
        form = form % {'month': first.month, 'year': first.year, 'class': classType, 'numChoices': len(status), 'tableData': tableData }
    
    body = body % {'form': form, 'title': title, 'month': first.month, 'year': first.year, 'class': classType, 'navigation': utility.getNavigation(first, './', classType) }
    s = s % {'title': title, 'htmlbody': body }
    
    return s



