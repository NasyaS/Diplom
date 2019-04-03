var mymap;
var circle = 0;
var markers = [];
var LeafIcon;
var qtWidget;

function initialize(){
	mymap = L.map('mapid').setView([51.505, -0.09], 13);
	L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoia25zcm9vIiwiYSI6ImNqczI3dDRncDA2cWc0OXBtM2syaXVtZWoifQ.MSuCCjQY-bmbmXu2bprSSA', {
	    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
	    maxZoom: 18,
	    id: 'mapbox.streets'
	}).addTo(mymap);

	if (typeof qt != 'undefined') {

			new QWebChannel(qt.webChannelTransport, function (channel) {
		        qtWidget = channel.objects.qOSMap;
		    });

		mymap.on('dragend', function () {
			center = mymap.getCenter();
			qtWidget.mapIsMoved(center.lat, center.lng);
		});

		mymap.on('click', function (ev) {
		    qtWidget.mapIsClicked(ev.latlng.lat, ev.latlng.lng);
		});

		mymap.on('dblclick', function (ev) {
		    qtWidget.mapIsDoubleClicked(ev.latlng.lat, ev.latlng.lng);
		});

		mymap.on('contextmenu', function (ev) {
		    qtWidget.mapIsRightClicked(ev.latlng.lat, ev.latlng.lng);
		});
}

}

function osm_setCenter(lat, lng) {
    mymap.panTo(new L.LatLng(lat, lng));
}

function osm_getCenter() {
    return mymap.getCenter();
}

function osm_setZoom(zoom) {
    mymap.setZoom(zoom);
}

function osm_addCircle(lat, lng, radius){
    osm_removeCircle()
    circle = L.circle([lat, lng], radius).addTo(mymap); 
}

function osm_removeCircle(){
    if (circle != 0){
        mymap.removeLayer(circle)
        circle = 0
    }
}

function osm_addMarker(key, latitude, longitude, parameters){

    if (key in markers) {
        osm_deleteMarker(key);
    } 

    if ("icon" in parameters) {

        parameters["icon"] = new L.Icon({
            iconUrl: parameters["icon"],
            iconAnchor: new L.Point(16, 16)
        });
    }

    var marker = L.marker([latitude, longitude], parameters).addTo(mymap);

    if (typeof qtWidget != 'undefined') {

        marker.on('dragend', function (event) {
            var marker = event.target;
            qtWidget.markerIsMoved(key, marker.getLatLng().lat, marker.getLatLng().lng);
        });

        marker.on('click', function (event) {
            var marker = event.target;
            qtWidget.markerIsClicked(key, marker.getLatLng().lat, marker.getLatLng().lng);
        });

        marker.on('dbclick', function (event) {
            var marker = event.target;
            qtWidget.markerIsDBClicked(key, marker.getLatLng().lat, marker.getLatLng().lng);
        });

        marker.on('contextmenu', function (event) {
            var marker = event.target;
            qtWidget.markerIsRClicked(key, marker.getLatLng().lat, marker.getLatLng().lng);
        });
   }

    markers[key] = marker;
    return key;
}

function osm_deleteMarker(key) {
    mymap.removeLayer(markers[key]);
    delete markers[key];
}

function osm_moveMarker(key, latitude, longitude) {
    marker = markers[key];
    var newLatLng = new L.LatLng(latitude, longitude);
    marker.setLatLng(newLatLng);
}

function osm_posMarker(key) {
    marker = markers[key];
    return [marker.getLatLng().lat, marker.getLatLng().lng];
}