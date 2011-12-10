import utility
from geastman.web.httpvars import httpvars
from database import dataconnect
from mod_python import util

# The Publisher passes the Request object to the function
def index(req):
    user = utility.getUser(req)
    date = utility.getDate(req)
    httpvar = httpvars(req)
    availability = httpvar.getArray("availability")
    
    dbconn = dataconnect()
    userInfo = dbconn.getUser(user)
    if userInfo != None:
        for day, status in availability.iteritems():
            d = date.fromordinal(int(day))
            dbconn.updateAvailability(userInfo.id, d, int(status)) #this could fail and we aren't bubbling the error up, but it shouldn't happen
    
    del dbconn
    
    page = './?month=%(month)s&year=%(year)s' % {'month': date.month, 'year': date.year }
    util.redirect(req, page)
