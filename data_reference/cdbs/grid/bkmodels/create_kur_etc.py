#!/python/bin

import astropy.io.fits as pf
import argparse
import os
import sys

'''
     Converts a Kurucz model to an ETC compliant file
    -i, i'--finput', input file
    -o, --output',  is the output file name
    -g gravity value
'''
def parse_args():

    '''
    Parse command line arguments
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-o','--output', action='store', dest='output', default = None)
    parser.add_argument('-i','--finput', action='store', dest='finput', default = None)
    parser.add_argument('-g','--gval', action='store', dest='gravity', default = '40')
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = parse_args()

    gv=['g00', 'g05', 'g10', 'g15', 'g20', 'g25', 'g30', 'g35', 'g40', 'g45', 'g50']
    v=['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50']

    # define output filename

    if args.finput != None:
        print('reading file'+args.finput)
        infile = args.finput
    else:
        print 'Please provide with the finput file'
        sys.exit(1)

    if args.gravity != None:
        print('Extracting flux for gravity ',args.gravity)
        grav= 'g{}'.format(args.gravity)
        print grav
        if grav not in gv:
            print  'value ', grav, 'is not in ', v
            sys.exit(1)
    else:
        print 'provide with the gravity value to extract ', v
        sys.exit(1)

    #Read kurucs model
    model=pf.open(infile)
    data=model[1].data

    wave=data.field('WAVELENGTH')
    flux=data.field(grav)
    print wave
    print 'flux =',flux
    if args.output != None:
        print('creating file'+args.output)
        outfile = args.outpu
    else:
        outfile = 'kurucz_etc.fits'


    if os.access(outfile, os.R_OK):
        os.remove(outfile)


    descrip = "New ETC FITS table"
    history0 = " Created by "

    # Read ol

    # Define primary heder and add the needed keywords
    prihdr = pf.Header()
    prihdr['FILENAME'] = outfile
    prihdr['DESCRIP']=descrip
    prihdr['COMMENT'] = '= \'File created for the ETC\''


    prihdu = pf.PrimaryHDU(header=prihdr)


    time=[]
    compname=[]
    filename=[]
    comment=[]
    # Defines columns and asign their values

    col2=pf.Column(name='FLUX', format='E',unit='FLAM',array=flux)
    col1=pf.Column(name='WAVELENGTH', format='E', unit='ANGSTROMS',array=wave)

    cols0 = [col1,col2]

    cols = pf.ColDefs(cols0)

    tbhdu = pf.BinTableHDU.from_columns(cols)

    thdulist = pf.HDUList([prihdu,tbhdu])
    thdulist.writeto(outfile)

