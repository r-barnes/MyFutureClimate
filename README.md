MyFutureClimate
===============

The goal of MyFutureClimate is to help the public understand otherwise
complicated models of climate change by calculating how similar a location's
climate is to every other location. The location of this "climate analog" can
then be tracked forward and backward through time.


TODO
===============
 * Add year indicator to display
 * Make display mobile friendly
 * Separate server map generation code into a separate Python script
 * Write a new server in Node.js to serve up the images produced by the above


Getting Started
===============

You'll need some basic things to get started. The follow commands will install
the environment you'll need to run our code.

    apt-get install python-scipy python-h5py python-matplotlib python-redis redis-server python-pip python-routes libhdf5-dev
    pip install cherrypy==3.3.0
    pip install python-magic
    pip install h5py
    apt-get install nginx


Data Sources
============

Climate Data
------------

CMIP5 GCM climate data can be viewed [here](ftp://gdo-dcp.ucllnl.org/pub/dcp/archive/cmip5/global_mon/).

The prototype app uses the CESM1-CAM5 model. Later iterations will use a multi-ensemble average of climate models. The download links for the data used in the app are as follows. The downloaded files should be placed in the `data/` directory.

    ftp://gdo-dcp.ucllnl.org/pub/dcp/archive/cmip5/global_mon/BCSD/cesm1-cam5/rcp60/mon/r1i1p1/tas/BCSD_0.5deg_tas_Amon_CESM1-CAM5_rcp60_r1i1p1_200601-210012.nc

    ftp://gdo-dcp.ucllnl.org/pub/dcp/archive/cmip5/global_mon/BCSD/cesm1-cam5/rcp60/mon/r1i1p1/pr/BCSD_0.5deg_pr_Amon_CESM1-CAM5_rcp60_r1i1p1_200601-210012.nc

    ftp://gdo-dcp.ucllnl.org/pub/dcp/archive/cmip5/global_mon/BCSD/cesm1-cam5/historical/mon/r1i1p1/tas/BCSD_0.5deg_tas_Amon_CESM1-CAM5_historical_r1i1p1_195001-200512.nc

    ftp://gdo-dcp.ucllnl.org/pub/dcp/archive/cmip5/global_mon/BCSD/cesm1-cam5/historical/mon/r1i1p1/pr/BCSD_0.5deg_pr_Amon_CESM1-CAM5_historical_r1i1p1_195001-200512.nc

Notes:
 * 0.5 degree images are 720x278 pixels.

Elevation Data (if we do something we sea level rise)
-----------------------------------------------------
ftp://srtm.csi.cgiar.org/SRTM_V41/SRTM_Data_GeoTiff/


Media
=====
Category finals presentation is [here](https://www.youtube.com/watch?v=h_GzzvIa4QY&list=UU3ofNKrKZBn8AvFeG3A6w6A) and starts at 29:17.
