import os
import sys
import threading
import urllib
from random import random, shuffle

import cv2
from numpy import count_nonzero, uint8, zeros
from pygeotile.point import Point
from pygeotile.tile import Tile

try:
    from fake_useragent import UserAgent  # https://github.com/hellysmile/fake-useragent
except:
    pass

import time


class YaBiGooo:
    """

    """

    def __init__(self, **kwargs):
        """

        :param mode:
        :param zoom:
        :param lat_start:
        :param lat_stop:
        :param lon_start:
        :param lon_stop:
        :param max_threads:
        :param DEBUG:
        :param ERR:
        """
        self.map = kwargs.get('map', 'bing')
        self.mode = kwargs.get('mode', 'satellite')
        self.zoom = kwargs.get('zoom', 2)
        self.x = kwargs.get('x', 2)
        self.y = kwargs.get('y', 2)
        self.img_dir = kwargs.get('img_dir', os.path.dirname(os.path.realpath(__file__)) + '/images')
        self.lat_start = kwargs.get('lat_start', 44.65)
        self.lat_stop = kwargs.get('lat_stop', 44.487067)
        self.lon_start = kwargs.get('lon_start', 33.376973)
        self.lon_stop = kwargs.get('lon_stop', 33.63)
        self.max_threads = kwargs.get('max_threads', 1)
        self.DEBUG = kwargs.get('DEBUG', True)
        self.ERR = kwargs.get('ERR', True)
        self.url = None

    def getTileUrl(self):
        """
        https://github.com/emdete/tabulae/blob/7751d7cd4d366f2ef4ba46dbc5b8f5fb2114ac58/provider.py
        """
        tile = Tile.from_google(self.x, self.y, self.zoom)

        if 'bing' in self.map:
            if self.mode == 'satellite':
                self.url = 'http://a0.ortho.tiles.virtualearth.net/tiles/a{}.jpeg?g=2'.format(tile.quad_tree)

        elif 'yandex' in self.map:
            if self.mode == 'map':
                self.url = 'https://vec02.maps.yandex.net/tiles?l=map&v=17.08.08-0&x=' + str(self.x) + \
                           '&y=' + str(self.y) + '&z=' + str(self.zoom) + '&scale=1&lang=ru_RU'
            elif self.mode == 'satellite':
                self.url = 'https://sat01.maps.yandex.net/tiles?l=sat&v=3.339.0&x=' + str(self.x) + \
                           '&y=' + str(self.y) + '&z=' + str(self.zoom) + '&lang=ru_RU'

    def stitchTiles(self):
        """

        :return:
        """
        print('Stitching Tiles ...')

        _, __, files = list(os.walk(self.img_dir))[0]

        files.sort(key=lambda x: (int(x.split('_')[3]), int(x.split('_')[4].split('.')[0])))

        tilX = lambda x: int(x.split('_')[3])
        tilY = lambda x: int(x.split('_')[4].split('.')[0])

        Xs = sorted(list(set([tilX(x) for x in files])))
        Ys = sorted(list(set([tilY(x) for x in files])))

        vert_hor_list = []

        # read error (no data) and empty (transparent) tile images
        errorImage = cv2.imread(os.path.dirname(os.path.realpath(__file__)) + '/Error.png')
        emptyImage = zeros([256, 256, 3], dtype=uint8)

        count = 0.
        tot = len(Xs) * len(Ys)

        # start_tile = Tile.for_latitude_longitude(self.lat_start, self.lon_start, self.zoom)
        # stop_tile = Tile.for_latitude_longitude(self.lat_stop, self.lon_stop, self.zoom)
        # start_x, start_y = start_tile.google
        # stop_x, stop_y = stop_tile.google
        # Xs = range(start_x, stop_x)
        # Ys = range(start_y, stop_y)

        # for x in Xs[80:100]:
        #     vertical_list = []
        #     for y in Ys[50:110]:

        for x in Xs:
            vertical_list = []
            for y in Ys:

                img = cv2.imread(self.img_dir + '/{}_{}_{}_{}_{}.jpeg'.format(self.map, self.mode, self.zoom, x, y))

                # # check if tile image has no data, and replace it with transparent tile
                if count_nonzero(img == errorImage) == 196608:
                    img = emptyImage

                vertical_list.append(img)

                if self.DEBUG:
                    count += 1.
                    prog = count / tot * 100
                    print('\rCompleted: {:.2f}%'.format(prog), end=' ')

            vertical_images = cv2.vconcat(vertical_list)
            vert_hor_list.append(vertical_images)

        del vertical_list, Xs, Ys, files  # clean up

        fnl_img = cv2.hconcat(vert_hor_list)

        del vert_hor_list  # clean up

        # fnl_img = None
        # for x in Xs[:210]:
        #     vertical = None
        #     for y in Ys[:110]:
        #         img = cv2.imread(self.img_dir + '/{}_{}_{}_{}_{}.jpeg'.format(self.map, self.mode, self.zoom, x, y))
        #         if vertical is None:
        #             vertical = img
        #         else:
        #             vertical = concatenate((vertical, img), axis=0)
        #         count += 1.
        #         prog = count / tot * 100
        #         print('\rCompleted: {:.2f}%'.format(prog), end=' ')
        #
        #     if fnl_img is None:
        #         fnl_img = vertical
        #     else:
        #         fnl_img = concatenate((fnl_img, vertical), axis=1)

        # fnl_img = cv2.convertScaleAbs(fnl_img)
        # fnl_img = cv2.cvtColor(fnl_img, cv2.COLOR_RGB2GRAY)
        # fnl_img = cv2.cvtColor(fnl_img, cv2.COLOR_GRAY2RGB)

        print('\nWriting to disk ...')

        # cv2.imwrite('stitched.png', fnl_img, [int(cv2.IMWRITE_PNG_COMPRESSION), 2])
        # cv2.imwrite('stitched.jpg', fnl_img, [int(cv2.IMWRITE_JPEG_QUALITY), 100, cv2.IMWRITE_JPEG_PROGRESSIVE, 1, cv2.IMWRITE_JPEG_OPTIMIZE, 1])
        # Note, that writing to bmp is faster than to jpeg and faster than to png
        # cv2.imwrite('stitched.bmp', fnl_img)

        cv2.imwrite('stitched.bmp', fnl_img)

        # from scipy.misc import imsave
        # imsave('stitched.jpg', fnl_img)

        print('Stitching Complete!')

    def georeference(self):
        """

        :return:
        """
        print('Georeferencing ...')

        tile_start = Tile.for_latitude_longitude(self.lat_start, self.lon_start, self.zoom)
        tile_stop = Tile.for_latitude_longitude(self.lat_stop, self.lon_stop, self.zoom)

        point_start = Point.from_latitude_longitude(max(tile_start.bounds[0][0], tile_start.bounds[1][0]),
                                                    min(tile_start.bounds[0][1], tile_start.bounds[1][1]))
        point_stop = Point.from_latitude_longitude(min(tile_stop.bounds[0][0], tile_stop.bounds[1][0]),
                                                   max(tile_stop.bounds[0][1], tile_stop.bounds[1][1]))

        # print(point_start.meters, point_stop.meters)

        if 'bing' in self.map or 'google' in self.map:
            a_srs = 'EPSG:3857'
        else:
            a_srs = 'EPSG:4326'

        os.system("gdal_translate -of GTiff -co BIGTIFF=YES -co NUM_THREADS=8 -a_ullr " +
                  str(point_start.meters[0]) + " " +
                  str(point_start.meters[1]) + " " +
                  str(point_stop.meters[0]) + " " +
                  str(point_stop.meters[1]) + " " +
                  "-a_srs " + a_srs + " stitched.bmp result.tif")
        # os.system(
        #     "gdalwarp --config GDAL_CACHEMAX 32000 -wm 1500 -dstalpha -srcnodata 0 -dstnodata 0 -overwrite -wo "
        #     "NUM_THREADS=8 result.tif result2.tif ")

        os.system(
                "gdalwarp -dstalpha -srcnodata 0 -dstnodata 0 -overwrite -wo NUM_THREADS=8 result.tif result2.tif ")
        os.system(
                "gdal_translate -of GTiff -co COMPRESS=LZW -co BIGTIFF=YES -co NUM_THREADS=8 result2.tif " +
                self.map + "_gcps.tif")

        os.remove('result.tif')
        os.remove('result2.tif')

        print('Georeferencing Complete!')

    def downloadTiles(self):
        """

        :return:
        """

        print('Downloading Tiles ...')

        try:
            ua = UserAgent()
        except:
            pass

        spawn_count = 0

        # convert lat/lon to google tiles
        start_tile = Tile.for_latitude_longitude(self.lat_start, self.lon_start, self.zoom)
        stop_tile = Tile.for_latitude_longitude(self.lat_stop, self.lon_stop, self.zoom)
        start_x, start_y = start_tile.google
        stop_x, stop_y = stop_tile.google

        # adding +1 for further range()
        stop_x += 1
        stop_y += 1

        if self.DEBUG: print(("x range", start_x, stop_x))
        if self.DEBUG: print(("y range", start_y, stop_y))
        if self.DEBUG: print(("Total Tiles: ", (stop_x - start_x) * (stop_y - start_y)))

        # set default UA if no fake_useragent specified
        user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_9; us-at) AppleWebKit/533.23.1 (KHTML, ' \
                     'like Gecko) ' \
                     'Version/5.0.5 Safari/533.21.3'
        headers = {'User-Agent': user_agent}

        if not os.path.exists(self.img_dir):
            os.mkdir(self.img_dir)

        # prepare shuffled list to randomly download tiles
        rndm_x = list(range(start_x, stop_x))
        rndm_y = list(range(start_y, stop_y))
        shuffle(rndm_x)
        shuffle(rndm_y)

        # prepare counter
        tot = (stop_x - start_x) * (stop_y - start_y)
        count = 0.

        for x in rndm_x:
            for y in rndm_y:

                self.x = x
                self.y = y
                self.getTileUrl()

                filename = self.img_dir + "/%s_%s_%d_%d_%d.%s" % (
                    self.map, self.mode, self.zoom, self.x, self.y, 'jpeg')

                if os.path.exists(filename):
                    count += 1
                elif not os.path.exists(filename):
                    try:
                        user_agent = ua.random
                        headers = {'User-Agent': user_agent}
                    except:
                        pass

                    if self.max_threads > 1:
                        threads = []
                        for i in range(self.max_threads):
                            t = threading.Thread(target=self.worker, args=(self.url, filename, user_agent, headers))
                            t.start()
                            threads.append(t)
                            spawn_count += 1
                            time.sleep(random() / self.max_threads)

                        if self.DEBUG:
                            # for not shuffled list
                            # x_percent = float((start_x - x)) / float(start_x - stop_x)
                            # y_percent = float((start_y - y)) / float(start_y - stop_y)
                            # print('\r-- Spawned Workers {:.0f}. Completed: x={:.2f}, y={:.2f} '.format(
                            #         spawn_count, 100 * x_percent, 100 * y_percent), end='  ')
                            # for shuffled list
                            count += 1.
                            prog = (count / tot) * 100
                            print('\rCompleted: {:.2f}%'.format(prog), end=' ')

                        for i in range(len(threads)):
                            threads[i].join()

                    else:
                        self.worker(self.url, filename, user_agent, headers, self.ERR)

                        if self.DEBUG:
                            # x_percent = float((start_x - x)) / float(start_x - stop_x)
                            # y_percent = float((start_y - y)) / float(start_y - stop_y)
                            # print('\r-- Completed: x={:.2f}, y={:.2f} '.format(
                            #         100 * x_percent, 100 * y_percent), end='  ')
                            count += 1.
                            prog = (count / tot) * 100
                            print('\rCompleted: {:.2f}%'.format(prog), end=' ')

                    if 'yandex' in self.url or 'google' in self.url:
                        time.sleep(5 + random())
        print("Download Complete!")

    @staticmethod
    def worker(url, filename, user_agent, headers, ERR=True):
        data = None
        try:
            req = urllib.request.Request(url, data=None, headers=headers)
            response = urllib.request.urlopen(req)
            data = response.read()
        except Exception as e:
            if ERR: print("--", filename, "->", e)
            sys.exit(1)
        if response.info().get_content_type() == 'text/html':
            if ERR: print(("-- Forbidden", filename))
            sys.exit(1)
        f = open(filename, 'wb')
        f.write(data)
        f.close()
