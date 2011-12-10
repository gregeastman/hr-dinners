import utility
import ConfigParser
from database import dataconnect
from datetime import date
from calendar import month_name
import os


def index(req):
    user = utility.getUser(req)
    first = utility.getDate(req)
    next = utility.getNextMonth(first)
    
    dbconn = dataconnect()
    status = dbconn.getSelectable()
    userInfo = dbconn.getUser(user)
    if userInfo != None:
        availability = dbconn.getAvailability(userInfo.id, first, next)
    hosts = dbconn.getHosts(first, next)
    del dbconn
    
    
    s = utility.buildTemplate() #%(title)s %(htmlbody)s are the bits to be filled in
    title = "%(monthName)s %(year)s Candidate Dinner Availability" % {'monthName': month_name[first.month], 'year': first.year }
    body = """\
<h2>%(title)s</h2>
<h4><font color="#800000">Please consider signing up for Sunday.  This is the nicest day for candidates since they are able to fly in on Sunday, interview on Monday morning, and fly back Monday evening while only missing one day of the work week.  It's not ideal for hosts, but please help if you can to distribute the load.</font></h4>
<h4><a href="./summary?month=%(month)s&year=%(year)s">All Host Summary Report For The Month</a></h4>
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
    <input type="submit" value="Update Availability" />
</form>
"""
        tableData = ''
        config = ConfigParser.ConfigParser()
        file = os.path.dirname(__file__) + "/../../main.cfg"
        config.read(file)
        unavailable = config.getint("Main", "unavailable")
        for i in range(first.toordinal(), next.toordinal()):
            d = date.fromordinal(i)
            readOnly = utility.isDateReadOnly(d, hosts)
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
        form = form % {'month': first.month, 'year': first.year, 'numChoices': len(status), 'tableData': tableData }
    
    body = body % {'form': form, 'title': title, 'month': first.month, 'year': first.year, 'navigation': utility.getNavigation(first, './') }
    s = s % {'title': title, 'htmlbody': body }
    
    return s



