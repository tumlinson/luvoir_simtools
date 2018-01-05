
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from astropy.table import Column, QTable
import scipy.signal as signal
from astropy.io import fits
import os
import astropy.constants as con
import astropy.units as u

#telescope parameters
primary=[4.,5.,6.,7.,8.,9.,10.,11.,12.,13.,14.,15.]


dr7qso = QTable.read('../dr7_qso_galex.fits')


zem = dr7qso['Z'][0]
fuv = dr7qso['FUV_MAG'][0]
nuv = dr7qso['NUV_MAG'][0]

SDSS_spec_area = 9380.

N22 = np.where((fuv > 10) & (fuv < 22))
N22 = N22[0]
zem_N22 = zem[N22]

N21 = np.where((fuv > 10) & (fuv < 21))
N21 = N21[0]
zem_N21 = zem[N21]

N20 = np.where((fuv > 10) & (fuv < 20))
N20 = N20[0]
zem_N20 = zem[N20]

N19 = np.where((fuv > 10) & (fuv < 19))
N19 = N19[0]
zem_N19 = zem[N19]

N18 = np.where((fuv > 10) & (fuv < 18))
N18 = N18[0]
zem_N18 = zem[N18]


#define z_min_neviii = 0.46 (to give at least a search path of 0.1 in z
# for neViii and remain > 1050 rest)

zlim1 = 0.1
zlim2 = 0.5

lowz_N18 = np.where(zem_N18 > zlim1)
n_n18 = len(lowz_N18[0])/SDSS_spec_area
lowz_N19 = np.where(zem_N19 > zlim1)
n_n19 = len(lowz_N19[0])/SDSS_spec_area
lowz_N20 = np.where(zem_N20 > zlim1)
n_n20 = len(lowz_N20[0])/SDSS_spec_area
lowz_N21 = np.where(zem_N21 > zlim1)
n_n21 = len(lowz_N21[0])/SDSS_spec_area
lowz_N22 = np.where(zem_N22 > zlim1)
n_n22 = len(lowz_N22[0])/SDSS_spec_area

midz_N18 = np.where(zem_N18 > zlim2)
n_n18z1 = len(midz_N18[0])/SDSS_spec_area
midz_N19 = np.where(zem_N19 > zlim2)
n_n19z1 = len(midz_N19[0])/SDSS_spec_area
midz_N20 = np.where(zem_N20 > zlim2)
n_n20z1 = len(midz_N20[0])/SDSS_spec_area
midz_N21 = np.where(zem_N21 > zlim2)
n_n21z1 = len(midz_N21[0])/SDSS_spec_area
midz_N22 = np.where(zem_N22 > zlim2)
n_n22z1 = len(midz_N22[0])/SDSS_spec_area

#exposure time in hours for flat AB source at ~1300A, LUMOS G120M
# vs aperture numbers above

g120m_ab22 = [7.6,4.7,3.3,2.4,2.0,1.6,1.3,1.1,0.9,0.8,0.6,0.5]


#signal to noise (per resel) in 1 hour

MAB = [18.,18.5,19.0,19.5,20.0,20.5,21.0,21.5,22.0]
SN_120m4m = [11.42,9.03,7.23,5.73,4.58,3.62,2.86,2.28,1.81]
SN_120m6m = [17.06,13.61,10.81,8.55,6.82,5.42,4.32,3.42,2.71]
SN_120m9m = [25.70,20.33,16.22,12.88,10.23,8.13,6.45,5.13,4.05]
SN_120m15m = [42.83,34.02,27.03,21.47,17.05,13.54,10.80,8.54,6.76]

plt.plot(MAB,SN_120m15m,'g',label='15 m')
plt.plot(MAB,SN_120m9m,'b', label='9 m')
plt.plot(MAB,SN_120m6m,'orange', label='6 m')
plt.plot(MAB,SN_120m4m,'red', label='4 m')

plt.plot([18.0,18.0],[0.,50.],'--',color='grey')
plt.text(18.05,50,r'N={0:0.3f}, {1:0.3f} deg$^{{-2}}$'.format(n_n18,n_n18z1),
             rotation=90,fontsize=8)
plt.plot([19.0,19.0],[0.,50.],'--',color='grey')
plt.text(19.05,50,r'N={0:0.2f}, {1:0.2f} deg$^{{-2}}$'.format(n_n19,n_n19z1),
             rotation=90,fontsize=8)

plt.plot([20.0,20.0],[0.,50.],'--',color='grey')
plt.text(20.05,50,r'N={0:0.2f}, {1:0.2f} deg$^{{-2}}$'.format(n_n20,n_n20z1),
             rotation=90,fontsize=8)
plt.plot([21.0,21.0],[0.,50.],'--',color='grey')
plt.text(21.05,50,r'N={0:0.2f}, {1:0.2f} deg$^{{-2}}$'.format(n_n21,n_n21z1),
             rotation=90,fontsize=8)
plt.plot([22.0,22.0],[0.,50.],'--',color='grey')
plt.text(22.05-0.2,50,
             r'N={0:0.2f}, {1:0.2f} deg$^{{-2}}$'.format(n_n22,n_n22z1),
             rotation=90,fontsize=8)
plt.xlabel('AB mag')
plt.ylabel('S/N per resel at 1300$\AA$')
plt.title('LUMOS G120M for quasars at z > {0}, > {1}'.format(zlim1,zlim2))
plt.legend()
plt.show()

#plt.plot(primary,g120m_ab22)
#plt.show()
###Plot the delta_z to NeVIII vs zem within the mag cuts

###Need to do cuts for Lya-Lyb, OVI, NeVIII
