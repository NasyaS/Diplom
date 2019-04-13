L.CircleDisk = L.Circle.extend({
    initialize: function (latlng, radius, radius2, options) {
        L.setOptions(this, options);
        this._latlng = L.latLng(latlng);
        this._mRadius = radius;
        this._iRadius = radius2;
    },
    _project: function () {
        var lng = this._latlng.lng,
            lat = this._latlng.lat,
            map = this._map,
            crs = map.options.crs;

        if (crs.distance === L.CRS.Earth.distance) {
            var d = Math.PI / 180,
                latR = (this._mRadius / L.CRS.Earth.R) / d,
                latRI = (this._iRadius / L.CRS.Earth.R) / d,
                top = map.project([lat + latR, lng]),
                bottom = map.project([lat - latR, lng]),
                p = top.add(bottom).divideBy(2),
                lat2 = map.unproject(p).lat,
                lngR = Math.acos((Math.cos(latR * d) - Math.sin(lat * d) * Math.sin(lat2 * d)) /
                        (Math.cos(lat * d) * Math.cos(lat2 * d))) / d,
                lngRI = Math.acos((Math.cos(latRI * d) - Math.sin(lat * d) * Math.sin(lat2 * d)) /
                        (Math.cos(lat * d) * Math.cos(lat2 * d))) / d;

            this._point = p.subtract(map.getPixelOrigin());
            this._radius = isNaN(lngR) ? 0 : Math.max(Math.round(p.x - map.project([lat2, lng - lngR]).x), 1);
            this._radiusI = isNaN(lngRI) ? 0 : Math.max(Math.round(p.x - map.project([lat2, lng - lngRI]).x), 1);
            this._radiusY = Math.max(Math.round(p.y - top.y), 1);

        } else {
            var latlng2 = crs.unproject(crs.project(this._latlng).subtract([this._mRadius, 0])),
                latlng3 = crs.unproject(crs.project(this._latlng).subtract([this._iRadius, 0]));

            this._point = map.latLngToLayerPoint(this._latlng);
            this._radius = this._point.x - map.latLngToLayerPoint(latlng2).x;
            this._radiusI = this._point.x - map.latLngToLayerPoint(latlng3).x;
        }

        this._updateBounds();
    },
    _updatePath: function () {
        this._renderer._updateCircleDisk(this);
    },
});

L.SVG.prototype._updateCircleDisk = function(layer) {
    var p = layer._point,
        r = layer._radius,
        rI = layer._radiusI,
        r2 = layer._radiusY || r,
        dr = r - rI,
        arc = 'a' + r + ',' + r2 + ' 0 1,0 ',
        arcI = 'a' + rI + ',' + rI + ' 0 0,1 ';

    // drawing a circle with two half-arcs
    var d = layer._empty() ? 'M0 0' :
            'M' + (p.x - r) + ',' + p.y +
            arc +  (r * 2) + ',0 ' +
            'm' + (-dr) + ' 0' +
            arcI +  (-rI * 2) + ',0 ' +
            arcI +  (rI * 2) + ',0 ' +
            'm' + dr + ' 0' +
            arc + (-r * 2) + ',0 ';

    this._setPath(layer, d);
};

L.Canvas.prototype._updateCircleDisk = function(layer) {
    console.log('canvas _updateCircleDisk');
};

L.circleDisk = function (latlng, radius, radius2, options) {
    return new L.CircleDisk(latlng, radius, radius2, options);
};