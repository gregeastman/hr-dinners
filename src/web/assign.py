import utility
from database import dataconnect
from datetime import date
from mod_python import util


def _buildIndex(available):
    index = {}
    for d in available:
        if available[d].has_key("assigned"): #if there are hosts assigned, ignore the date
            continue
        numHosts = 0        
        for s in available[d]:
            numHosts += len(available[d][s])
        if not index.has_key(numHosts):
            index[numHosts] = []
        index[numHosts].append(d)
    return index


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
    available = dbconn.getAvailable(first, next)
    index = _buildIndex(available)
    hosts = dbconn.getHosts(first, next)
    counts = {} #TODO: need to update counts with already assigned from month - this information is in available
    assign = {}
    
    for numHosts in index:
        days = index[numHosts]
        for i in days:
            d = date.fromordinal(i)
            hostsNeeded = utility.getNumHostsNeeded(d, hosts)
            if hostsNeeded == 0: #don't assign people for days not needed
                continue
            least = []
            for status, users in available[i].iteritems():
                scalar = 0
                if status == 2:
                    scalar = 2
                for user in users:
                    numDinners = 0
                    if counts.has_key(user.id):
                        numDinners = counts[user.id]
                    numDinners += scalar #add fudge factor to balance things out
                    least.append((numDinners, user.id))
            least.sort()
            #for user in least[:hostsNeeded]:
            userCounter = 0
            while (hostsNeeded > 0 and userCounter < len(least)):
                userTuple = least[userCounter]
                userCounter += 1
                #counts = _assignHost(counts, i, userTuple[1]
                if dbconn.assignHost(userTuple[1], d):
                    hostsNeeded -= 1
                    if not counts.has_key(userTuple[1]):
                        counts[userTuple[1]] = 0
                    counts[userTuple[1]] += 1
                    if not assign.has_key(i):
                        assign[i] = []
                    assign[i].append(userTuple[1])
    
    del dbconn
    page = './summary?month=%(month)s&year=%(year)s' % {'month': first.month, 'year': first.year }
    util.redirect(req, page)
