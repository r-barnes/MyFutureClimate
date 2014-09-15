var vent = {}; // or App.vent depending how you want to do this
_.extend(vent, Backbone.Events);

var TourClass = Backbone.View.extend({
  el: '#tourview',

  events: {
    'click #closetour': 'closeTour'
  },

  closeTour: function(){
    this.remove();
  }
});

var MapViewClass = Backbone.View.extend({
  el: '#mapview',

  events: {
    'change #year':   'yearChangedEvent',
    'input #year':    'yearDrag',
    'click #switchq': 'switchQuestion',
    'click #fitzoom': 'fitZoom'
  },

  initialize: function(){
    var self = this;

    var minneapolis = new google.maps.LatLng(44.9833, -93.2667);

    //These bounds are used for CONUS climate projections
    // self.climatebounds = new google.maps.LatLngBounds(
      // new google.maps.LatLng(25.1875,-124.6875), //SW
      // new google.maps.LatLng(52.8125,-67.0625)); //NE

    //These bounds are used for global climate projections
    //TODO: Does the 0.25 refer to the cell center or the top/bottom? Is the map
    //shifted vertically as a result?
    self.climatebounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(-55.25, -180),  //SW
        new google.maps.LatLng( 83.25,  180)); //NE


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

    if(navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
        initialLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
        self.click_marker.setPosition(initialLocation);
        self.map.setCenter(initialLocation);
      }, function() {
        console.log('Could not get geolocation.');
      });
    }

    self.question = 'goingto';
  },

  fitZoom: function(){
    var self = this;
    if(self.imagebounds)
      self.map.fitBounds(self.imagebounds);
  },

  switchQuestion: function(){
    var self = this;

    if(self.question=='goingto'){
      $('#goingto').hide();
      $('#comingfrom').show();
      $('#switchq').html('Going To');
      self.question = 'comingfrom';
    } else {
      $('#goingto').show();
      $('#comingfrom').hide();
      $('#switchq').html('Coming From');
      self.question = 'goingto';
    }
  },

  mapClicked: function(event){
    this.click_marker.setPosition(event.latLng)
    this.click_marker.setVisible(true);
  },

  yearDrag: function(event){
    var year = $('#year').val();
    $('.yearshow').html(year);
  },

  yearChanged: function(event){
    var year = $('#year').val();
    $('.yearshow').html(year);
    this.setMapGrid(year);
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

//Deprecated client-side caching
/*    if(typeof(self.climateoverlays[year])!=='undefined'){
      self.hideClimateOverlays();
      self.showClimateOverlay(year);
      return;
    }
*/
    var markerpos = this.click_marker.getPosition();
    var lat       = markerpos.lat();
    var lon       = markerpos.lng();

    vent.trigger('thinking');

    var img_data_url;
    if(self.question=='goingto')
      img_data_url = '/showgrid/simgrid/'+lat+'/'+lon+'/1985/2005/'+year+'/'+(parseInt(year,10)+20).toString()+'/6,7,8,12,1,2';
    else
      img_data_url = '/showgrid/simgrid/'+lat+'/'+lon+'/'+year+'/'+(parseInt(year,10)+20).toString()+'/1985/2005/6,7,8,12,1,2';

    $.getJSON(img_data_url, [], function(data){
      var img_url = '/imgget/'+data.img;
      var img     = new Image();
      img.src = img_url;

      console.log('Data raw', data);

      if(data.sw[1]>180)
        data.sw[1] = data.sw[1]-360;
      if(data.ne[1]>180)
        data.ne[1] = data.ne[1]-360;

      console.log('Data fixed', data);

      var my_imagebounds = new google.maps.LatLngBounds(
          new google.maps.LatLng(data.sw[0], data.sw[1]),  //SW
          new google.maps.LatLng(data.ne[0], data.ne[1])); //NE

      self.imagebounds = new google.maps.LatLngBounds(
          new google.maps.LatLng(data.sw[0], data.sw[1]),  //SW
          new google.maps.LatLng(data.ne[0], data.ne[1])); //NE
      self.imagebounds.extend(markerpos);

      img.addEventListener('load', function(){
        var newoverlay = new google.maps.GroundOverlay(img_url, my_imagebounds);
        newoverlay.setOpacity(0.6);
        google.maps.event.addListener(newoverlay,'click',self.mapClicked);

        self.hideClimateOverlays();
        self.climateoverlays[year] = newoverlay;
        self.showClimateOverlay(year);
      });
    })
    .fail(function() {
      console.log('Error occurred!');
      alert('Error occurred. Please try again.');
    })
    .always(function() {
      vent.trigger('donethinking');
    });
    //var newoverlay = new google.maps.GroundOverlay('/showgrid/prcpgrid/'+year+'/3', setMapGrid.climatebounds);
    //var newoverlay = new google.maps.GroundOverlay('/showgrid/prcpmean/'+year+'/3/'+(parseInt(year,10)+1).toString()+'/3', setMapGrid.climatebounds);


  }
});

var MapView  = new MapViewClass();
var TourView = new TourClass();

vent.on('thinking', function(){
  $('#thinkingbox').show();
});

vent.on('donethinking', function(){
  $('#thinkingbox').hide();
});