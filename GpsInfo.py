from PIL.ExifTags import TAGS, GPSTAGS
import numpy as np

def get(data, key):
	if key in data: return data[key]
	return None

def frac(value):
	return float(value[0])/float(value[1])

def to_deg(value):
	degs = [ frac(value[i]) for i in range(len(value))]
	return degs[0] + (degs[1]/60.0) + (degs[2] / 3600.0)

def getlatlngs(info):
	exif_data = {}
	targets, g = ["GPSLatitude", 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef'], "GPSInfo"
	if not info: return
	for tag, value in info.items():
		decoded = TAGS.get(tag, tag)
		if decoded == g:
			gps_data = {}
			for t in value:
				sub_decoded = GPSTAGS.get(t, t)
				gps_data[sub_decoded] = value[t]
			exif_data[decoded] = gps_data
		else:
			exif_data[decoded] = value

	if not g in exif_data: return None, None
	gps = [get(exif_data[g], item) for item in targets]	
	if gps[0] and gps[1] and gps[2] and gps[3]:
		lat, lng = to_deg(gps[0]), to_deg(gps[2])
		if gps[1] != "N": lat = 0 - lat
		if gps[3] != "E": lng = 0 - lng
	return lat, lng