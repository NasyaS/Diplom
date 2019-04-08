
var mymap;
var circles = [];
var markers = [];
var LeafIcon;
var qtWidget;

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

function drawCirclePoly(lng, lat, radius){
    var d2r = Math.PI / 180;
    var r2d = 180 / Math.PI;
    var earthsradius = 6377830
    var points = 512;
    var rlat = (radius / earthsradius) * r2d;
    var rlng = rlat / Math.cos(lat * d2r);
    var extp = new Array();
    for (var i=0; i < points+1; i++){
        var theta = Math.PI * (i / (points/2));
        ex = lng + (rlng * Math.cos(theta));
        ey = lat + (rlat * Math.sin(theta));
        extp.push(new L.LatLng(ey, ex));
    }
    return extp
}

function osm_addCircle(rad, method){
    lat = markers[key].getLatLng().lat
    lng = markers[key].getLatLng().lng
    if (method == 1){
        outer = rad+rad*0.05
        inner = rad-rad*0.05
        for (key in markers){
            var outer_circle = drawCirclePoly(lng, lat, outer)
            var inner_circle = drawCirclePoly(lng, lat, inner) 
            var latlngs = [ ]
            latlngs.push(outer_circle)
            latlngs.push(inner_circle)
            var circle = new L.polygon(latlngs).addTo(mymap)
            circles[key] = circle
        }
    } else if (method == 2){
        stroke = rad*0.1
        for (key in markers){
            var circle = L.circle([lat, lng], { fillOpacity: 0.0, weight: stroke, opacity: 0.5, radius: rad}).addTo(mymap);
            circles[key] = circle
        }
    } else {
        outer = rad+rad*0.05
        inner = rad-rad*0.05
        for (key in markers){
            var outer_circle = L.circle([lat, lng], outer).addTo(mymap);
            var inner_circle = L.circle([lat, lng], inner).addTo(mymap);
            var circle = L.layerGroup([outer_circle, inner_circle]);
            circles[key] = circle
        }

    }
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