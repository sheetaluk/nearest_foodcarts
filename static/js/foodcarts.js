(function($) {
  var DEFAULT_USER_LAT = 37.776775;
  var DEFAULT_USER_LONG = -122.416791;
  var DEFAULT_USER_MARKER_TITLE = 'User Location';

  var GET_FOODCARTS_API_URL =
    'http://vast-castle-9076.herokuapp.com/api/v1.0/nearest_foodcarts';

  var USER_PIN = 
    'images/pin.png';

  var MAP_CANVAS = 'map-canvas';
  
  // Method to return URL for fetching foodcarts
  var getUrlForFetchingFoodcarts = function(lat, lng) {
    return GET_FOODCARTS_API_URL +
      '?user_lat=' +
      lat +
      '&user_long=' +
      lng;
  };

  // Method to return HTML for marker infowindow
  var getTemplate = function(applicant, address, foodItems) {
    var foodItemsFormatted = foodItems.replace(/:/g, ',');
    return '<address>' +
    '<div class="applicant">' +
    '<h5>' +
    applicant +
    '<div>' +
    '<small>' +
    address +
    '</small>' +
    '</div>' +
    '</h5>' +
    '<div class="food-items">' +
    foodItemsFormatted +
    '</div>' +
    '</address>';
  }
  
  // function that return a new google Latlng
  function createNewLatlng(lat, lng) {
    return new google.maps.LatLng(lat, lng);
  }

  // User location pin
  var Userpin = Backbone.Model.extend({
    defaults: {
      'lat': DEFAULT_USER_LAT,
      'long':DEFAULT_USER_LONG
    }
  });
  var userpin = new Userpin();

  // Foodcarts model and collection
  var Foodcart = Backbone.Model.extend();

  var Foodcarts = Backbone.Collection.extend({
    model: Foodcart,
    url: getUrlForFetchingFoodcarts(userpin.get('lat'), userpin.get('long'))
  });
  var foodcarts = new Foodcarts;

  // function to initialize the map
  var map;
  var infowindow;
  function initialize() {
    var myLatlng = createNewLatlng(
      userpin.get('lat'), userpin.get('long'));
    var mapOptions = {
      zoom: 16,
      center: myLatlng
    };

    map = new google.maps.Map(document.getElementById(MAP_CANVAS), mapOptions);

    infowindow = new google.maps.InfoWindow();

    var userpinMarker = new google.maps.Marker({
      position: myLatlng,
      map: map,
      title: DEFAULT_USER_MARKER_TITLE,
      icon: {
        url: USER_PIN,
        scaledSize: new google.maps.Size(50, 50)
      }
    });

    google.maps.event.addListener(map, 'click', function(event){
      userpin.set({
        lat: event.latLng.lat(),
        long: event.latLng.lng()
      });
      userpinMarker.setPosition(createNewLatlng(userpin.get('lat'), userpin.get('long')));
      map.setCenter(userpinMarker.getPosition());
      foodcarts.fetch({reset: true, url: getUrlForFetchingFoodcarts(userpin.get('lat'), userpin.get('long'))});
    });
  };

  // function to clear markers
  var foodcartMarkersArray = [];
  google.maps.Map.prototype.clearOverlays = function() {
    for (var i = 0; i < foodcartMarkersArray.length; i++ ) {
      foodcartMarkersArray[i].setMap(null);
    }
    foodcartMarkersArray.length = 0;
  };

  // Mapview
  var mapView;
  var MapView = Backbone.View.extend({
    el: $('#'+MAP_CANVAS),

    initialize: function() {
      _.bindAll(this, 'render');
      this.collection.on('reset', this.render, this);
      this.collection.fetch({
        success: this.render
      });
    },

    render: function() {
      map.clearOverlays();
      _.each(this.collection.models, function(m) {
        var foodcartLatlng =
          createNewLatlng(m.get('latitude'), m.get('longitude'));
        
        var foodcartMarker = new google.maps.Marker({
          position: foodcartLatlng,
          map: map,
          title: m.get('applicant')
        });
        foodcartMarkersArray.push(foodcartMarker);
        google.maps.event.addListener(foodcartMarker, 'click', function() {
          infowindow.setContent(getTemplate(
            m.get('applicant'), m.get('address'), m.get('fooditems')))
          infowindow.open(map,foodcartMarker);
        });
      });
    }
  });
  mapView = new MapView({
    collection: foodcarts
  });

  google.maps.event.addDomListener(window, 'load', initialize);
})(jQuery);
