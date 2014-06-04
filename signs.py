#!/usr/bin/python

import re
import sys

split_regex = re.compile(r"[-.:]")
q = { }
c = [ ]  

def getNames(filename):
    with open(filename) as fin:
        return fin.readlines()

def split_name(name):
    global split_regex
    
    return list( re.split(split_regex, name) )

def process(l):
    process_list(l, 0, len(l))

def process_list(l, start, end):
    global c

    if end == (start + 1):

        # Only interested in strings of at least two signs.

        return

    else:

        # Recursive call may attempt to add the same substring
        # repeatedly.  Check indices on substring before accepting.

        if not [start, end] in c:
            c.append( [start, end] )

            # Order inventory by number of signs in string.

            n = end - start
            s = '-'.join(l[start:end])

            if not n in q:
                q[n] = { }
 
            if s in q[n]:
                q[n][s] += 1
            else:
                q[n][s] = 1

        # Recursively call on left and right substrings.

        process_list(l, start + 1, end)
        process_list(l, start, end - 1)

# ====
# Main
# ====

if len(sys.argv) < 2:
    print "Enter corpus file as first argument to script."
    exit(1)

names = getNames(sys.argv[1])

for name in names:

    # Reset the current list of seen indices.

    c = [ ]

    process( split_name( name.strip().lower() ) )

# Output
# Show only the top 50 sign substrings for each string length

for n in q:
    print '# %i signs: ' % n
    for s in sorted(q[n], key=lambda s: -q[n][s])[:50]:
        print '\t%-5i\t%s' % (q[n][s], s)
