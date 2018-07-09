#!/usr/bin/env python
# this script will read a fits table and provide information about
# the column names, column formats, extensions for the file
#
# R. Diaz 11/07/2016

import sys
import astropy.io.fits as pf
import argparse
import numpy as np


#Check arguments. THE ONLY ONE NOW IS FILENAME
parser = argparse.ArgumentParser(description = "Check a Fits Table:")
parser.add_argument('-filename', help='filename is:')
parser.add_argument('-info', help='What information you want?')
parser.add_argument('-headnum',help='Get header number here', default = 0)
args = parser.parse_args()

print args.filename, args.info
# Open file

filein = pf.open(args.filename)

def all():
    print 'FIlename =',filein
    return filein.info()
def header():
    filehdr = filein[0].header
    return  filehdr
def extensions():
    if filein[0].header.get('NEXTEND', default = -1) != -1:
        return filein[0].header['NEXTEND']
    else:
        return 0

value=args.headnum
def readheader(value):
    return filein[value].header


next=extensions()
head1=readheader(1)

print all()
print next
print head1
