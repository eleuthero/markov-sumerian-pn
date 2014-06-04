#!/usr/bin/python

import re
import sys
import math

from math import log10

# Globals
# =======

EPSILON = .05  # probability of unattested a-b sign sequences.

init = { }  # Initial signs and their subsequent signs
segu = { }  # Non-initial signs and their subsequent signs
freq = { }  # Total sign frequency count

split_regex = re.compile(r"[-.:]")

def getNames(filename):
    with open(filename) as fin:
        return fin.readlines()

def compileFrequencyInit(current):

    # Have we seen the current sign before ?

    if current in init:
        entry = init[current]
    else:
        entry = { }
        init[current] = entry

    # Increment count.

    if current in entry:
        entry[current] += 1
    else:
        entry[current] = 1

def compileFrequency(current):
    if current in freq:
        freq[current] += 1
    else:
        freq[current] = 1

def compileFrequencySegu(current, next):

    # Have we seen the current sign before ?

    if current in segu:
        entry = segu[current]
    else:
        entry = { }
        segu[current] = entry

    # Have we seen the transition from the current to the next sign ?

    if next in entry:
        entry[next] += 1
    else:
        entry[next] = 1

def getFrequencyScoreInitial(current, log):
    score = EPSILON

    # Calculate probability of current appearing word-initial

    gtl = sum( [ sum( [ init[w][u] for u in init[w] ] ) for w in init ] )

    if current in init:
        stl = sum( [ init[current][u] for u in init[current] ] )
        score = float(stl) / gtl

    if log:
        return math.log10(score)
    else:
        return score

def getFrequencyScoreSegu(current, next, log):
    trans_score = EPSILON
    freq_score = EPSILON

    # Calculate probability of current --> next transition

    if current in segu:
        total_trans = sum( [ segu[current][u] for u in segu[current] ] )

        if next in segu[current]:
            trans_score = float(segu[current][next]) / total_trans

    if next in freq:
        total_freq = sum( [ freq[u] for u in freq ] )

        if next in freq:
            freq_score = float(freq[next]) / total_freq

    if log:
        return math.log10(trans_score) + math.log10(freq_score)
    else:
        return trans_score * freq_score

def split_name(name):
    return list( re.split(split_regex, name) )

def process(name):

    # Turn name into a queue of signs.

    sequence = split_name(name)
    sequence.reverse()

    next = None

    if len(sequence) > 0:
        current = sequence.pop().strip()

    if current:

        # Add current sign to initial frequency table.

        compileFrequencyInit(current)

        # Add current sign to total frequency table.

        compileFrequency(current)

        while len(sequence) > 0:
            next = sequence.pop().strip()

            # Add current --> next to our transition tally.

            compileFrequencySegu(current, next)

            # Add sign to total frequency count.

            compileFrequency(current)

            current = next 

        # Add current --> None to our transition tally.

        compileFrequencySegu(current, None)

def tally(current, element, log):
    if log:
        return current + element
    else:
        return current * element

def score(name, log):

    # Turn name into a queue of signs.

    sequence = split_name(name)
    sequence.reverse()

    if log:
        freq = 0
    else:
        freq = 1

    next = None

    # print "score(): %s: " % (name)

    if len(sequence) > 0:
        current = sequence.pop().strip()

    if current:
        score = getFrequencyScoreInitial(current,
                                         log)

        # print "\t[%s] = %.5f" % (current, score)
        freq = tally(freq, score, log)

        while len(sequence) > 0:
            next = sequence.pop().strip()
       
            score = getFrequencyScoreSegu(current,
                                          next,
                                          log)

            # print "\t[%s ==> %s] = %.5f" % (current, next, score)
            freq = tally(freq, score, log)
            current = next 
 
        score = getFrequencyScoreSegu(current,
                                      None,
                                      log)

        # print "\t[%s ==> None] = %.5f" % (current, score)

        freq = tally(freq, score, log)

        # print "\tscore: %s: %.5f" % (name, freq)
        # print 

    return freq
        
def showFrequenciesList():

    print """INITIAL
======="""

    showFrequencyList(init)

    print
    print """SUBSEQUENT
======="""

    showFrequencyList(segu)

def showFrequencyList(coll):
    for current in sorted(coll):
        print "[%s] -->" % (current)

        total = 0

        for next in coll[current]:
            total += coll[current][next]

        for next in sorted(coll[current]):
            count = float(coll[current][next])
            print '\t[%s]: %5i / %5i (%.3f%%)' % (next, count, total, count * 100 / total)

        print

def showFrequenciesTable(log = False):

    merged = sorted(dict(init.items() + segu.items()))

    # Print header row.

    print 'NXT CUR,INITIAL,',
    for current in merged:
   	print current, ',',
    print

    print '========',
    for current in merged:
        print '=======,',
    print

    # For each sign in the merged set...

    showFrequenciesTableRow(merged, None, log)

    for next in merged:
        showFrequenciesTableRow(merged, next, log)

def showFrequenciesTableRow(coll, next, log):

    # Print header cell

    print next, ',',

    # Print initial count

    if next in init:
        print sum( [ init[next][key] for key in init[next] ] ), ",",
    else:
        print '0,',

    # For each transition into the next sign ...

    for current in coll:
        if current in segu:
            if next in segu[current]:
                if log:
                    # print '%i / %i (%.5f),' % (segu[current][next],
                    #                            sum( [ segu[current][u] for u in segu[current] ] ),
                    #                            getFrequencyScoreSegu(current, next, log)),
                    print '%.5f,' % getFrequencyScoreSegu(current, next, log),
                else:
                    # print '%i / %i (%.5f%%),' % (segu[current][next],
                    #                              sum( [ segu[current][u] for u in segu[current] ] ),
                    #                              getFrequencyScoreSegu(current, next, log)),
                    print '%.5f%%,' % getFrequencyScoreSegu(current, next, log),
            else:
                if log:
                     print '%d,' % EPSILON,
                else:
                    print '0,',
        else:
            if log:
                print '%d,' % EPSILON,
            else:
                print '0,',

    print

def compare(names):
    with open(sys.argv[2], "r") as fin:
        wordlist = fin.readlines()

    # Create word score list

    words = [ ]
    for word in wordlist:
        word = word.strip().lower()
        w = { }
        w["name"]  = word
        w["score"] = score(word, True)
        words.append(w)

    # Sort and output words and p-scores

    for word in sorted(words, key=lambda k: -k["score"]):
        print "%s, %.5f" % (word["name"], word["score"])

# ====
# Main
# ====

# Ensure user has given us a corpus filename.

if len(sys.argv) < 3:
    print "Enter names corpus file as first argument to script."
    print "Enter words corpus file as second argument to script."
    exit(1)

# Calculate frequency of letter transitions in the corpus.

names = getNames(sys.argv[1])

for name in names:
    process(name.strip().lower())

# Show transition analysis.

# Enable this to see a list of transitions
# showFrequenciesList()

# Enable this to see a table of transitions in percentage format
# (all transitions # sum to 100%)
# showFrequenciesTable(log = False)

# Enable this to see a table of transitions with p-score (logarithmic)
# showFrequenciesTable(log = True) 

compare(names)
