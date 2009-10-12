"""
Fetches tickets from the marinemap issue tracker and generates a dot file for 
generating a diagram using graphviz
"""

import urllib
f = urllib.urlopen('http://code.google.com/p/marinemap/issues/csv?can=1&q=&colspec=ID%20Type%20Status%20Priority%20Owner%20Component%20BlockedOn%20EstimatedTime%20Summary')


def get_ticket(id):
    for ticket in tickets:
        if ticket['id'] == id:
            return ticket
    return None

import csv
reader = csv.reader(f, delimiter=',', quotechar='"')
print """
digraph graphname {
   overlap=false
   ratio=0.4
"""
tickets = []

tickets_that_block = []

for row in reader:
    if reader.line_num != 1 and row:
        ticket = {
            'id': int(row[0]),
            'type': row[1],
            'status': row[2],
            'priority': row[3],
            'owner': row[4],
            'component': row[5],
            'blockedon': row[6],
            'estimatedtime': row[7],
            'summary': row[8]
        }
        blockers = [tid.strip() for tid in ticket['blockedon'].split(',')]
        ticket['blockedon'] = []
        for blocker in blockers:
            if blocker != '':
                blocker = int(blocker)
                ticket['blockedon'].append(blocker)
                tickets_that_block.append(blocker)
        if ticket['component'] != 'KmlTools':
            tickets.append(ticket)

for ticket in tickets:
    for blocker in ticket['blockedon']:
        print '%s -> %s;' % (blocker, ticket['id'])

for ticket in tickets:
    if (len(ticket['blockedon']) > 0 or ticket['id'] in tickets_that_block):
        fillcolor = 'white'
        fontcolor = 'black'
        style = 'solid'
        if len(ticket['blockedon']) == 0:
            fillcolor = 'palegoldenrod'
            fontcolor = 'black'
            style= 'filled'
        else:
            next_step = True
            for blocker in ticket['blockedon']:
                blocker = get_ticket(blocker)
                if blocker:
                    if blocker['status'] == 'WontFix' or blocker['status'] == 'Fixed' or blocker['status'] == 'Done':
                        pass
                    else:
                        next_step = False
            if next_step:
                fillcolor = 'palegoldenrod'
                fontcolor = 'black'
                style= 'filled'
                    
        if ticket['status'] == 'WontFix' or ticket['status'] == 'Fixed' or ticket['status'] == 'Done':
            fillcolor = 'lightslategray'
            fontcolor = 'black'
        if ticket['status'] == 'Started':
            fillcolor = 'palegreen'
            
        print '%s [URL=http://code.google.com/p/marinemap/issues/detail?id=%s,label="%s\\n%s\\n%s\\n%s\\nStatus: %s\\nOwner: %s",fontsize=24,fillcolor=%s,fontcolor=%s, style=%s];' % (ticket['id'], ticket['id'], ticket['summary'], ticket['estimatedtime'], ticket['priority'], ticket['component'], ticket['status'], ticket['owner'], fillcolor, fontcolor, style)
        
print "}"
