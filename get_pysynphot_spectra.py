import pysynphot as S 
import os 

def add_spectrum_to_library(): 

   spec_dict = {} 

   filename_qso = os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'agn', 'qso_template.fits')
   qso = S.FileSpectrum(filename_qso)
   q = qso.renorm(21., 'abmag', S.ObsBandpass('galex,fuv'))
   spec_dict['QSO'] = q 

   filename_star = os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'pickles', 'dat_uvk', 'pickles_uk_1.fits')
   star = S.FileSpectrum(filename_star)
   s = star.renorm(21., 'abmag', S.ObsBandpass('galex,fuv'))
   spec_dict['O5V Star'] = s 

   filename_star = os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'pickles', 'dat_uvk', 'pickles_uk_26.fits')
   star = S.FileSpectrum(filename_star)
   s = star.renorm(21., 'abmag', S.ObsBandpass('galex,fuv'))
   spec_dict['G2V Star'] = s 

   filename_star = os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'galactic', 'orion_template.fits') 
   star = S.FileSpectrum(filename_star)
   s = star.renorm(21., 'abmag', S.ObsBandpass('galex,fuv'))
   spec_dict['Orion Nebula'] = s 

   filename_star = os.path.join(os.environ['PYSYN_CDBS'], 'calspec', 'g191b2b_mod_010.fits') 
   star = S.FileSpectrum(filename_star)
   s = star.renorm(21., 'abmag', S.ObsBandpass('galex,fuv'))
   spec_dict['G191B2B'] = s 

   filename_star = os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'kc96', 'starb1_template.fits') 
   star = S.FileSpectrum(filename_star)
   s = star.renorm(21., 'abmag', S.ObsBandpass('galex,fuv'))
   spec_dict['Starburst, No Dust'] = s 

   filename_star = os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'kc96', 'starb6_template.fits') 
   star = S.FileSpectrum(filename_star)
   s = star.renorm(21., 'abmag', S.ObsBandpass('galex,fuv'))
   spec_dict['Starburst, E(B-V) = 0.6'] = s 

   return spec_dict 

