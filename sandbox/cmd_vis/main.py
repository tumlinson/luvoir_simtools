"""
Bokeh app example using datashader for rasterizing a large dataset and
geoviews for reprojecting coordinate systems.

This example requires the 1.7GB nyc_taxi.csv dataset which you can
obtain by following the instructions for 'nyc_taxi' at:

  https://github.com/bokeh/datashader/blob/master/examples/README.md

Once this CSV is placed in a data/ subfolder, you can run this app with:

  bokeh serve --show nytaxi_hover.py

"""
import holoviews as hv
import geoviews as gv
import dask.dataframe as dd
import pandas as pd
import cartopy.crs as ccrs
from astropy.table import Table 
from holoviews.operation.datashader import aggregate

hv.extension('bokeh')

# make a dataframe out of the CMD 
ssp = Table.read('../data/basic_ssp.fits') 
print(ssp.keys()) 
cmd = ssp[ssp['LOGAGE'] > 10.1] 
df_test = pd.DataFrame({'b_band':cmd['UVIS_F475W'], 'r_band':cmd['UVIS_F814W'], 'color':cmd['UVIS_F475W']-cmd['UVIS_F814W']}) 
df1 = dd.from_pandas(df_test, npartitions=1) 

# Set plot and style options
hv.util.opts('Image [width=400 height=400 shared_axes=False logz=True] {+axiswise} ')
hv.util.opts("HLine VLine (color='white' line_width=1) Layout [shared_axes=False] ")
hv.util.opts("Curve [xaxis=None yaxis=None show_grid=False, show_frame=False] (color='orangered') {+framewise}")

# Read the short NYC CSV file over in the data directory 
#df2 = dd.read_csv('../data/nyc_taxi_short.csv',usecols=['b_band', 'r_band'])
df = df1.persist()

# Reproject points from Mercator to PlateCarree (latitude/longitude)
points = gv.Points(df, kdims=['color', 'r_band'], vdims=[], crs=ccrs.GOOGLE_MERCATOR)
projected = gv.operation.project_points(points, projection=ccrs.PlateCarree())
projected = projected.redim(color='lon', r_band='latR')

# Use datashader to rasterize and linked streams for interactivity
agg = aggregate(projected, link_inputs=True, x_sampling=0.0000001, y_sampling=0.0000001)
pointerx = hv.streams.PointerX(x=-74, source=projected)
pointery = hv.streams.PointerY(y=40.8,  source=projected)
vline = hv.DynamicMap(lambda x: hv.VLine(x), streams=[pointerx])
hline = hv.DynamicMap(lambda y: hv.HLine(y), streams=[pointery])

sampled = hv.util.Dynamic(agg, operation=lambda obj, x: obj.sample(lon=x),
                          streams=[pointerx], link_inputs=False)

hvobj = ((agg * hline * vline) << sampled.opts(plot={'Curve': dict(width=100)}))

doc = hv.renderer('bokeh').server_doc(hvobj)
doc.title = 'LUVOIR CMD Simulator'
