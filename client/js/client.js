var vent = {}; // or App.vent depending how you want to do this
_.extend(vent, Backbone.Events);

var MapViewClass = Backbone.View.extend({
  el: '#mapview',

  events: {
    'change #year': 'yearChangedEvent'
  },

  initialize: function(){
    var self = this;

    var minneapolis = new google.maps.LatLng(44.9833, -93.2667);

    self.climatebounds = new google.maps.LatLngBounds(
      new google.maps.LatLng(25.1875,-124.6875),
      new google.maps.LatLng(52.8125,-67.0625));

    self.imageBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(40.712216, -74.22655),  //SW
        new google.maps.LatLng(40.773941, -74.12544)); //NE

    var mapOptions = {
      zoom: 4,
      center: minneapolis
    };

    self.map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    google.maps.event.addListener(self.map, 'click', self.mapClicked);

    self.click_marker = new google.maps.Marker({
      position:  minneapolis,
      map:       self.map,
      draggable: true,
      zIndex:    1,
    });

    this.climateoverlays = {};

    this.yearChangedEvent = $.debounce(self.yearChanged, 500);

    self.loadPolygons();
  },

  mapClicked: function(event){
    this.click_marker.setPosition(event.latLng)
    this.click_marker.setVisible(true);
  },

  yearChanged: function(event){
    this.setMapGrid($('#year').val());
  },

  hideClimateOverlays: function(){
    for(var i in this.climateoverlays)
      this.climateoverlays[i].setMap(null);
  },

  showClimateOverlay: function(year){
    this.climateoverlays[year].setMap(this.map);
  },

  setMapGrid: function(year){
    var self = this;
    console.log(year);

    if(typeof(self.climateoverlays[year])!=='undefined'){
      self.hideClimateOverlays();
      self.showClimateOverlay(year);
      return;
    }

    var markerpos = this.click_marker.getPosition();
    var lat       = markerpos.lat();
    var lon       = markerpos.lng();

    var img     = new Image();
    var img_url = '/showgrid/simgrid/'+lat+'/'+lon+'/2007/2017/'+year+'/'+(parseInt(year,10)+20).toString()+'/6,7,8,12,1,2';
    img.src = img_url;

    vent.trigger('thinking');

    img.addEventListener('load', function(){
      console.log('Image loaded.');
      var newoverlay = new google.maps.GroundOverlay(img_url, self.climatebounds);
      newoverlay.setOpacity(0.6);
      google.maps.event.addListener(newoverlay,'click',self.mapClicked);

      self.hideClimateOverlays();
      self.climateoverlays[year] = newoverlay;
      self.showClimateOverlay(year);

      vent.trigger('donethinking');
    });
    //var newoverlay = new google.maps.GroundOverlay('/showgrid/prcpgrid/'+year+'/3', setMapGrid.climatebounds);
    //var newoverlay = new google.maps.GroundOverlay('/showgrid/prcpmean/'+year+'/3/'+(parseInt(year,10)+1).toString()+'/3', setMapGrid.climatebounds);


  }
});

var MapView       = new MapViewClass();

vent.on('thinking', function(){
  $('#thinkingbox').show();
});

vent.on('donethinking', function(){
  $('#thinkingbox').hide();
});