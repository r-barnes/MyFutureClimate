#!/usr/bin/env python

from scipy.io import netcdf  #For NetCDF file reading
import h5py                  #For HDF5 file reading
import sys
import numpy as np
import matplotlib.pyplot as plt
import Image
import cStringIO     #TODO: Unused
import matplotlib as mpl
import redis         #For caching processed results
import io
import glob          #Used for listing files in a directory
import inspect       #For gettting the server root directory
import os            #For gettting the server root directory
import bisect        #For finding where lat/lon are in a sorted list
import itertools     #For mashing years with months
import datetime
import time
import json          #For talking to server
import hashlib       #For Redis
import cPickle       #Used for stashing Numpy arrays

#import code #For debugging with: code.interact(local=locals())

redisclient = redis.StrictRedis(host='localhost', port=6379, db=0)







def binaryfind(arr, val):
  if val<arr[0] or val>arr[-1]:
    raise Exception('Value not in range of array')

  i = bisect.bisect_left(arr, val)
  if arr[i]==val:                         #Obviously should return this index
    return i
  elif i==0:                              #We're at the left edge of list, only one index to return
    return i
  elif abs(arr[i]-val)<abs(arr[i-1]-val): #Decide which is best based on difference
    return i
  else:
    return i-1



class ClimateGrid():
  def __init__(self):
    self.start_time = datetime.datetime(year=1950, month=1, day=1, hour=0, minute=0, second=0)

  def getGridByTime(self, year, month):
    time = self.yearMonthToTime(year, month)
    return self.data[time]

  def yxClosestToLatLon(self, lat, lon):
    y = binaryfind(self.lat[:],float(lat))
    x = binaryfind(self.lon[:],float(lon))
    return y, x

  def timesToUnix(self):
    return map(lambda x: time.mktime((self.start_time+datetime.timedelta(days=x)).timetuple()),self.time)

  def timesToDateTime(self):
    return map(lambda x: self.start_time+datetime.timedelta(days=x),self.time)

  def yearMonthsToTimes(self, startyear, endyear, months):
    years     = range(int(startyear),int(endyear)+1)
    yms       = itertools.product(years,months)
    yms       = map(lambda ym: self.yearMonthToTime(ym[0],ym[1]), yms)
    return yms #TODO: Verify that this is correct

  def pointMean(self, lat, lon, startyear, endyear, months):
    y,x      = self.yxClosestToLatLon(lat,lon)
    times    = self.yearMonthsToTimes(startyear, endyear, months)
    return np.mean(self.data[times,y,x])

  def yearMonthToTime(self, year, month):
    year      = int(year)
    month     = int(month)
    this_time = datetime.datetime(year=year, month=month, day=16, hour=12, minute=0) #Data is labeled in the middle of the month on the 15th/16th @ midnight
    days      = (this_time-self.start_time).days
    return binaryfind(self.time, days)

  def meanVals(self, startyear, endyear, months):
    key = 'meanVals-' + self.filename + '-' + str(startyear)+':'+str(endyear)+':'+str(months)
    key = 'int-'+hashlib.md5(key).hexdigest()

    cached = redisclient.get(key)
    if cached:
      print "Loading cached meanVals"
      return cPickle.loads(cached)

    times             = self.yearMonthsToTimes(startyear, endyear, months)
    tgrid             = self.data[times]
    tgrid[tgrid>1e15] = np.nan
    avg_grid          = np.mean(tgrid, axis=0)

    to_cache = cPickle.dumps(avg_grid)
    redisclient.set(key,to_cache)

    return avg_grid

  def stdVals(self, startyear, endyear, months):
    key = 'stdVals-' + self.filename + '-' + str(startyear)+':'+str(endyear)+':'+str(months)
    key = 'int-'+hashlib.md5(key).hexdigest()

    cached = redisclient.get(key)
    if cached:
      print "Loading cached stdVal"
      return cPickle.loads(cached)

    times             = self.yearMonthsToTimes(startyear, endyear, months)
    tgrid             = self.data[times]
    tgrid[tgrid>1e15] = np.nan
    std_grid          = np.std(tgrid, axis=0)

    to_cache = cPickle.dumps(std_grid)
    redisclient.set(key,to_cache)

    return std_grid

  def timeSeries(self, lat, lon):
    y = binaryfind(self.lat[:],float(lat))
    x = binaryfind(self.lon[:],float(lon))
    return self.data[:,y,x]


class NetCDFClimateGrid(ClimateGrid):
  def __init__(self, filename, varname):
    ClimateGrid.__init__(self)
    self.filename = filename
    self.fin      = netcdf.netcdf_file(filename,'r')
    self.data     = self.fin.variables[varname]
    self.lat      = self.fin.variables['latitude'][:]
    self.lon      = self.fin.variables['longitude'][:]
    self.time     = self.fin.variables['time'][:]

  def varNames(self):
    return self.fin.variables

  def varShape(self, var):
    return self.fin.variables[var].shape

  def varUnits(self, var):
    return self.fin.variables[var].units

  def varDims(self, var):
    return self.fin.variables[var].dimensions

class HDFClimateGrid(ClimateGrid):
  def __init__(self, filename, varname):
    ClimateGrid.__init__(self)
    self.filename = filename
    self.fin      = h5py.File(filename,'r')
    self.data     = self.fin[varname]
    self.lat      = self.fin['latitude'][:]
    self.lon      = self.fin['longitude'][:]
    self.time     = self.fin['time'][:]

  def varNames(self):
    return self.fin.keys()



import cherrypy
class ServerRoot():
  def __init__(self):
    #Serve static files from the directory the server file is included in.
    #TODO: Exclude the server script itself
    #server_root_directory = os.path.dirname(os.path.realpath(__file__))

    filename              = inspect.getframeinfo(inspect.currentframe()).filename
    server_root_directory = os.path.dirname(os.path.abspath(filename))
    self._cp_config       = {
      'tools.staticdir.on':    True,
      'tools.staticdir.dir':   server_root_directory,
      'tools.staticdir.index': 'index.html'
    }

    self.temp = HDFClimateGrid('data/BCSD_0.5deg_tas_Amon_MIROC5_rcp45_r1i1p1_200601-210012.nc', 'tas')
    self.prcp = HDFClimateGrid('data/BCSD_0.5deg_pr_Amon_MIROC5_rcp45_r1i1p1_200601-210012.nc', 'pr')

    self.data = {}
    for fname in glob.glob('data/BCSD*nc'):
      fnameparts = fname.split('_')
      variable   = fnameparts[2]
      model      = fnameparts[4]
      rcp        = fnameparts[5]
      if not rcp in self.data:
        self.data[rcp] = {}
      if not model in self.data[rcp]:
        self.data[rcp][model] = {}
      print rcp,model,variable
      self.data[rcp][model][variable] = HDFClimateGrid(fname, variable)

  def img2buffer(self, image):
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output

  def bufferAsPNGFile(self, buffer):
    cherrypy.response.headers['Content-Type'] = "image/png"
    return cherrypy.lib.file_generator(buffer)

  def stringAsBuffer(self, str):
    output = io.BytesIO(str)
    output.seek(0)
    return output

  def _gridToImage(self, grid):
    #Get a copy of the grid related to this time. TODO: Try not to make a copy
    grid            = grid.copy()
    #Convert NoData cells to NaNs
    grid[grid>1e15] = np.nan
    #Flip grid to display in the familiiar orientation
    grid            = grid[::-1,:]

    #Build a mask from the NaN values so that we can avoid displaying them
    mask = Image.fromarray((~np.isnan(grid))*3000.).convert('L')
    #Scale the grid based on the max/min values (ignoring NaNs) and then convert
    #to RGBA colour scheme
    grid = Image.fromarray(mpl.cm.jet_r((grid-np.nanmin(grid))/(np.nanmax(grid)-np.nanmin(grid)), bytes=True)).convert('RGBA')
    #Mask the NaN values to transparent
    grid.putalpha(mask)

    return grid

  def genSimGrid(self, lat, lon, refstartyear, refendyear, compstartyear, compendyear, months):
    accum = np.zeros(self.temp.data.shape[1:]) #TODO: Abstract this somehow
    for m in months:
      temp_ref_mean = self.temp.pointMean(lat, lon, refstartyear, refendyear, [m]) #Units are degC
      temp_mean     = self.temp.meanVals(compstartyear, compendyear, [m])
      temp_std      = self.temp.stdVals (refstartyear,  refendyear,  [m])
      accum        += np.power(np.divide(temp_mean-temp_ref_mean,temp_std),2.0)

    for m in months:
      prcp_ref_mean = self.prcp.pointMean(lat, lon, refstartyear, refendyear, [m]) #Units are mm/d
      prcp_mean     = self.prcp.meanVals(compstartyear, compendyear, [m])
      prcp_std      = self.prcp.stdVals (refstartyear,  refendyear,  [m])
      accum        += np.power(np.divide(prcp_mean-prcp_ref_mean,prcp_std),2.0)

    accum = np.sqrt(accum)
    #accum = np.log (accum)
    print 'similarity max',np.nanmax(accum)

    #Make portions of the map which are not like this climate transparent
    accum[accum>2] = np.NaN

    #TODO: Used to shift Global 0.5 degree grid so that the first data point is
    #-180 degrees. This ensures appropriate centering in Google Maps.

    return accum

  def _trimGrid(self, grid):
    grid = np.roll(grid,360,axis=1)

    nans    = np.isnan(grid)
    nancols = np.all(nans, axis=0)
    nanrows = np.all(nans, axis=1)

    firstcol = nancols.argmin() #The first index where not NAN
    firstrow = nanrows.argmin()

    lastcol = len(nancols) - nancols[::-1].argmin() # Last index where not NAN
    lastrow = len(nanrows) - nanrows[::-1].argmin() #

    lons = self.temp.lon
    lons = np.roll(lons,360)

    print lastrow,lastcol
    lastrow = min(lastrow,len(self.temp.lat)-1)
    lastcol = min(lastcol,len(lons)-1)
    print lastrow,lastcol

    sw = [float(self.temp.lat[firstrow]), float(lons[firstcol])]
    ne = [float(self.temp.lat[lastrow]), float(lons[lastcol])]

    return (grid[firstrow:lastrow,firstcol:lastcol],sw,ne)

  @cherrypy.expose
  def imgget(self, key):
    cached = redisclient.get('img-'+key)
    if cached:
      cached = self.stringAsBuffer(cached)
      cached = self.bufferAsPNGFile(cached)
      return cached
    else:
      cherrypy.response.status = 404
      cherrypy.response.body = ''
      return

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def simgrid(self, lat, lon, refstartyear, refendyear, compstartyear, compendyear, months):
    print "Entering simgrid"

    lat = float(lat)
    lon = float(lon)
    if lon<0:
      lon = 360+lon

    y,x = self.temp.yxClosestToLatLon(lat,lon)

    key = (y, x, refstartyear, refendyear, compstartyear, compendyear, months)
    key = hashlib.md5(json.dumps(key)).hexdigest()

    print key
    cached = redisclient.get('pos-'+key)
    print cached
    if cached:
      print "Found cached image data."
      return json.loads(cached)

    print "Building new image"
    compendyear = min(compendyear,2100)
    refendyear  = min(refendyear,2100)

    months = map(int,months.split(','))

    accum = self.genSimGrid(lat, lon, refstartyear, refendyear, compstartyear, compendyear, months)

    print "Trimming"
    accum = self._trimGrid(accum)

    pos = json.dumps({'img':key, 'sw':accum[1], 'ne':accum[2]})

    img = self._gridToImage(accum[0])
    img = self.img2buffer(img).getvalue()
    redisclient.set('img-'+key,img)
    redisclient.set('pos-'+key,pos)

    print pos

    return {'img':key, 'sw':accum[1], 'ne':accum[2]}
    #img = self.bufferAsPNGFile(img)
    #return img

#Entry point of script. Starts up server and sets up URL routing.
if len(sys.argv)!=2:
  print "Syntax: %s <COMMAND>" % (sys.argv[0])
  print "Commands:"
  print "\tserver         - Starts the web server"
  print "\tinteractive    - Start things in interactive mode"
elif sys.argv[1]=='server':
  #These two lines turn off the WSGI (whatever that is) handling of the server
  #which, at least in theory, speeds up its operation slightly
  from cherrypy._cpnative_server import CPHTTPServer
  cherrypy.server.httpserver = CPHTTPServer(cherrypy.server)

  root = ServerRoot()

  d = cherrypy.dispatch.RoutesDispatcher()
  #If we don't know what it is, try to handle it using the class itself
  d.connect('default_route', '/', controller=root)

  #Recognised paths go here
  d.connect('some_other', '/showgrid/tempgrid/:year/:month', controller=root, action='tempgrid')
  d.connect('some_other', '/showgrid/prcpgrid/:year/:month', controller=root, action='prcpgrid')

  d.connect('some_other', '/showgrid/tempmean/:startyear/:startmonth/:endyear/:endmonth', controller=root, action='tempmean')
  d.connect('some_other', '/showgrid/prcpmean/:startyear/:startmonth/:endyear/:endmonth', controller=root, action='prcpmean')

  d.connect('some_other', '/showgrid/simgrid/:lat/:lon/:refstartyear/:refendyear/:compstartyear/:compendyear/:months', controller=root, action='simgrid')

  d.connect('some_other', '/imgget/:key', controller=root, action='imgget')

  #Set up configuration options for server
  conf = {'/': {'request.dispatch': d}}

  #cherrypy.config.update(file('cfg.ini'))

  #Start up the server
  cherrypy.quickstart(root, '/', config=conf)
else:
  pass