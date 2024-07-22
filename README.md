# luvoir_simtools
simulation tools for the LUVOIR Surveyor STDT

(1) you must have bokeh 0.12 installed to use these tools 
    http://bokeh.pydata.org/en/latest/docs/installation.html

(2) bokeh serve --show image_comparison (for instance) 

## docker-based setup

If you can't get all the dependencies wrangled, you might try using docker.  You need to get [docker](https://www.docker.com/), and then do: 

* ``docker build -t luvoir_simtools .``
* ``docker run -it --rm -p 5006:5006 --mount type=bind,source=/path/to/your/cdbs/dir,target=/app/pysynphot_cdbs``

Note this will require the pysynphot cdbs files - if you have these just update ``/path/to/your/cdbs/dir`` to wherever you have them, otherwise you'll need to download everything in the list of files from the [pysynphot install instructions](https://pysynphot.readthedocs.io/en/latest/#installation-and-setup), and then update the path to wherever you un-tar them.