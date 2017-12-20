#####BOKEH CORONAGRAPH NOISE MODEL SIMULATOR#####
# This code produces an interactive browser widget that runs
# the coronagraph noise model
#
#
# To run this code on your local machine, type
# bokeh serve --show coron_model.py
# 
################################################

# Import some standard python packages

import numpy as np
from astropy.io import fits, ascii 
import pdb
import sys
import os 
from astropy.table import Table, Column
import os
from bokeh.io import curdoc
from bokeh.client import push_session

from bokeh.themes import Theme 
import yaml 
from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource, HBox, VBoxForm, HoverTool, Paragraph, Range1d, DataRange1d, Label, DataSource
from bokeh.models.glyphs import Text, Rect
from bokeh.layouts import column, row, WidgetBox 
from bokeh.models.widgets import Slider, Panel, Tabs, Div, TextInput, RadioButtonGroup, Select, RadioButtonGroup
from bokeh.io import hplot, vplot, curdoc, output_file, show, vform
from bokeh.models.callbacks import CustomJS
from bokeh.embed import components, autoload_server



import coronagraph as cg  # Import coronagraph model

#allow it to run it from other folders and still know where planet folder is
planetdir = "../coronagraph/planets/" #new path compared to before
stardir = "../coronagraph/star_galaxy/" #new path compared to before
relpath = os.path.join(os.path.dirname(__file__), planetdir)
relpath2 = os.path.join(os.path.dirname(__file__), stardir)

################################
# PARAMETERS
################################

# Integration time (hours)
Dt = 24.0 # - SLIDER

# Telescopes params
diam = 12.7 # mirror diameter - SLIDER
Res = 150. # vis resolution - SLIDER
Res_UV = 20. # UV resolution - SLIDER
Res_NIR = 100. #NIR resolution - SLIDER
Tsys = 270. # system temperature - SLIDER

# Planet params
alpha = 90.     # phase angle at quadrature
Phi   = 1.      # phase function at quadrature (already included in SMART run)
Rp    = 1.0     # Earth radii - SLIDER 
r     = 1.0     # semi-major axis (AU) - SLIDER 

# Stellar params
Teff  = 5780.   # Sun-like Teff (K)
Rs    = 1.      # star radius in solar radii

# Planetary system params
d    = 10.     # distance to system (pc)  - SLIDER 
Nez  = 3.      # number of exo-zodis  - SLIDER

# Instrumental Params
owa = 30. #OWA scaling factor - SLIDER
iwa = 2. #IWA scaling factor - SLIDER
De_UV = 1e-4 #dark current
De_VIS = 1e-4
De_NIR = 2e-3
Re_UV = 0. #read noise
Re_VIS = 0.
Re_NIR = 0.018
Dtmax = 0.03 # max single exposure time - SLIDER
wantsnr = 10. #for exposure time calculator - SLIDER

# Template
template = ''
global template
global comparison
global Teff
global Ts
global stargalaxy
global spec
stargalaxy = 'false'

################################
# READ-IN DATA

# Read-in Earth spectrum file to start 

fn = 'earth_quadrature_radiance_refl.dat'
fn = os.path.join(relpath, fn)
model = np.loadtxt(fn, skiprows=8)
lamhr = model[:,0]
radhr = model[:,1]
solhr = model[:,2]
# Calculate hi-resolution reflectivity
Ahr   = np.pi*(np.pi*radhr/solhr)
solhr = cg.noise_routines.Fstar(lamhr, Teff, Rs, r, AU=True) # stellar flux blackbody for comparison
lammin = 0.2
lammax = 3.
planet_label = ['']
Planet = ['Planet']
Exozodi=['Exozodi']
Zodi=['Zodi']
Speckles=['Speckles']
Dark_noise=['Dark Noise']
Read_noise=['Read noise']
Thermal_noise=['Thermal noise']
all_astro=['All astro sources']
all_noise=['All sources']

Ahr_ = Ahr
lamhr_ = lamhr
solhr_ = solhr
Teff_ = Teff
Rs_ = Rs


################################
# RUN CORONAGRAPH MODEL
################################

# Run coronagraph with default LUVOIR telescope 
lam, dlam, A, q, Cratio, cp, csp, cz, cez, cD, cR, cth, DtSNR = \
    cg.count_rates(Ahr, lamhr, solhr, alpha,  Rp, Teff, Rs, r, d, Nez, lammin=lammin, lammax=lammax, Res=Res, Res_UV = Res_UV, Res_NIR = Res_NIR, diam=diam, Tsys=Tsys, IWA=iwa, OWA=owa,De_UV=De_UV, De_VIS=De_VIS, De_NIR=De_NIR, Re_UV=Re_UV, Re_VIS=Re_VIS, Re_NIR=Re_NIR, Dtmax=Dtmax, GROUND=False, THERMAL=True,  wantsnr=wantsnr)
#arg



# Calculate background photon count rates
cb = (cz + cez + csp + cD + cR + cth)
# Convert hours to seconds
Dts = Dt * 3600.
# Calculate signal-to-noise assuming background subtraction (the "2")
SNR  = cp*Dts/np.sqrt((cp + 2*cb)*Dts)
# Calculate 1-sigma errors
sig= Cratio/SNR
# Add gaussian noise to flux ratio
spec = Cratio + np.random.randn(len(Cratio))*sig

#update params
lastlam = lam
lastCratio = Cratio
snr_ymax_ = np.max(Cratio)*1e9
yrange=[snr_ymax_]
snr_ymin_ = np.min(Cratio)*1e9
lamC = lastlam * 0.
CratioC = lastCratio * 0.
global lamC
global CratioC

#blank bandpasses
x_uv = [0,0,0,0,0,0]
y_uv = [0,0,0,0,0,0]
x_vis = [0,0,0,0,0,0]
y_vis = [0,0,0,0,0,0]
x_nir = [0,0,0,0,0,0,0,0]
y_nir = [0,0,0,0,0,0,0,0]
x_uvwidth = [0,0,0,0,0,0]
x_viswidth = [0,0,0,0,0,0]
x_nirwidth = [0,0,0,0,0,0,0,0]


#data
planet = ColumnDataSource(data=dict(lam=lam, cratio=Cratio*1e9, spec=spec*1e9, downerr=(spec-sig)*1e9, uperr=(spec+sig)*1e9, cz=cz*Dts, cez=cez*Dts, csp=csp*Dts, cD=cD*Dts, cR=cR*Dts, cth=cth*Dts, cp=cp*Dts, planetrate=cp, czrate=cz, cezrate=cez, csprate=csp, cDrate=cD, cRrate=cR, ctherm=cth, castro=cp+cz+cez+csp, ctotal=cp+cz+cez+csp+cD+cR+cth))
expplanet = ColumnDataSource(data=dict(lam=lam[np.isfinite(DtSNR)], DtSNR=DtSNR[np.isfinite(DtSNR)])) 
plotyrange = ColumnDataSource(data = dict(yrange=yrange))
compare = ColumnDataSource(data=dict(lam=lamC, cratio=Cratio*1e9)) 
expcompare = ColumnDataSource(data=dict(lam=lam[np.isfinite(DtSNR)], DtSNR=DtSNR[np.isfinite(DtSNR)]*(-1000000))) #to make it not show up
textlabel = ColumnDataSource(data=dict(label = planet_label, Planet=Planet, Exozodi=Exozodi, Zodi=Zodi, Speckles=Speckles, Dark_noise=Dark_noise, Read_noise=Read_noise, Thermal_noise=Thermal_noise,  all_astro=all_astro, all_noise=all_noise))
uv_bandpasses = ColumnDataSource(data=dict(x=x_uv, y=y_uv, width=x_uvwidth))
vis_bandpasses = ColumnDataSource(data=dict(x=x_vis, y=y_vis, width=x_viswidth))
nir_bandpasses = ColumnDataSource(data=dict(x=x_nir, y=y_nir, width=x_nirwidth))



################################
# BOKEH PLOTTING
################################
#plots spectrum and exposure time
snr_plot = Figure(plot_height=500, plot_width=1000, 
                  tools="crosshair,pan,reset,resize,save,box_zoom,wheel_zoom,hover",
                  toolbar_location='right', x_range=[0.2, 3.0], y_range=[0, 0.2])

exp_plot = Figure(plot_height=500, plot_width=1000, 
                  tools="crosshair,pan,reset,resize,save,box_zoom,wheel_zoom,hover",
                  toolbar_location='right', x_range=[0.2, 3.0], y_range=[1e-3, 1e10],
                  y_axis_type="log")

counts_plot = Figure(plot_height=500, plot_width=1000, 
                  tools="crosshair,pan,reset,resize,save,box_zoom,wheel_zoom,hover",
                  toolbar_location='right', x_range=[0.2, 3.0], y_range=[1e-3, 1e6],
                  y_axis_type="log")

snr_plot.background_fill_color = "white"
snr_plot.background_fill_alpha = 0.5
snr_plot.yaxis.axis_label='F_p/F_s (x10^9)' 
snr_plot.xaxis.axis_label='Wavelength [micron]'
snr_plot.title.text = 'Planet Spectrum: Earth' #initial spectrum is Earth
snr_plot.xgrid.grid_line_color = None
snr_plot.ygrid.grid_line_color = None

exp_plot.background_fill_color = "white"
exp_plot.background_fill_alpha = 0.5
exp_plot.yaxis.axis_label='Integration time for SNR = 10 [hours]' 
exp_plot.xaxis.axis_label='Wavelength [micron]'
exp_plot.title.text = 'Planet Spectrum: Earth' #initial spectrum is Earth

counts_plot.background_fill_color = "white"
counts_plot.background_fill_alpha = 0.5
counts_plot.yaxis.axis_label='Counts [photons/sec]' 
counts_plot.xaxis.axis_label='Wavelength [micron]'
counts_plot.title.text = 'Count rates' #initial spectrum is Earth

snr_plot.line('lam','cratio',source=compare,line_width=4.0, color="navy", alpha=0.7)
snr_plot.line('lam','cratio',source=planet,line_width=4.0, color="LightBlue", alpha=0.7)
snr_plot.circle('lam', 'spec', source=planet, fill_color='Gold', line_color='black', size=8) 
snr_plot.segment('lam', 'downerr', 'lam', 'uperr', source=planet, line_width=2, line_color='LightGrey', line_alpha=0.5)

exp_plot.line('lam','DtSNR',source=expcompare,line_width=2.0, color="navy", alpha=0.7) #arg
exp_plot.line('lam','DtSNR',source=expplanet,line_width=2.0, color="darkgreen", alpha=0.7)

counts_plot.line('lam','planetrate',source=planet,line_width=2.0, color="navy", alpha=0.7)
counts_plot.line('lam','cezrate',source=planet,line_width=2.0, color="green", alpha=0.7)
counts_plot.line('lam','czrate',source=planet,line_width=2.0, color="purple", alpha=0.7)
counts_plot.line('lam','csprate',source=planet,line_width=2.0, color="red", alpha=0.7)
counts_plot.line('lam', 'cDrate',source=planet,line_width=2.0, color="cyan", alpha=0.7)
counts_plot.line('lam', 'cRrate',source=planet,line_width=2.0, color="magenta", alpha=0.7)
counts_plot.line('lam', 'ctherm',source=planet,line_width=2.0, color="brown", alpha=0.7)
counts_plot.line('lam', 'castro',source=planet,line_width=2.0, color="orange", alpha=0.7)
counts_plot.line('lam','ctotal',source=planet,line_width=2.0, color="black", alpha=0.7)
#add labels
glyph1= Text(x=0.5, y=3e5, text="Planet", text_font_size='9pt', text_font_style='bold', text_color='navy')
glyph2= Text(x=0.5, y=1e5, text="Exozodi", text_font_size='9pt', text_font_style='bold', text_color='green')
glyph3= Text(x=0.5, y=3e4, text="Zodi", text_font_size='9pt', text_font_style='bold', text_color='purple')
glyph4= Text(x=0.5, y=1e4, text="Speckles", text_font_size='9pt', text_font_style='bold', text_color='red')
glyph5= Text(x=0.5, y=3e3, text="Dark_noise", text_font_size='9pt', text_font_style='bold', text_color='cyan')
glyph6= Text(x=0.5, y=1e3, text="Read_noise", text_font_size='9pt', text_font_style='bold', text_color='magenta')
glyph7= Text(x=0.5, y=3e2, text="Thermal_noise", text_font_size='9pt', text_font_style='bold', text_color='brown')
glyph8= Text(x=0.5, y=1e2, text="all_astro", text_font_size='9pt', text_font_style='bold', text_color='orange')
glyph9= Text(x=0.5, y=3e1, text="all_noise", text_font_size='9pt', text_font_style='bold', text_color='black')
counts_plot.add_glyph(textlabel, glyph1)
counts_plot.add_glyph(textlabel, glyph2)
counts_plot.add_glyph(textlabel, glyph3)
counts_plot.add_glyph(textlabel, glyph4)
counts_plot.add_glyph(textlabel, glyph5)
counts_plot.add_glyph(textlabel, glyph6)
counts_plot.add_glyph(textlabel, glyph7)
counts_plot.add_glyph(textlabel, glyph8)
counts_plot.add_glyph(textlabel, glyph9)


#text on plot
glyph = Text(x=0.25, y=snr_ymin_*0.95, text="label", text_font_size='9pt', text_font_style='bold', text_color='blue')
#attempting to outline the text here for ease of visibility... 
glyph2 = Text(x=0.245, y=snr_ymin_*0.95, text="label", text_font_size='9pt', text_font_style='bold', text_color='white')
glyph3 = Text(x=0.25, y=snr_ymin_*0.935, text="label", text_font_size='9pt', text_font_style='bold', text_color='white')
glyph4 = Text(x=0.25, y=snr_ymin_*0.965, text="label", text_font_size='9pt', text_font_style='bold', text_color='white')
glyph5 = Text(x=0.255, y=snr_ymin_*0.95, text="label", text_font_size='9pt', text_font_style='bold', text_color='white')
snr_plot.add_glyph(textlabel, glyph2)
snr_plot.add_glyph(textlabel, glyph3)
snr_plot.add_glyph(textlabel, glyph4)
snr_plot.add_glyph(textlabel, glyph5)
snr_plot.add_glyph(textlabel, glyph)

#add bandpasses

#UV:
uv_rect = Rect(x='x',
            y='y',
            width='width',
            height=200,
            fill_alpha=0.3,
            fill_color="#cc33ff")
uv_rect1 = Rect(x='x',
            y='y',
            width='width',
            height=1e22,
            fill_alpha=0.3,
            fill_color="#cc33ff")
snr_plot.add_glyph(uv_bandpasses, uv_rect)
exp_plot.add_glyph(uv_bandpasses, uv_rect1)

#Vis:
vis_rect = Rect(x='x',
            y='y',
            width='width',
            height=200,
            fill_alpha=0.3,
            fill_color="#66ff99")
vis_rect1 = Rect(x='x',
            y='y',
            width='width',
            height=1e22,
            fill_alpha=0.3,
            fill_color="#66ff99")
snr_plot.add_glyph(vis_bandpasses, vis_rect)
exp_plot.add_glyph(vis_bandpasses, vis_rect1)
    
#NIR:
nir_rect = Rect(x='x',
            y='y',
            width='width',
            height=200,
            fill_alpha=0.3,
            fill_color= "#ff0066")
nir_rect1 = Rect(x='x',
            y='y',
            width='width',
            height=1e22,
            fill_alpha=0.3,
            fill_color= "#ff0066")
snr_plot.add_glyph(nir_bandpasses, nir_rect)
exp_plot.add_glyph(nir_bandpasses, nir_rect1)

#hovertool
hover = snr_plot.select(dict(type=HoverTool))
lam_A = lam * 10000.
global lam_A
hover.tooltips = [
   ('planet', '@cp{int}'),
   ('wavelength', '@lam microns'),
   ('zodi', '@cz{int}'),
   ('exozodi', '@cez{int}'),
   ('dark current', '@cD{int}'),
   ('read noise', '@cR{int}'),
   ('speckle noise', '@csp{int}'),
   ('thermal', '@cth{int}')
]

ptab1 = Panel(child=snr_plot, title='Spectrum')
ptab2 = Panel(child=exp_plot, title='Exposure Time')
ptab3 = Panel(child=counts_plot, title='Count Rates')

ptabs = Tabs(tabs=[ptab1, ptab2, ptab3])
show(ptabs)

################################
#  PROGRAMS
################################

def change_filename(attrname, old, new): 
   format_button_group.active = None 


instruction0 = Div(text="""Specify a filename here:
                           (no special characters):""", width=300, height=15)
text_input = TextInput(value="filename", title=" ", width=100)
instruction1 = Div(text="""Then choose a file format here:""", width=300, height=15)
format_button_group = RadioButtonGroup(labels=["txt", "fits"])
instruction2 = Div(text="""The link to download your file will appear here:""", width=300, height=15)
link_box  = Div(text=""" """, width=300, height=15)


def i_clicked_a_button(new): 
    filename=text_input.value + {0:'.txt', 1:'.fits'}[format_button_group.active]
    print "Your format is   ", format_button_group.active, {0:'txt', 1:'fits'}[format_button_group.active] 
    print "Your filename is: ", filename 
    fileformat={0:'txt', 1:'fits'}[format_button_group.active]
    link_box.text = """Working""" 
 
    t = Table(planet.data)
    t = t['lam', 'spec','cratio','uperr','downerr'] 

    if (format_button_group.active == 1): t.write(filename, overwrite=True) 
    if (format_button_group.active == 0): ascii.write(t, filename)
 
    os.system('gzip -f ' +filename) 
    os.system('cp -rp '+filename+'.gz /home/jtastro/jt-astro.science/outputs') 
    print    """Your file is <a href='http://jt-astro.science/outputs/"""+filename+""".gz'>"""+filename+""".gz</a>. """

    link_box.text = """Your file is <a href='http://jt-astro.science/outputs/"""+filename+""".gz'>"""+filename+""".gz</a>. """


#########################################
# GET DATA FROM USER AND UPDATE PLOT
#########################################

def update_data(attrname, old, new):
    print 'Updating model for exptime = ', exptime.value, ' for planet with R = ', radius.value, ' at distance ', distance.value, ' parsec '
    print '                   exozodi = ', exozodi.value, 'diameter (m) = ', diameter.value, 'resolution = ', resolution.value, 'resolution uv =', resolution_UV.value, 'resolution nir =', resolution_NIR.value,
    print '                   temperature (K) = ', temperature.value, 'IWA = ', inner.value, 'OWA = ', outer.value
    print 'You have chosen planet spectrum: ', template.value
    print 'You have chosen comparison spectrum: ', comparison.value
    try:
       lasttemplate
    except NameError:
       lasttemplate = 'Earth' #default first spectrum
    try:
       lastcomparison
    except NameError:
       lastcomparison = 'none' #default first spectrum
    global lasttemplate
    global Ahr_
    global lamhr_
    global solhr_
    global Teff_
    global Rs_
    global Ahr_c
    global lamhr_c
    global solhr_c
    global Teff_c
    global Rs_c
    global radius_c
    global semimajor_c
    global lastcomparison
    stargalaxy = 'false'

    #if user has selected specific telscope, update parameters
    #note collect_area is currently a hidden variable...
    collect_area = -1 #set if user has not specified a given architecture
    if observatory.value == 'LUVOIR 15 m':
       diameter.value = 12.7
       collect_area = 137.
       ntherm.value = 13.
       temperature.value = 270.
       resolution_UV.value = 10.
    if observatory.value == 'LUVOIR 9 m':
       diameter.value = 7.6
       collect_area = 49.7 #this is wrong. update when know right value.
       ntherm.value = 13.
       temperature.value = 270.
       resolution_UV.value = 10.
    
# Read-in new spectrum file only if changed
    if template.value != lasttemplate:
       if template.value == 'Earth':
          fn = 'earth_quadrature_radiance_refl.dat'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=8)
          lamhr_ = model[:,0]
          radhr_ = model[:,1]
          solhr_ = model[:,2]
          Ahr_   = np.pi*(np.pi*radhr_/solhr_)
          semimajor.value = 1.
          radius.value = 1.
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr, Teff, Rs, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by T. Robinson (Robinson et al. 2011)']


       if template.value == 'Venus':
          fn = 'new_venus.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Fhr_ = model[:,3]
          solhr_ = model[:,2]
          Ahr_ = (Fhr_/solhr_) 
          lamhr_ = lamhr_[::-1]
          Ahr_ = Ahr_[::-1]
          semimajor.value = 0.72
          radius.value = 0.94
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by G. Arney']


       if template.value =='Archean Earth':
          fn = 'ArcheanEarth_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=8)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          semimajor.value = 1.
          radius.value = 1.
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']
          
       if template.value =='Hazy Archean Earth':
          fn = 'Hazy_ArcheanEarth_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          print fn
          model = np.loadtxt(fn, skiprows=8)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          semimajor.value = 1.
          radius.value = 1.
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']


       if template.value =='1% PAL O2 Proterozoic Earth':
          fn = 'proterozoic_hi_o2_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          print fn
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          semimajor.value = 1.
          radius.value = 1.
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']
          

       if template.value =='0.1% PAL O2 Proterozoic Earth':
          fn = 'proterozoic_low_o2_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          semimajor.value = 1.
          radius.value = 1.
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']

          
       if template.value =='Early Mars':
          fn = 'EarlyMars_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=8)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          semimajor.value = 1.52
          radius.value = 0.53
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by G. Arney based on Smith et al. 2014']

          
       if template.value =='Mars':
          fn = 'Mars_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=8)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          semimajor.value = 1.52
          radius.value = 0.53         
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by T. Robinson']

          
       if template.value =='Jupiter':
          fn = 'Jupiter_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          semimajor.value = 5.46
          radius.value = 10.97
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']

          
       if template.value =='Saturn':
          fn = 'Saturn_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          semimajor.value = 9.55
          radius.value = 9.14
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']

          
       if template.value =='Uranus':
          fn = 'Uranus_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          semimajor.value = 19.21
          radius.value = 3.98
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']

          
       if template.value =='Neptune':
          fn = 'Neptune_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          semimajor.value = 29.8
          radius.value = 3.86
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']

       if template.value =='Warm Neptune at 2 AU':
          fn = 'Reflection_a2_m1.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          lamhr_ = lamhr_ / 1000. #convert to microns
          Ahr_ = Ahr_ * 0.67 #convert to geometric albedo
          semimajor.value = 2.0
          radius.value = 3.86
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by R. Hu (Hu and Seager 2014)']

       if template.value =='Warm Neptune w/o Clouds at 1 AU':
          fn = 'Reflection_a1_m2.6_LM_NoCloud.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          lamhr_ = lamhr_ / 1000. #convert to microns
          Ahr_ = Ahr_ * 0.67 #convert to geometric albedo
          semimajor.value = 1.0
          radius.value = 3.86
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by R. Hu (Hu and Seager 2014)']
          
       if template.value =='Warm Neptune w/ Clouds at 1 AU':
          fn = 'Reflection_a1_m2.6_LM.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          lamhr_ = lamhr_ / 1000. #convert to microns
          Ahr_ = Ahr_ * 0.67 #convert to geometric albedo
          semimajor.value = 1.0
          radius.value = 3.86
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by R. Hu']

       if template.value =='Warm Jupiter at 0.8 AU':
          fn = '0.8AU_3x.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,1]
          Ahr_ = model[:,3]
          semimajor.value = 0.8
          radius.value = 10.97
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by K. Cahoy (Cahoy et al. 2010)']

       if template.value =='Warm Jupiter at 2 AU':
          fn = '2AU_3x.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,1]
          Ahr_ = model[:,3]
          semimajor.value = 2.0
          radius.value = 10.97
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by K. Cahoy (Cahoy et al. 2010)']             
          
       if template.value =='False O2 Planet (F2V star)':
          fn = 'fstarcloudy_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          semimajor.value = 1.72 #Earth equivalent distance for F star
          radius.value = 1.
          Teff_  = 7050.   # F2V Teff (K)
          Rs_    = 1.3     # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by S. Domagal-Goldman (Domagal-Goldman et al. 2014)']


       if template.value =='Proxima Cen b 10 bar 95% O2 dry':
          fn = 'Proxima15_o2lb_10bar_dry.pt_filtered_hitran2012_50_100000cm_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,0]
          solhr_ = model[:,2]
          Flx_ = model[:,3]
          Ahr_ = Flx_/solhr_
          lamhr_ = lamhr_[::-1]
          Ahr_ = Ahr_[::-1]
          semimajor.value = 0.048
          radius.value = 1.
          distance.value = 1.3
          Teff_  = 3040.   # Sun-like Teff (K)
          Rs_    = 0.141      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by E. Schwieterman (Meadows et al. 2016)']

          
       if template.value =='Proxima Cen b 10 bar 95% O2 wet':
          fn = 'Proxima15_o2lb_10bar_h2o.pt_filtered_hitran2012_50_100000cm_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,0]
          solhr_ = model[:,2]
          Flx_ = model[:,3]
          Ahr_ = Flx_/solhr_
          lamhr_ = lamhr_[::-1]
          Ahr_ = Ahr_[::-1]
          semimajor.value = 0.048
          radius.value = 1.
          distance.value=1.3
          Teff_  = 3040.   # Sun-like Teff (K)
          Rs_    = 0.141      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by E. Schwieterman (Meadows et al. 2016)']

       if template.value =='Proxima Cen b 10 bar O2-CO2':
          fn = 'Proxima16_O2_CO2_10bar_prox_hitran2012_50_100000cm_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,0]
          solhr_ = model[:,2]
          Flx_ = model[:,3]
          Ahr_ = Flx_/solhr_
          lamhr_ = lamhr_[::-1]
          Ahr_ = Ahr_[::-1]
          semimajor.value = 0.048
          radius.value = 1.
          distance.value = 1.3
          Teff_  = 3040.   # Sun-like Teff (K)
          Rs_    = 0.141      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by E. Schwieterman (Meadows et al. 2016)']

       if template.value =='Proxima Cen b 90 bar O2-CO2':
          fn = 'Proxima16_O2_CO2_90bar_prox_hitran2012_50_100000cm_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,0]
          solhr_ = model[:,2]
          Flx_ = model[:,3]
          Ahr_ = Flx_/solhr_
          lamhr_ = lamhr_[::-1]
          Ahr_ = Ahr_[::-1]
          semimajor.value = 0.048
          radius.value = 1.
          distance.value = 1.3
          Teff_  = 3040.   # Sun-like Teff (K)
          Rs_    = 0.141      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by E. Schwieterman (Meadows et al. 2016)']

       if template.value =='Proxima Cen b 90 bar Venus':
          fn = 'Proxima17_smart_spectra_Venus90bar_clouds_500_100000cm-1_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,0]
          solhr_ = model[:,2]
          Flx_ = model[:,3]
          Ahr_ = Flx_/solhr_
          lamhr_ = lamhr_[::-1]
          Ahr_ = Ahr_[::-1]
          semimajor.value = 0.048
          radius.value = 1.
          distance.value = 1.3
          Teff_  = 3040.   # Sun-like Teff (K)
          Rs_    = 0.141      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by G. Arney (Meadows et al. 2016)']

       if template.value =='Proxima Cen b 10 bar Venus':
          fn = 'Proxima17_smart_spectra_Venus10bar_cloudy_500_100000cm-1_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,0]
          solhr_ = model[:,2]
          Flx_ = model[:,3]
          Ahr_ = Flx_/solhr_
          lamhr_ = lamhr_[::-1]
          Ahr_ = Ahr_[::-1]
          semimajor.value = 0.048
          radius.value = 1.
          distance.value = 1.3
          Teff_  = 3040.   # Sun-like Teff (K)
          Rs_    = 0.141      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by G. Arney (Meadows et al. 2016)']

       if template.value =='Proxima Cen b CO2/CO/O2 dry':
          fn = 'Proxima18_gao_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,0]
          solhr_ = model[:,2]
          Flx_ = model[:,3]
          Ahr_ = Flx_/solhr_
          lamhr_ = lamhr_[::-1]
          Ahr_ = Ahr_[::-1]
          semimajor.value = 0.048
          radius.value = 1.
          distance.value = 1.3
          Teff_  = 3040.   # Sun-like Teff (K)
          Rs_    = 0.141      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by E. Schwieterman based on work by P. Gao (Meadows et al. 2016; Gao et al. 2015)']            

       if template.value =='Proxima Cen b Earth':
          # this one needs a weighted average
          fn = 'Proxima19_earth_prox.pt_stratocum_hitran2012_50_100000cm_toa.rad'
          fn1 = 'Proxima19_earth_prox.pt_filtered_hitran2012_50_100000cm_toa.rad'
          fn2 = 'Proxima19_earth_prox.pt_stratocum_hitran2012_50_100000cm_toa.rad'
          fn = os.path.join(relpath, fn)
          fn1 = os.path.join(relpath, fn1)
          fn2 = os.path.join(relpath, fn2)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,0]
          solhr_ = model[:,2]
          Flx_ = model[:,3]
          model1 = np.loadtxt(fn1, skiprows=1)
          lamhr_1 = model1[:,0]
          solhr_1 = model1[:,2]
          Flx_1 = model1[:,3]
          model2 = np.loadtxt(fn2, skiprows=1)
          lamhr_2 = model2[:,0]
          solhr_2 = model2[:,2]
          Flx_2 = model2[:,3]
          Ahr_ = Flx_/solhr_
          Ahr_1 = Flx_1/solhr_1
          Ahr_2 = Flx_2/solhr_2
          Ahr_ = (Ahr_*0.25+Ahr_2*0.25+Ahr_1*0.5)
          lamhr_ = lamhr_[::-1]
          Ahr_ = Ahr_[::-1]
          semimajor.value = 0.048
          radius.value = 1.
          distance.value = 1.3
          Teff_  = 3040.   # Sun-like Teff (K)
          Rs_    = 0.141      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by E. Schwieterman (Meadows et al. 2016)']  

       if template.value =='Proxima Cen b Archean Earth':
          fn = 'Proxima21_HAZE_msun21_0.0Ga_1.00e-02ch4_rmix_5.0E-2__30.66fscale_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,0]
          solhr_ = model[:,2]
          Flx_ = model[:,3]
          Ahr_ = Flx_/solhr_
          lamhr_ = lamhr_[::-1]
          Ahr_ = Ahr_[::-1]
          semimajor.value = 0.048
          radius.value = 1.
          distance.value = 1.3
          Teff_  = 3040.   # Sun-like Teff (K)
          Rs_    = 0.141      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by G. Arney (Meadows et al. 2016)']           

       if template.value =='Proxima Cen b hazy Archean Earth':
          fn = 'Proxima21_HAZE_msun21_0.0Ga_3.00e-02ch4_rmix_5.0E-2__30.66fscale_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_ = model[:,0]
          solhr_ = model[:,2]
          Flx_ = model[:,3]
          Ahr_ = Flx_/solhr_
          lamhr_ = lamhr_[::-1]
          Ahr_ = Ahr_[::-1]
          semimajor.value = 0.048
          radius.value = 1.
          distance.value = 1.3
          Teff_  = 3040.   # Sun-like Teff (K)
          Rs_    = 0.141      # star radius in solar radii
          solhr_ =  cg.noise_routines.Fstar(lamhr_, Teff_, Rs_, semimajor.value, AU=True)
          planet_label = ['Synthetic spectrum generated by G. Arney (Meadows et al. 2016)']           
          
       global lammin
       global lammax
       global planet_label
       lammin=min(lamhr_)
       if lammin <= 0.2:
          lammin = 0.2
       lammax=3.
          
       planet_label = ['']

    print "ground based = ", ground_based.value
    if ground_based.value == "No":
       ground_based_ = False
    if ground_based.value == "Yes":
       ground_based_ = True
    
    # Run coronagraph 
    lam, dlam, A, q, Cratio, cp, csp, cz, cez, cD, cR, cth, DtSNR = \
        cg.count_rates(Ahr_, lamhr_, solhr_, alpha,  radius.value, Teff_, Rs_, semimajor.value, distance.value, exozodi.value, diam=diameter.value, collect_area=collect_area, Res=resolution.value, Res_UV = resolution_UV.value, Res_NIR = resolution_NIR.value, Tsys=temperature.value, IWA=inner.value, OWA=outer.value, lammin=lammin, lammax=lammax, De_UV=De_UV, De_VIS=De_VIS, De_NIR=De_NIR, Re_UV=Re_UV, Re_VIS=Re_VIS, Re_NIR=Re_NIR, Dtmax = dtmax.value, THERMAL=True, GROUND=ground_based_, wantsnr=want_snr.value, ntherm=ntherm.value, gain=gain.value)


    # Calculate background photon count rates
    cb = (cz + cez + csp + cD + cR + cth)
    # Convert hours to seconds
    Dts = exptime.value * 3600.
    # Calculate signal-to-noise assuming background subtraction (the "2")
    SNR  = cp*Dts/np.sqrt((cp + 2*cb)*Dts)
    # Calculate 1-sigma errors
    sig= Cratio/SNR
    # Add gaussian noise to flux ratio
    spec = Cratio + np.random.randn(len(Cratio))*sig
    lastlam = lam
    lastCratio = Cratio
    global lastlam
    global lastCratio
    planet_label = ['']
    
    #UPDATE DATA
    planet.data = dict(lam=lam, cratio=Cratio*1e9, spec=spec*1e9, downerr=(spec-sig)*1e9, uperr=(spec+sig)*1e9, cz=cz*Dts, cez=cez*Dts, csp=csp*Dts, cD=cD*Dts, cR=cR*Dts, cth=cth*Dts, cp=cp*Dts, planetrate=cp, czrate=cz, cezrate=cez, csprate=csp, cDrate=cD, cRrate=cR, castro=cp+cz+cez+csp, ctherm=cth, ctotal=cp+cz+cez+csp+cD+cR+cth)
    expplanet.data = dict(lam=lam[np.isfinite(DtSNR)], DtSNR=DtSNR[np.isfinite(DtSNR)])
     #make the data the time for a given SNR if user wants this:
    textlabel.data = dict(label=planet_label, Planet=Planet, Exozodi=Exozodi, Zodi=Zodi, Speckles=Speckles, Dark_noise=Dark_noise, Read_noise=Read_noise, Thermal_noise=Thermal_noise,  all_astro=all_astro, all_noise=all_noise)
    if bandpass.value == "No":
       x_uv = [0,0,0,0,0,0]
       y_uv = [0,0,0,0,0,0]
       x_vis = [0,0,0,0,0,0]
       y_vis = [0,0,0,0,0,0]
       x_nir = [0,0,0,0,0,0,0,0]
       y_nir = [0,0,0,0,0,0,0,0]
       x_uvwidth = [0,0,0,0,0,0]
       x_viswidth = [0,0,0,0,0,0]
       x_nirwidth = [0,0,0,0,0,0,0,0]

       uv_bandpasses.data = dict(x=x_uv, y=y_uv, width=x_uvwidth)
       vis_bandpasses.data = dict(x=x_vis, y=y_vis, width=x_viswidth)
       nir_bandpasses.data = dict(x=x_nir, y=y_nir, width=x_nirwidth)

       print 'no bandpasses'
     #  print x_uvwidth

    if bandpass.value == "Yes":
       x_vis1 = [0.41, 0.44, 0.525, 0.565, 0.675]
       x_vis2 = [0.45, 0.535, 0.575, 0.685, 0.820]
       sum = [a + b for a, b in zip(x_vis2, x_vis1)] 
       x_vis = [0,0,0,0,0]
       x_vis = [x * 0.5 for x in sum]
       x_viswidth = [a - b for a, b in zip(x_vis2, x_vis1)] 
       #x_vis2 - x_vis1
       
       x_nir1 = [0.820, 0.890, 1.0, 1.09, 1.31, 1.5]
       x_nir2 = [0.94, 1.07, 1.1, 1.32, 1.58, 1.8]
       sum = [a + b for a, b in zip(x_nir2, x_nir1)] 
       x_nir = [0,0,0,0,0,0]
       x_nir = [x * 0.5 for x in sum]
       x_nirwidth = [a - b for a, b in zip(x_nir2, x_nir1)] 
      # x_nirwidth = x_nir2 - x_nir1

       #import pdb; pdb.set_trace()
       x_uv1=[0.220]
       x_uv2=[0.41]
       sum = [a + b for a, b in zip(x_uv2, x_uv1)] 
       y_uv = [0]
       x_uv = [x * 0.5 for x in sum]
       x_uvwidth = [a - b for a, b in zip(x_uv2, x_uv1)] 
       #x_vis=[0.445, 0.510, 0.590, 0.670, 0.755, 0.825]
       y_vis = [0,0,0,0,0,0]
       y_uv = [0]
      # x_nir=[0.880, 0.985, 1.105, 1.240, 1.390, 1.580, 1.740]       
       y_nir = [0,0,0,0,0,0,0,0]
       #x_uvwidth=[0.03, 0.04, 0.04, 0.05, 0.05, 0.06]
      # x_viswidth = [.070, .080, .100 ,  .080 , .110, .05]
      # x_nirwidth = [.120 , .110 , .150  ,  .140 ,  .180  ,  .220 , .120]
      # x_uv=[0.220, 0.240, 0.270, 0.305, 0.345, 0.390]
      # y_uv = [0,0,0,0,0,0]
      # x_vis=[0.445, 0.510, 0.590, 0.670, 0.755, 0.825]
      # y_vis = [0,0,0,0,0,0]
      # x_nir=[0.890, 0.980, 1.105, 1.240, 1.390, 1.580, 1.740]       
      # y_nir = [0,0,0,0,0,0,0,0]
      # x_uvwidth=[0.03, 0.04, 0.04, 0.05, 0.05, 0.06]
      # x_viswidth = [.070, .080, .100 ,  .080 , .110, .05]
      # x_nirwidth = [.080 , .120 , .150  ,  .140 ,  .180  ,  .220 , .120]

      
       uv_bandpasses.data = dict(x=x_uv, y=y_uv, width=x_uvwidth)
       vis_bandpasses.data = dict(x=x_vis, y=y_vis, width=x_viswidth)
       nir_bandpasses.data = dict(x=x_nir, y=y_nir, width=x_nirwidth)
       
       print 'yes bandpasses'
      # print x_uvwidth

    #pdb.set_trace()
    format_button_group.active = None
    lasttemplate = template.value
    teststar = False
    if 'star' in comparison.value: teststar = True
    if 'galaxy' in comparison.value: teststar = True
    if 'brown dwarf' in comparison.value: teststar = True

    print 'teststar is', teststar
        
    #IF YOU WANT COMPARISON SPECTRUM:
    if comparison.value != lastcomparison or teststar:
      stargalaxy = 'false'
      
      if comparison.value == 'Earth':
          fn = 'earth_quadrature_radiance_refl.dat'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=8)
          lamhr_c = model[:,0]
          radhr_c = model[:,1]
          solhr_c = model[:,2]
          Ahr_c   = np.pi*(np.pi*radhr_c/solhr_c)
          semimajor_c = 1.
          radius_c = 1.
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by T. Robinson (Robinson et al. 2011)']

      if comparison.value == 'Venus':
          fn = 'new_venus.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_c = model[:,0]
          Fhr_c = model[:,3]
          solhr_c = model[:,2]
          Ahr_c = (Fhr_c/solhr_c)
          lamhr_c = lamhr_c[::-1]
          Ahr_c = Ahr_c[::-1]
          semimajor_c = 0.72
          radius_c = 0.94
          Teff_c = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by G. Arney']

      if comparison.value =='Archean Earth':
          fn = 'ArcheanEarth_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=8)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          semimajor_c = 1.
          radius_c = 1.
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']
          
      if comparison.value =='Hazy Archean Earth':
          fn = 'Hazy_ArcheanEarth_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=8)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          semimajor_c = 1.
          radius_c = 1.
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']


      if comparison.value =='1% PAL O2 Proterozoic Earth':
          fn = 'proterozoic_hi_o2_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          semimajor_c = 1.
          radius_c = 1.
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']
          

      if comparison.value =='0.1% PAL O2 Proterozoic Earth':
          fn = 'proterozoic_low_o2_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          semimajor_c = 1.
          radius_c = 1.
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']

          
      if comparison.value =='Early Mars':
          fn = 'EarlyMars_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=8)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          semimajor_c = 1.52
          radius_c = 0.53
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by G. Arney based on Smith et al. 2014']

          
      if comparison.value =='Mars':
          fn = 'Mars_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=8)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          semimajor_c = 1.52
          radius_c = 0.53         
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by T. Robinson']

          
      if comparison.value =='Jupiter':
          fn = 'Jupiter_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          semimajor_c = 5.46
          radius_c = 10.97
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']

          
      if comparison.value =='Saturn':
          fn = 'Saturn_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          semimajor_c = 9.55
          radius_c = 9.14
          Teff_c = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']

          
      if comparison.value =='Uranus':
          fn = 'Uranus_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          semimajor_c = 19.21
          radius_c = 3.98
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']

          
      if comparison.value =='Neptune':
          fn = 'Neptune_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          semimajor_c = 29.8
          radius_c = 3.86
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']


      if comparison.value =='Warm Neptune at 2 AU':
          fn = 'Reflection_a2_m1.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          lamhr_c = lamhr_c / 1000. #convert to microns
          Ahr_c = Ahr_c * 0.67 #convert to geometric albedo
          semimajor_c = 2.0
          radius_c = 3.86
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by R. Hu (Hu and Seager 2014)']

      if comparison.value =='Warm Neptune w/o Clouds at 1 AU':
          fn = 'Reflection_a1_m2.6_LM_NoCloud.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          lamhr_c = lamhr_c / 1000. #convert to microns
          Ahr_c = Ahr_c* 0.67 #convert to geometric albedo
          semimajor_c = 1.0
          radius_c = 3.86
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by R. Hu (Hu and Seager 2014)']
          
      if comparison.value =='Warm Neptune w/ Clouds at 1 AU':
          fn = 'Reflection_a1_m2.6_LM.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          lamhr_c = lamhr_c / 1000. #convert to microns
          Ahr_c = Ahr_c * 0.67 #convert to geometric albedo
          semimajor_c = 1.0
          radius_c = 3.86
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by R. Hu']

      if comparison.value =='Warm Jupiter at 0.8 AU':
          fn = '0.8AU_3x.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,1]
          Ahr_c = model[:,3]
          semimajor_c = 0.8
          radius_c = 10.97
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by K. Cahoy (Cahoy et al. 2010)']

      if comparison.value =='Warm Jupiter at 2 AU':
          fn = '2AU_3x.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,1]
          Ahr_c = model[:,3]
          semimajor_c = 2.0
          radius_c = 10.97
          Teff_c  = 5780.   # Sun-like Teff (K)
          Rs_c    = 1.      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by K. Cahoy (Cahoy et al. 2010)']              

      if comparison.value =='False O2 Planet (F2V star)':
          fn = 'fstarcloudy_geo_albedo.txt'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=0)
          lamhr_c = model[:,0]
          Ahr_c = model[:,1]
          semimajor_c = 1.72 #Earth equivalent distance for F star
          radius_c = 1.
          Teff_c  = 7050.   # F2V Teff (K)
          Rs_c    = 1.3     # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by S. Domagal-Goldman (Domagal-Goldman et al. 2014)']          

      if comparison.value =='Proxima Cen b 10 bar 95% O2 dry':
          fn = 'Proxima15_o2lb_10bar_dry.pt_filtered_hitran2012_50_100000cm_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,0]
          solhr_c = model[:,2]
          Flx_c = model[:,3]
          Ahr_c = Flx_c/solhr_c
          lamhr_c = lamhr_c[::-1]
          Ahr_c = Ahr_c[::-1]
          semimajor_c = 0.048
          radius_c = 1.
          distance_c = 1.3
          Teff_c  = 3040.   # Sun-like Teff (K)
          Rs_c    = 0.141      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by E. Schwieterman (Meadows et al. 2016)']

          
      if comparison.value =='Proxima Cen b 10 bar 95% O2 wet':
          fn = 'Proxima15_o2lb_10bar_h2o.pt_filtered_hitran2012_50_100000cm_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,0]
          solhr_c = model[:,2]
          Flx_c = model[:,3]
          Ahr_c = Flx_c/solhr_c
          lamhr_c = lamhr_c[::-1]
          Ahr_c = Ahr_c[::-1]
          semimajor_c = 0.048
          radius_c = 1.
          distance_c=1.3
          Teff_c  = 3040.   # Sun-like Teff (K)
          Rs_c    = 0.141      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by E. Schwieterman (Meadows et al. 2016)']

      if comparison.value =='Proxima Cen b 10 bar O2-CO2':
          fn = 'Proxima16_O2_CO2_10bar_prox_hitran2012_50_100000cm_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,0]
          solhr_c = model[:,2]
          Flx_c = model[:,3]
          Ahr_c = Flx_c/solhr_c
          lamhr_c = lamhr_c[::-1]
          Ahr_c = Ahr_c[::-1]
          semimajor_c = 0.048
          radius_c = 1.
          distance_c = 1.3
          Teff_c  = 3040.   # Sun-like Teff (K)
          Rs_c    = 0.141      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by E. Schwieterman (Meadows et al. 2016)']

      if comparison.value =='Proxima Cen b 90 bar O2-CO2':
          fn = 'Proxima16_O2_CO2_90bar_prox_hitran2012_50_100000cm_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,0]
          solhr_c = model[:,2]
          Flx_c = model[:,3]
          Ahr_c = Flx_c/solhr_c
          lamhr_c = lamhr_c[::-1]
          Ahr_c = Ahr_c[::-1]
          semimajor_c = 0.048
          radius_c = 1.
          distance_c = 1.3
          Teff_c  = 3040.   # Sun-like Teff (K)
          Rs_c    = 0.141      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by E. Schwieterman (Meadows et al. 2016)']

      if comparison.value =='Proxima Cen b 90 bar Venus':
          fn = 'Proxima17_smart_spectra_Venus90bar_clouds_500_100000cm-1_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,0]
          solhr_c = model[:,2]
          Flx_c = model[:,3]
          Ahr_c = Flx_c/solhr_c
          lamhr_c = lamhr_c[::-1]
          Ahr_c = Ahr_c[::-1]
          semimajor_c = 0.048
          radius_c = 1.
          distance_c = 1.3
          Teff_c  = 3040.   # Sun-like Teff (K)
          Rs_c    = 0.141      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by G. Arney (Meadows et al. 2016)']

      if comparison.value =='Proxima Cen b 10 bar Venus':
          fn = 'Proxima17_smart_spectra_Venus10bar_cloudy_500_100000cm-1_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,0]
          solhr_c = model[:,2]
          Flx_c = model[:,3]
          Ahr_c = Flx_c/solhr_c
          lamhr_c = lamhr_c[::-1]
          Ahr_c = Ahr_c[::-1]
          semimajor_c = 0.048
          radius_c = 1.
          distance_c = 1.3
          Teff_c  = 3040.   # Sun-like Teff (K)
          Rs_c    = 0.141      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by G. Arney (Meadows et al. 2016)']

      if comparison.value =='Proxima Cen b CO2/CO/O2 dry':
          fn = 'Proxima18_gao_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,0]
          solhr_c = model[:,2]
          Flx_c = model[:,3]
          Ahr_c = Flx_c/solhr_c
          lamhr_c = lamhr_c[::-1]
          Ahr_c = Ahr_c[::-1]
          semimajor_c = 0.048
          radius_c = 1.
          distance_c = 1.3
          Teff_c  = 3040.   # Sun-like Teff (K)
          Rs_c    = 0.141      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by E. Schwieterman (Meadows et al. 2016)']            

      if comparison.value =='Proxima Cen b Earth':
          # this one needs a weighted average
          fn = 'Proxima19_earth_prox.pt_stratocum_hitran2012_50_100000cm_toa.rad'
          fn1 = 'Proxima19_earth_prox.pt_filtered_hitran2012_50_100000cm_toa.rad'
          fn2 = 'Proxima19_earth_prox.pt_stratocum_hitran2012_50_100000cm_toa.rad'
          fn = os.path.join(relpath, fn)
          fn1 = os.path.join(relpath, fn1)
          fn2 = os.path.join(relpath, fn2)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,0]
          solhr_c = model[:,2]
          Flx_c = model[:,3]
          model1 = np.loadtxt(fn1, skiprows=1)
          lamhr_1c = model1[:,0]
          solhr_1c = model1[:,2]
          Flx_1c = model1[:,3]
          model2 = np.loadtxt(fn2, skiprows=1)
          lamhr_2c = model2[:,0]
          solhr_2c = model2[:,2]
          Flx_2c = model2[:,3]
          Ahr_c = Flx_c/solhr_c
          Ahr_1c = Flx_1c/solhr_1c
          Ahr_2c = Flx_2c/solhr_2c
          Ahr_c = (Ahr_c*0.25+Ahr_2c*0.25+Ahr_1c*0.5)
          lamhr_c = lamhr_c[::-1]
          Ahr_c = Ahr_c[::-1]
          semimajor_c = 0.048
          radius_c = 1.
          distance_c = 1.3
          Teff_c  = 3040.   # Sun-like Teff (K)
          Rs_c    = 0.141      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by E. Schwieterman (Meadows et al. 2016)']  

      if comparison.value =='Proxima Cen b Archean Earth':
          fn = 'Proxima21_HAZE_msun21_0.0Ga_1.00e-02ch4_rmix_5.0E-2__30.66fscale_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,0]
          solhr_c = model[:,2]
          Flx_c = model[:,3]
          Ahr_c = Flx_c/solhr_c
          lamhr_c = lamhr_c[::-1]
          Ahr_c = Ahr_c[::-1]
          semimajor_c = 0.048
          radius_c = 1.
          distance_c = 1.3
          Teff_c  = 3040.   # Sun-like Teff (K)
          Rs_c    = 0.141      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by G. Arney (Meadows et al. 2016)']           

      if comparison.value =='Proxima Cen b hazy Archean Earth':
          fn = 'Proxima21_HAZE_msun21_0.0Ga_3.00e-02ch4_rmix_5.0E-2__30.66fscale_toa.rad'
          fn = os.path.join(relpath, fn)
          model = np.loadtxt(fn, skiprows=1)
          lamhr_c = model[:,0]
          solhr_c = model[:,2]
          Flx_c = model[:,3]
          Ahr_c = Flx_c/solhr_c
          lamhr_c = lamhr_c[::-1]
          Ahr_c = Ahr_c[::-1]
          semimajor_c = 0.048
          radius_c = 1.
          distance_c = 1.3
          Teff_c  = 3040.   # Sun-like Teff (K)
          Rs_c    = 0.141      # star radius in solar radii
          solhr_c =  cg.noise_routines.Fstar(lamhr_c, Teff_c, Rs_c, semimajor_c, AU=True)
          planet_label_c = ['Synthetic spectrum generated by G. Arney (Meadows et al. 2016)']

#for now I'm just adding these in like the others to save time on reworkign the code. This will need to be tidied up in future. 


      if comparison.value == 'O5V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_1.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)

      if comparison.value == 'B5V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_6.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)

      if comparison.value == 'A5V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_12.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)

      if comparison.value == 'F5V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_16.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)
          
      if comparison.value == 'G2V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_26.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)

      if comparison.value == 'G5V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_27.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)

      if comparison.value == 'K2V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_33.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)

      if comparison.value == 'K5V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_36.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)

      if comparison.value == 'M0V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_38.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)

      if comparison.value == 'M2V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_40.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)
          
      if comparison.value == 'M4V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_43.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)
          
      if comparison.value == 'M5V star':
          stargalaxy = 'true'
          fn = 'pickles_uk_44.ascii'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=39)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #convert A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)
          
      if comparison.value == 'Proxima Centauri star':
          stargalaxy = 'true'
          fn = 'proxima_cen_sed.txt'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=25)
 #         import pdb; pdb.set_trace()
          lamhr_c = model[:,0]
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)

      if comparison.value == 'T0 brown dwarf':
          stargalaxy = 'true'
          fn = 'T0_SDSS0837m0000_full_fluxed.txt'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=13)
#          import pdb; pdb.set_trace()
          lamhr_c = model[:,0]
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)          

      if comparison.value == 'T9 brown dwarf':
          stargalaxy = 'true'
          fn = 'T9_WISE1741p2553_full_fluxed.txt'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=13)
#          import pdb; pdb.set_trace()
          lamhr_c = model[:,0]
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)               
         
      if comparison.value == 'L5 brown dwarf':
          stargalaxy = 'true'
          fn = 'L5_2MASS1821p1414_full_fluxed.txt'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=13)
#          import pdb; pdb.set_trace()
          lamhr_c = model[:,0]
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)    

      if comparison.value == 'L8 brown dwarf':
          stargalaxy = 'true'
          fn = 'L8_SDSS0857p5708_full_fluxed.txt'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=13)
#          import pdb; pdb.set_trace()
          lamhr_c = model[:,0]
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)    

      if comparison.value == 'NGC 337 spiral galaxy':
          stargalaxy = 'true'
          fn = 'NGC_0337_S_Uv-MIr_bms2014.txt'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=9)
#          import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)  
          
      if comparison.value == 'NGC 660 peculiar galaxy':
          stargalaxy = 'true'
          fn = 'NGC_0660_S_Uv-MIr_bms2014.txt'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=9)
#          import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)  

      if comparison.value == 'NGC 4621 elliptical galaxy':
          stargalaxy = 'true'
          fn = 'NGC_4621_S_Uv-MIr_bms2014.txt'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=9)
#          import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)           

      if comparison.value == 'NGC 5033 spiral galaxy':
          stargalaxy = 'true'
          fn = 'NGC_5033_S_Uv-MIr_bms2014.txt'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=9)
#          import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)

      if comparison.value == 'Haro 6 blue compact dwarf galaxy':
          stargalaxy = 'true'
          fn = 'Haro_06_S_Uv-MIr_bms2014.txt'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=9)
#          import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #A -> um
          Flx_c = model[:,1]
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)   

      if comparison.value == 'NGC 7476 spiral galaxy':
          stargalaxy = 'true'
          fn = 'NGC_7674_S_Uv-MIr_bms2014.txt'
          fn = os.path.join(relpath2, fn)
          model = np.loadtxt(fn, skiprows=9)
#          import pdb; pdb.set_trace()
          lamhr_c = model[:,0]*.0001 #A -> um
          Flx_c = model[:,1] 
          Flx_c = cg.downbin_spec(Flx_c, lamhr_c, lam, dlam)   
          
      global lammin_c
      global lammax_c
      lammin_c=min(lamhr_c)
      if lammin_c <= 0.2:
         lammin_c = 0.2
      lammax_c=3.
              
    print 'stargalaxy is ', stargalaxy
    print 'teststar is', teststar
#    import pdb; pdb.set_trace()
    if comparison.value != 'none' and teststar == False:
      print 'comparison.value =', comparison.value
      print  'running comparison spectrum'
      try:
         distance_c
      except NameError:
         print "running comparison"
         lamC, dlamC, AC, qC, CratioC, cpC, cspC, czC, cezC, cDC, cRC, cthC, DtSNRC = \
                                                                                         cg.count_rates(Ahr_c, lamhr_c, solhr_c, alpha,  radius_c, Teff_c, Rs_c, semimajor_c, distance.value, exozodi.value, diam=diameter.value, collect_area=collect_area, Res=resolution.value, Res_UV = resolution_UV.value, Res_NIR = resolution_NIR.value,Tsys=temperature.value, IWA=inner.value, OWA=outer.value, lammin=lammin, lammax=lammax, De_UV=De_UV, De_VIS=De_VIS, De_NIR=De_NIR, Re_UV=Re_UV, Re_VIS=Re_VIS, Re_NIR=Re_NIR, Dtmax = dtmax.value, THERMAL=True, GROUND=ground_based_, wantsnr=want_snr.value, ntherm=ntherm.value, gain = gain.value)
      else:
         print "running comparison spectrum"
         lamC, dlamC, AC, qC, CratioC, cpC, cspC, czC, cezC, cDC, cRC, cthC, DtSNRC = \
                                                                                         cg.count_rates(Ahr_c, lamhr_c, solhr_c, alpha, radius_c, Teff_c, Rs_c, semimajor_c, distance_c, exozodi.value, diam=diameter.value, collect_area=collect_area, Res=resolution.value, Res_UV = resolution_UV.value, Res_NIR = resolution_NIR.value,Tsys=temperature.value, IWA=inner.value, OWA=outer.value, lammin=lammin, lammax=lammax,De_UV=De_UV, De_VIS=De_VIS, De_NIR=De_NIR, Re_UV=Re_UV, Re_VIS=Re_VIS, Re_NIR=Re_NIR,Dtmax = dtmax.value, THERMAL=True, GROUND=ground_based_, wantsnr=want_snr.value, ntherm=ntherm.value, gain = gain.value)


    if stargalaxy == 'true':
       #check for nans
       nans = np.isnan(Flx_c)
       Flx_c[nans] = np.interp(lam[nans], lam[~nans], Flx_c[~nans])

       #Flx_c = np.nan_to_num(Flx_c)
       maxbright1 = max(Cratio[np.isfinite(Cratio)])
       maxbright2 = max(Flx_c)
       ratio = maxbright1/maxbright2
       CratioC = [x * ratio for x in Flx_c]
       lamC = lam
       DtSNRC = [x * 0. for x in Flx_c]
       CratioC = np.nan_to_num(CratioC)
       DtSNRC = np.nan_to_num(DtSNRC)
       
    if comparison.value == 'none':
       lamC = lamhr_ * 0.
       CratioC = Ahr_ *0.
       DtSNRC = lamhr_ * 0.


    lastcomparison = comparison.value
    #UPDATE DATA
  #  pdb.set_trace()
    compare.data = dict(lam=lamC, cratio=CratioC*1e9)
    expcompare.data = dict(lam=lamC[np.isfinite(DtSNRC)], DtSNR=DtSNRC[np.isfinite(DtSNRC)])
        
    #######PLOT UPDATES#######    
    global snr_ymax_
    global snr_ymin_

    #ii = np.where(lam < 3.) #only want where reflected light, not thermal
    #iii = np.where(lamC < 3.)  #only want where reflected light, not thermal
   
    #Cratio_ok = Cratio[ii]
    #CratioC_ok = CratioC[iii]
    Cratio_ok = Cratio[~np.isnan(Cratio)]
    CratioC_ok = CratioC[~np.isnan(CratioC)]
    print 'snr_ymax_',  np.max([np.max(Cratio_ok)*1e9, np.max(CratioC_ok)*1e9])
    print 'snr_ymin_',  np.min([np.min(Cratio_ok)*1e9, np.min(CratioC_ok)*1e9])
    snr_ymax_ = np.max([np.max(Cratio_ok)*1e9, np.max(CratioC_ok)*1e9])
    snr_ymin_ = np.min([np.min(Cratio_ok)*1e9, np.min(CratioC_ok)*1e9])
    snr_plot.y_range.start = snr_ymin_*0.9

    exp_plot.yaxis.axis_label='Integration time for SNR = '+str(want_snr.value)+' [hours]' 

    
    if comparison.value != 'none':
       snr_plot.title.text = 'Planet Spectrum: '+template.value +' and comparison spectrum '+comparison.value
       exp_plot.title.text = 'Planet Spectrum: '+template.value +' and comparison spectrum '+comparison.value
       
    if comparison.value == 'none':
      snr_plot.title.text = 'Planet Spectrum: '+template.value
      exp_plot.title.text =  'Planet Spectrum: '+template.value

    if template.value == 'Early Mars' or template.value == 'Mars':
       if comparison.value == 'none' or comparison.value == 'Early Mars' or comparison.value == 'Mars':
          snr_plot.y_range.end = snr_ymax_ + 2.*snr_ymax_
    else:
       snr_plot.y_range.end = snr_ymax_ *1.1
      


       
######################################
# SET UP ALL THE WIDGETS AND CALLBACKS 
######################################

source = ColumnDataSource(data=dict(value=[]))
source.on_change('data', update_data)
exptime  = Slider(title="Integration time per bandpass (hours)", value=24., start=0.1, end=1000.0, step=0.1, callback_policy='mouseup')
exptime.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
distance = Slider(title="Distance (parsec)", value=10., start=0.1, end=100.0, step=0.2, callback_policy='mouseup') 
distance.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
radius   = Slider(title="Planet Radius (R_Earth)", value=1.0, start=0.5, end=20., step=0.1, callback_policy='mouseup') 
radius.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
semimajor= Slider(title="Semi-major axis of orbit (AU)", value=1.0, start=0.01, end=20., step=0.01, callback_policy='mouseup') 
semimajor.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
exozodi  = Slider(title="Number of Exozodi", value = 3.0, start=1.0, end=10., step=1., callback_policy='mouseup') 
exozodi.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
diameter  = Slider(title="Mirror Diameter (meters)", value = 12.2, start=0.5, end=50., step=0.1, callback_policy='mouseup') 
diameter.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
resolution  = Slider(title="Telescope Visible Resolution (R)", value = 150.0, start=5.0, end=300., step=1., callback_policy='mouseup') 
resolution.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
resolution_UV  = Slider(title="Telescope UV Resolution (R)", value = 20.0, start=5.0, end=300., step=1., callback_policy='mouseup') 
resolution_UV.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
resolution_NIR  = Slider(title="Telescope NIR Resolution (R)", value = 100.0, start=5.0, end=1000., step=1., callback_policy='mouseup') 
resolution_NIR.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
temperature  = Slider(title="Telescope Temperature (K)", value = 270.0, start=90.0, end=400., step=10., callback_policy='mouseup') 
temperature.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
inner  = Slider(title="Inner Working Angle factor x lambda/D", value = 2.0, start=1.22, end=4., step=0.2, callback_policy='mouseup') 
inner.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
outer  = Slider(title="Outer Working Angle factor x lambda/D", value = 30.0, start=20, end=100., step=1, callback_policy='mouseup') 
outer.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
darkcurrent  = Slider(title="Dark current (counts/s)", value = 1e-4, start=1e-5, end=1e-3, step=1e-5, callback_policy='mouseup') 
darkcurrent.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
readnoise  = Slider(title="Read noise (counts/pixel)", value = 0.1, start=0.01, end=1, step=0.05, callback_policy='mouseup') 
readnoise.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
dtmax  = Slider(title="Maximum single exposure time (hours)", value = 0.3, start=0.0003, end=3, step=0.0001, callback_policy='mouseup') 
dtmax.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
want_snr  = Slider(title="Desired signal-to-noise ratio? (only used for exposure time plot)", value = 10, start=0.5, end=100., step=0.5, callback_policy='mouseup') 
want_snr.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
ntherm  = Slider(title="Number of thermal surfaces:", value = 1, start=1, end=30., step=1, callback_policy='mouseup') 
ntherm.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
gain  = Slider(title="Detector gain:", value = 1, start=1, end=1000., step=5, callback_policy='mouseup') 
gain.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
#ground based choice
ground_based = Select(title="Simulate ground-based observation?", value="No", options=["No",  "Yes"])

#bandpass choice
bandpass = Select(title="Show LUVOIR bandpasses", value="No", options=["No",  "Yes"])

#observatory choice
observatory = Select(title="Simulate specific observatory?", value="No", options=["No",  "LUVOIR 15 m", 'LUVOIR 9 m'])

#select menu for planet
template = Select(title="Planet Spectrum", value="Earth", options=["Earth",  "Archean Earth", "Hazy Archean Earth", "1% PAL O2 Proterozoic Earth", "0.1% PAL O2 Proterozoic Earth","Venus", "Early Mars", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune",'-----','Warm Neptune at 2 AU', 'Warm Neptune w/o Clouds at 1 AU', 'Warm Neptune w/ Clouds at 1 AU','Warm Jupiter at 0.8 AU', 'Warm Jupiter at 2 AU',"False O2 Planet (F2V star)", '-----', 'Proxima Cen b 10 bar 95% O2 dry', 'Proxima Cen b 10 bar 95% O2 wet', 'Proxima Cen b 10 bar O2-CO2', 'Proxima Cen b 90 bar O2-CO2', 'Proxima Cen b 90 bar Venus', 'Proxima Cen b 10 bar Venus', 'Proxima Cen b CO2/CO/O2 dry', 'Proxima Cen b Earth', 'Proxima Cen b Archean Earth', 'Proxima Cen b hazy Archean Earth' ])
#select menu for comparison spectrum
comparison = Select(title="Show comparison spectrum?", value ="none", options=["none", "Earth",  "Archean Earth", "Hazy Archean Earth", "1% PAL O2 Proterozoic Earth", "0.1% PAL O2 Proterozoic Earth","Venus", "Early Mars", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune",'-----','Warm Neptune at 2 AU', 'Warm Neptune w/o Clouds at 1 AU', 'Warm Neptune w/ Clouds at 1 AU','Warm Jupiter at 0.8 AU', 'Warm Jupiter at 2 AU', "False O2 Planet (F2V star)", '-----', 'Proxima Cen b 10 bar 95% O2 dry', 'Proxima Cen b 10 bar 95% O2 wet', 'Proxima Cen b 10 bar O2-CO2', 'Proxima Cen b 90 bar O2-CO2', 'Proxima Cen b 90 bar Venus', 'Proxima Cen b 10 bar Venus', 'Proxima Cen b CO2/CO/O2 dry', 'Proxima Cen b Earth', 'Proxima Cen b Archean Earth', 'Proxima Cen b hazy Archean Earth', '-----','stars & galaxies:', '(arbitrary y units)', 'O5V star', 'B5V star', 'A5V star', 'F5V star', 'G2V star', 'G5V star', 'K2V star', 'M0V star', 'M2V star', 'M4V star', 'M5V star', 'Proxima Centauri star', 'T0 brown dwarf', 'T9 brown dwarf', 'L5 brown dwarf', 'L8 brown dwarf', 'NGC 337 spiral galaxy', 'NGC 660 peculiar galaxy', 'NGC 4621 elliptical galaxy', 'NGC 5033 spiral galaxy', 'Haro 6 blue compact dwarf galaxy', 'NGC 7476 spiral galaxy'])

#info text
info_text = Div(text="""

The "Planet" tab includes options to simulate several types of planetary spectra that can be selected from the "Planet Spectrum" dropdown menu. The telescope-planetary system separation distance can be set using the "Distance" slider. When a target is selected, the "Planet Radius" and "Semi-major axis of orbit" sliders will default to the correct positions for the selected planet. Note that while it is possible to adjust these parameters for each target, changing them can result in spectra representing non-physical targets. Also included under the "Planet" tab is a slider for scaling exozodiacal dust.
<br><br>
The "Observation" tab controls telescope integration time per coronagraphic bandpass, maximum single exposure time, and the ability to turn on a ground-based simulator that includes thermal radiation from the sky and Earth's atmospheric transmission.
<br><br>
The "Telescope" tab controls whether to simulate specific observatory architecture,  mirror diameter,  telescope temperature, the number of thermal surfaces, and whether to show the currently considered LUVOIR bandpasses.
<br><Br>
The "Instrumentation" tab controls the instrument inner working angle (IWA), outer working angle (OWA), both in terms of lambda/D, the spectrograph resolution for UV-VIS-NIR channels, and the detector gain factor.
<br><Br>
The "Exposure Time Calculator" tab contains a slider to set a desired signal-to-noise ratio. In the "Exposure Time" plot tab, the simulator will display the integration time required to obtain this signal-to-noise ratio for the current telescope and instrumentation setup. Note that this tab applies only to the Exposure Time plot, not to the Spectrum plot.
<br><br>
In the "Download" tab, spectral data can be downloaded in either .txt or .fits format.
<br><br>
The underlying model is derived from the python-based version of Tyler Robinson's coronagraphic spectrum and noise model (Robinson et al. 2016). Python by Jacob Lustig-Yaeger. Bokeh rendering by Jason Tumlinson and Giada Arney.
<br><br>
For full details, please see the readme file <a href="coron_readme.txt">here</a>.

""",
width=250, height=120)

planet_text = Div(text="""Select parameters for simulated planet.""", width=250, height=15)
obs_text = Div(text="""Choose telescope integration time per coronagraphic bandpass, the maximum length of time for a single exposure,  and whether to turn on a ground-based simulator.""", width=250, height=100)
tel_text = Div(text="""Choose whether to use a specified telescope architecture, mirror diameter, telescope temperature, number of thermal surfaces, and whether to show the currently considered LUVOIR bandpasses.""", width = 250, height = 90)
ins_text = Div(text="""Choose the scaling factor for the inner working angle (IWA), the outer working angle (OWA), spectrographic resolution for UV-VIS-NIR channels, and detector gain factor""", width=250, height=70)


#

oo = column(children=[obs_text,exptime,dtmax, ground_based]) 
pp = column(children=[planet_text, template, comparison, distance, radius, semimajor, exozodi]) 
qq = column(children=[instruction0, text_input, instruction1, format_button_group, instruction2, link_box])
ii = column(children=[ins_text, inner, outer,  resolution_UV, resolution, resolution_NIR, gain])
tt = column(children=[tel_text, observatory,diameter,temperature, ntherm, bandpass])
ee = column(children=[want_snr])
info = column(children=[info_text])

observation_tab = Panel(child=oo, title='Observation')
planet_tab = Panel(child=pp, title='Planet')
telescope_tab = Panel(child=tt, title='Telescope')
instrument_tab = Panel(child=ii, title='Instrumentation')
download_tab = Panel(child=qq, title='Download')
time_tab = Panel(child=ee, title='Exposure Time Calculator')
info_tab = Panel(child=info, title='Info')

for w in [text_input]: 
    w.on_change('value', change_filename)
format_button_group.on_click(i_clicked_a_button)

for ww in [template]: 
    ww.on_change('value', update_data)

for www in [comparison]: 
    www.on_change('value', update_data)

for gg in [ground_based]: 
    gg.on_change('value', update_data)

for bb in [bandpass]: 
    bb.on_change('value', update_data)

for bb in [observatory]:
    bb.on_change('value', update_data)

inputs = Tabs(tabs=[ planet_tab, observation_tab, telescope_tab, instrument_tab, time_tab, download_tab, info_tab ])

curdoc().add_root(row(inputs, ptabs)) 
