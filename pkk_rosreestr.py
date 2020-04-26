import math
import os
import urllib.parse
from itertools import product

import pyproj

from crawler import BaseCrawler
from tile_manager import BaseTileManager


class PKK(BaseTileManager):
    """PKK downloads and merges relevant map tiles from pkk.rosreestr.ru server.
    """

    def __init__(self, **kwargs):
        """
        :param map: choose the source among 'bing', 'yandex' or 'google' map
        :param mode: 'satellite' or 'road'
        :param x: generated x tile for download
        :param y: generated y tile for download
        :param img_dir: tiles download location
        :param lat_start: starting latitude
        :param lat_stop: ending latitude
        :param lon_start: starting longitude
        :param lon_stop: ending longitude
        :param max_threads: number of threads to spawn
        :param DEBUG: set if one wants to print debug info
        :param ERR: set if one wants to print error messages
        :param url: generated url for download
        :param urls: generated list of urls for download
        """
        super().__init__(**kwargs)


def get_osm_resolution(zoom):
    max_res = 156543.0339
    return max_res / 2 ** zoom


def get_osm_resolutions():
    max_res = 156543.0339
    return [max_res / 2 ** z for z in range(0, 18)]


def convert_ll2bbox(lat_start, lat_stop, lon_start, lon_stop):
    keys = ("xMin", "xMax", "yMin", "yMax")
    # bb = [lat_start, lat_stop, lon_start, lon_stop]
    # yy = sorted(list(map(elliptical_lat2y, bb[:2])))
    # xx = sorted(list(map(elliptical_lon2x, bb[2:])))
    P4326 = pyproj.Proj('epsg:4326')
    P3785 = pyproj.Proj('epsg:3785')

    xx, yy = pyproj.transform(P4326, P3785, (lat_start, lat_stop), (lon_start, lon_stop))
    xx = sorted(xx)
    yy = sorted(yy)

    return dict(list(zip(keys, [xx[0], xx[1], yy[0], yy[1]])))


def get_tile_step(pxl_res, tile_shape=(1024, 1024)):
    _dx = int(math.ceil((bbox["xMax"] - bbox["xMin"]) / (pxl_res * tile_shape[0])))
    _dy = int(math.ceil((bbox["yMax"] - bbox["yMin"]) / (pxl_res * tile_shape[1])))
    return _dx, _dy


def get_tile_bbox(xx, yy):
    xMin = bbox["xMin"] + (xx * resolution * tile_size[0])
    xMax = bbox["xMin"] + ((xx + 1) * resolution * tile_size[0])
    yMin = bbox["yMin"] + (yy * resolution * tile_size[1])
    yMax = bbox["yMin"] + ((yy + 1) * resolution * tile_size[1])
    return [xMax, yMax, xMin, yMin]


# lat_start = 63.070454
# lat_stop = 62.981059
# lon_start = 74.329955
# lon_stop = 74.527553

lat_start = 63.052541
lat_stop = 63.050023
lon_start = 74.395752
lon_stop = 74.402082
zoom = 16
resolution = get_osm_resolution(zoom)

bbox = convert_ll2bbox(lat_start, lat_stop, lon_start, lon_stop)
# tile_shape = optimize_tile_size(50)
tile_size = (1024, 1024)
dx, dy = get_tile_step(resolution, tile_size)
p = list(product(range(dx), range(dy)))

print('Beginning file download with urllib2...')
prefix = './images/'

# url = "https://pkk.rosreestr.ru/arcgis/rest/services/PKK6/CadastreSelected/MapServer/export"
url = "https://pkk.rosreestr.ru/arcgis/rest/services/PKK6/Thematic/MapServer/export"

urls = []
out_files = []

for (_xx, _yy) in p:
    # layers = list(map(str, range(0, 20)))
    layers = ('8')
    params = {
        "dpi": 96,
        "transparent": "true",
        "format": "PNG32",
        "layers": f"show:{','.join(layers)}",
        "bbox": ",".join(map(str, get_tile_bbox(_xx, _yy))),
        "bboxSR": 102100,
        "imageSR": 102100,
        "size": f"{','.join(str(e) for e in tile_size)}",
        "f": "image"
    }

    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.parse.urlencode(query)
    meta_url = urllib.parse.urlunparse(url_parts)
    file_name = f"{_xx}_{_yy}.png"

    urls.append(meta_url)
    out_files.append(f'images/{file_name}')

if not os.path.exists('images'):
    os.makedirs('images')

# Download all urls into out_files
async_download = BaseCrawler(urls, out_files)
async_download.run()

# urllib.request.urlretrieve(meta_url, prefix + 'tmp.png')
# size = os.stat(prefix + 'tmp.png').st_size
# if size > 6527:
#     if not os.path.exists(prefix + str(z)):
#         os.makedirs(prefix + str(z))
#     if not os.path.exists(prefix + str(z) + '/' + str(x)):
#         os.makedirs(prefix + str(z) + '/' + str(x))
#     os.replace(prefix + 'tmp.png', prefix + str(z) + '/' + str(x) + '/' + str(y) + '.png')
