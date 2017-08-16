# Yandex/Bing/Google Map Tile Downlaoder/Stitcher

**Requirements:** Python 3, cv2, pygeotile, fake_useragent, tifffile

**Input:** Top Latitude, Top Longitude, Bottom Latitude, Bottom Longitude

**Output:** Georeferenced image

### Running instructions:

YaBiGooo.py downloads the relevant map tiles from corresponding servers. Bing by default.

**NOTE:** There is a small random sleep time set for each tile.
          While Bing doesn't ban you it is better to use 1 thread, as sleep time is randomly chosen between 0 and 1 sec.
          For Yandex and Google there is a larger random sleep time set for each tile.
          All of the tiles are randomly shuffled before download.
          Fake user agent is used for tiles download.

```Batchfile
from YaBiGooo import YaBiGooo
b = YaBiGooo(zoom=19, max_threads=1, img_dir='/home/magican/Documents/prj/repos/yabigooo/images/', DEBUG=True,
            lat_start=44.7, lat_stop=44.65)

```

After all of the tiles have been downloaded, they can be merged and georeferenced.

```Batchfile
b.stitchTiles()
b.georeference()
```