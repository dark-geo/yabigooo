import os
import urllib.parse
from random import randint

from pygeotile.tile import Tile

from crawler import BaseCrawler


class BaseTileManager:
    """TileManager is a Base class for downloading and merging relevant map tiles from different servers."""

    def __init__(self, **kwargs):
        """
        :param map: choose the source among 'pkk.rosreestr', 'bing', 'yandex' or 'google' map
        :param mode: 'cadastre' or 'thematic' for 'pkk', 'satellite' or 'road' for other
        :param zoom: zoom level
        :param x: generated google x tile for download
        :param y: generated google y tile for download
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
        self.map = kwargs.get('road', 'pkk')
        self.mode = kwargs.get('mode', 'thematic')
        self.zoom = kwargs.get('zoom', 16)
        self.x = kwargs.get('x', 2)
        self.y = kwargs.get('y', 2)
        self.img_dir = kwargs.get('img_dir', os.path.dirname(os.path.realpath(__file__)) + '/images')
        self.lat_start = kwargs.get('lat_start', 63.052541)
        self.lat_stop = kwargs.get('lat_stop', 63.050023)
        self.lon_start = kwargs.get('lon_start', 74.395752)
        self.lon_stop = kwargs.get('lon_stop', 74.402082)
        self.max_threads = kwargs.get('max_threads', 1)
        self.DEBUG = kwargs.get('DEBUG', True)
        self.ERR = kwargs.get('ERR', True)
        self.url = None
        self.urls = []
        self.fns = []
        self.headers = []

        if not os.path.exists(self.img_dir):
            os.mkdir(self.img_dir)

    def prepare_urls_for_download(self):
        # convert lat/lon to google tiles
        start_tile = Tile.for_latitude_longitude(self.lat_start, self.lon_start, self.zoom)
        stop_tile = Tile.for_latitude_longitude(self.lat_stop, self.lon_stop, self.zoom)
        start_x, start_y = start_tile.google
        stop_x, stop_y = stop_tile.google

        # check, that start tile numbers less than stop ones
        if start_x > stop_x:
            if self.DEBUG: print("switching start and stop x tiles", start_x, stop_x)
            stop_x, start_x = start_x, stop_x
        if start_y > stop_y:
            if self.DEBUG: print("switching start and stop y tiles", start_y, stop_y)
            stop_y, start_y = start_y, stop_y

        # adding +1 for further range()
        stop_x += 1
        stop_y += 1

        if self.DEBUG: print("x range", start_x, stop_x)
        if self.DEBUG: print("y range", start_y, stop_y)
        if self.DEBUG: print("Total Tiles: ", (stop_x - start_x) * (stop_y - start_y))

        # prepare shuffled list to randomly download tiles
        random_x = list(range(start_x, stop_x))
        random_y = list(range(start_y, stop_y))
        # shuffle(random_x)
        # shuffle(random_y)

        # generating list of urls, filenames and fake UA for download
        for x in random_x:
            for y in random_y:

                self.x = x
                self.y = y

                fn = self.img_dir + "/%s_%s_%d_%d_%d.%s" % (self.map, self.mode, self.zoom, self.x, self.y, 'png')

                # skip if already downloaded
                if os.path.exists(fn):
                    continue
                elif not os.path.exists(fn):
                    self._get_tile_url()  # getting tile url

                    self.urls.append(self.url)  # appending url to list of urls
                    self.fns.append(fn)  # appending corresponding filename

    def _get_tile_url(self):
        raise NotImplementedError


class BingTileManager(BaseTileManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.map = 'bing'
        self.mode = kwargs.get('mode', 'satellite')

    def _get_tile_url(self):
        tile = Tile.from_google(self.x, self.y, self.zoom)

        if self.mode == 'road':
            self.url = f'http://ecn.dynamic.t{randint(0, 3)}.' \
                       f'tiles.virtualearth.net/comp/CompositionHandler/' \
                       f'r{tile.quad_tree}.jpeg?mkt=ru-ru&it=G,VE,BX,L,LA&shading=hill&g=94'
        elif self.mode == 'satellite':
            self.url = f'http://a{randint(0, 3)}.' \
                       f'ortho.tiles.virtualearth.net/tiles/a{tile.quad_tree}.jpeg?g=94'


class YandexTileManager(BaseTileManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.map = 'yandex'
        self.mode = kwargs.get('mode', 'satellite')

    def _get_tile_url(self):
        tile = Tile.from_google(self.x, self.y, self.zoom)

        if 'yandex' in self.map:
            if self.mode == 'road':
                self.url = 'https://vec02.maps.yandex.net/tiles?l=map&v=17.08.08-0&x=' + str(self.x) + \
                           '&y=' + str(self.y) + '&z=' + str(self.zoom) + '&scale=1&lang=ru_RU'
            elif self.mode == 'satellite':
                self.url = 'https://core-sat.maps.yandex.net/tiles?l=sat&v=3.564.0&' \
                           f'x={self.x}&y={self.y}&z={self.zoom}&scale=1&lang=ru_RU'


class PkkTileManager(BaseTileManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.map = 'pkk'
        self.mode = kwargs.get('mode', 'thematic')

        if self.mode == 'cadastre':
            self.url = "https://pkk.rosreestr.ru/arcgis/rest/services/PKK6/CadastreSelected/MapServer/export"
        elif self.mode == 'thematic':
            self.url = "https://pkk.rosreestr.ru/arcgis/rest/services/PKK6/Thematic/MapServer/export"

    def _get_tile_url(self):
        tile = Tile.from_google(self.x, self.y, self.zoom)

        # NB! Don't forget that bbox and tile pyramid is calculated for standard 256x256 tile sizes.
        # One will need to keep that in mind when merging and georeferencing
        tile_size = (1024, 1024)
        # convert bbox into meters
        _bbox = tile.bounds
        _bbox = list(b.meters for b in _bbox)
        _bbox = [item for t in _bbox for item in t]
        layers = list(map(str, range(0, 20)))
        # layers = ('8',)
        params = {
            "dpi": 96,
            "transparent": "true",
            "format": "PNG32",
            "layers": f"show:{','.join(layers)}",
            "bbox": ",".join(map(str, _bbox)),
            "bboxSR": 102100,
            "imageSR": 102100,
            "size": f"{','.join(str(e) for e in tile_size)}",
            "f": "image"
        }

        # updating url request with params
        url_parts = list(urllib.parse.urlparse(self.url))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urllib.parse.urlencode(query)
        self.url = urllib.parse.urlunparse(url_parts)


if __name__ == "__main__":
    # tile_manager = PkkTileManager()
    # tile_manager.prepare_urls_for_download()
    # # Download all urls into out_files
    # async_download = BaseCrawler(tile_manager.urls, tile_manager.fns)
    # async_download.run()
    #
    # tile_manager = BingTileManager()
    # tile_manager.prepare_urls_for_download()
    # # Download all urls into out_files
    # async_download = BaseCrawler(tile_manager.urls, tile_manager.fns)
    # async_download.run()

    tile_manager = YandexTileManager()
    tile_manager.prepare_urls_for_download()
    # Download all urls into out_files
    async_download = BaseCrawler(tile_manager.urls, tile_manager.fns)
    async_download.run()
