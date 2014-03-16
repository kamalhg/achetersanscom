import requests


class WrongAddressError(Exception):
    pass

def geo_from_address(address):
    #url = "http://services.gisgraphy.com//geocoding/geocode?address='%s'&country=FR&format=json" % address
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=true&key=AIzaSyDybLZ5Wudjcjumgn8sZH9T3ko9FtOwduw" % address
    r = requests.get(url)
    try:
        json = r.json()
        lat = json['results'][0]['geometry']['location']['lat']
        lng = json['results'][0]['geometry']['location']['lng']
        pt = "POINT(%s %s)" % (lng, lat)
        return pt
    except:
        raise WrongAddressError


def address_from_geo(lat, lng):
    url = "https://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=true&key=AIzaSyDybLZ5Wudjcjumgn8sZH9T3ko9FtOwduw" % (lat, lng)
    r = requests.get(url)
    try:
        json = r.json()
        address = json['results'][0]['formatted_address']
        return address
    except:
        raise WrongAddressError
