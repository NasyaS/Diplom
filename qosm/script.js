
var mymap;
var circles = [];
var markers = [];
var qtWidget;

var m_c = 0;

var icons = [ 
    'https://c.radikal.ru/c37/1904/c0/5aa90f3825b3.png',
    'https://c.radikal.ru/c38/1904/b6/7ea95b578256.png',
    'https://c.radikal.ru/c15/1904/37/e0a2bef7c9cb.png',
    'https://b.radikal.ru/b37/1904/b4/e6a0c6a082f8.png',
    'https://c.radikal.ru/c06/1904/6e/e7ce93852bff.png',
    'https://a.radikal.ru/a22/1904/fe/8698904a1a2a.png',
    'https://c.radikal.ru/c07/1904/69/eee80cce7123.png',
    'https://b.radikal.ru/b19/1904/e7/20462fed67b7.png',
    'https://a.radikal.ru/a23/1904/c4/1ae8521ab52b.png',
    'https://b.radikal.ru/b17/1904/fc/2f915b55c959.png'];

function initialize(){
	mymap = L.map('mapid').setView([64.54938070965152, 40.53628921508789], 13);
	L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoia25zcm9vIiwiYSI6ImNqczI3dDRncDA2cWc0OXBtM2syaXVtZWoifQ.MSuCCjQY-bmbmXu2bprSSA', {
	    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
	    maxZoom: 18,
	    id: 'mapbox.streets'
	}).addTo(mymap);
    L.Control.geocoder().addTo(mymap);
    L.control.scale().addTo(mymap);

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

function osm_addCircle(rad, key) {
    lat = markers[key].getLatLng().lat
    lng = markers[key].getLatLng().lng
    outer = rad+rad*0.05
    inner = rad-rad*0.05
    var circle = L.circleDisk([lat, lng], inner, outer).addTo(mymap)
    circles[key] = circle
}

function osm_removeCircle(key){
    mymap.removeLayer(circles[key]);
    delete circles[key];
}

function osm_clear(){
    for (key in markers){
        mymap.removeLayer(circles[key]);
        mymap.removeLayer(markers[key]);
    }
    circles = []
    markers = []
}

function osm_addMarker(key, latitude, longitude, parameters){

    if (key in markers) {
        osm_deleteMarker(key);
    } 

    parameters["icon"] = new L.icon({
        iconUrl:     icons[m_c],
        //iconRetinaUrl: "lightblue_.png",
        shadowUrl:     "https://d.radikal.ru/d28/1904/db/8ba68aad1ea2.png",
        iconSize:    [25, 41],
        iconAnchor:  [12, 41],
        popupAnchor: [1, -34],
        tooltipAnchor: [16, -28],
        shadowSize:  [41, 41]
        });

    var marker = L.marker([latitude, longitude], parameters).addTo(mymap);

    m_c++

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