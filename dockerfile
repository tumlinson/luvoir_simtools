FROM python:3.7
WORKDIR /app
# if you don't want to run this next to the source repo, uncomment this and comment the next line
#RUN git clone https://github.com/tumlinson/luvoir_simtools.git
COPY . /app/luvoir_simtools
RUN apt update && \
    apt install -y gcc g++ gfortran libopenblas-dev liblapack-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*
RUN --mount=type=cache,target=/root/.cache/pip pip install "numba<0.50" "llvmlite<0.33" "dask<0.20" "bokeh<0.13" "numpy<1.15" "scipy<1.2" "Cython<0.29" "astropy<3.1" "tornado<5" "pandas<0.25" "pyyaml<4" "Jinja2<2.11" "markupsafe<2" "matplotlib<3" "pysynphot<1" "holoviews<1.10" "xarray<0.11" "datashader<0.9" "parambokeh==0.2.3"

# need to manually build specutils due to some weird cython-related incompatibility in the pyx file
ADD --checksum=sha256:d5536a67718887cf7778a4c35744b25c97f6c0efe0ccf0ea7b4b5d7200572516 https://files.pythonhosted.org/packages/d5/31/a5c67a70ae1b56f1ed9878d05e0694776d917a590e5797ee355a5aae262c/specutils-0.2.2.tar.gz /app
RUN tar xf specutils-0.2.2.tar.gz && cd specutils-0.2.2 && rm specutils/cextinction.pyx && python setup.py install

ENV PYTHONPATH="/app/luvoir_simtools"
ENV PYSYN_CDBS="/app/pysynphot_cdbs"
WORKDIR /app/luvoir_simtools
CMD bokeh serve cmd cmd_gk coron_model hdi_etc image_comparison image_comparison_gk image_viewer lumos_etc mosview multiplanet_vis phat_viewer pollux_etc qso_galaxy
EXPOSE 5006
