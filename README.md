MyFutureClimate
===============

The goal of MyFutureClimate is to help the public understand otherwise
complicated models of climate change by calculating how similar a location's
climate is to every other location. The location of this "climate analog" can
then be tracked forward and backward through time.

This project should be useful to policy and land management plannersin helping
them plan mitigation and adaptation strategies. It should also be useful to the
general public in helping them understand what effects climate change will have
on their local area.


TODO
===============
 * Ensure things are at least tablet-friendly
 * Set up a batch script to perform pre-caching for all major cities
 * Improve design/layout
 * Add in sea level rise
 * Add in a metric for extreme climate events
 * Use a multi-ensemble average for the projections
 * Use an adaptive strategy for judging similarity based on region
 * Bring service conf scripts into repo
 * Bring nginx conf scripts into repo
 * Add global finalist media


Getting Started
===============

You'll need some basic things to get started. The follow commands will install
the environment you'll need to run our code.

    apt-get install python-scipy python-h5py python-matplotlib python-redis redis-server python-pip python-routes libhdf5-dev python-pandas
    pip install cherrypy==3.3.0
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
Hack4Good finalist announcement is [here](http://blog.geekli.st/post/98065680547/the-winning-teams-of-the-geeklist-hack4good-against).
Hack4Good category finalist announcement is [here](http://blog.geekli.st/post/97978462607/announcing-12-challenge-theme-winners-hackers-choice).

Links
=====
[Geeklist Git Repo](https://git.geekli.st/rbarnes/myfutureclimate/)
[Geeklist Project Page](https://geekli.st/hackathon/hack4good-06/project/5414c07d1c363f370480641f)
[Geeklist Achievement Card](https://geekli.st/rbarnes/we-built-my-future-climate-at-geeklist-hack4good-06-in-virtual-locations)

Awards
======
This project was the grand finals winner of the Hack4Good 0.6 Hack Against Climate Change event.
