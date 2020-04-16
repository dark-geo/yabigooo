# Yandex/Bing/Google Map Tile Downloader/Stitcher

**Requirements:** Python 3, cv2, pygeotile, fake_useragent, tifffile

**Input:** Top Latitude, Top Longitude, Bottom Latitude, Bottom Longitude

**Output:** Georeferenced image

### Running instructions:

YaBiGooo.py downloads the relevant map tiles from corresponding servers. Bing by default.

**NOTE:** There is a small random sleep time set for each tile.
          While Bing doesn't ban you it is better to use 1 thread, as sleep time is randomly chosen between 0 and 1 sec.
          For Yandex and Google there is a larger random sleep time set for each tile.
          All of the tiles are randomly shuffled before download.
          Fake user agent is used for UA simulation.

### Understanding Scale and Resolution

| Zoom Level  | Scale (m/pixel)  | Zoom Level  | Scale (m/pixel) |
|-------------|------------------|-------------|-----------------|
| 1           | 78271.52         | 11          | 76.44           |
| 2           | 39135.76         | 12          | 38.22           |
| 3           | 19567.88         | 13          | 19.11           |
| 4           | 9783.94          | 14          | 9.55            |
| 5           | 4891.97          | 15          | 4.78            |
| 6           | 2445.98          | 16          | 2.39            |
| 7           | 1222.99          | 17          | 1.19            |
| 8           | 611.50           | 18          | 0.60            |
| 9           | 305.75           | 19          | 0.30            |
| 10          | 152.87           |             |                 |

### HowTo Download and Stitch Tiles

Example over Kholmogory OilField

```Batchfile
from YaBiGooo import YaBiGooo
b = YaBiGooo(zoom=17, max_threads=1, DEBUG=True,
            lat_start=63.070454, lat_stop=62.981059,
            lon_start=74.329955, lon_stop=74.527553)
b.downloadTiles()
```

After all of the tiles have been downloaded, they can be merged and georeferenced.

```Batchfile
b.stitchTiles()
b.georeference()
```

### Compare Resolutions

```Batchfile
b.generate_previews()
```

#### Facilities - Example of an area infrastructure object

facilitie_1

```Batchfile
from YaBiGooo import YaBiGooo
b = YaBiGooo(zoom=19, max_threads=4, DEBUG=True,
            lat_start=63.052541, lat_stop=63.050023,
            lon_start=74.395752, lon_stop=74.402082)
b.downloadTiles()
b.stitchTiles()
b.georeference()
b.generate_previews()
```

facilitie_2

```Batchfile
from YaBiGooo import YaBiGooo
b = YaBiGooo(zoom=19, max_threads=4, DEBUG=True,
            lat_start=63.024930, lat_stop=63.022925,
            lon_start=74.348851, lon_stop=74.354650)
b.downloadTiles()
b.stitchTiles()
b.georeference()
b.generate_previews()
```

#### Cross Roads

```Batchfile
from YaBiGooo import YaBiGooo
b = YaBiGooo(zoom=19, max_threads=4, DEBUG=True,
            lat_start=63.026852, lat_stop=63.025073,
            lon_start=74.425255, lon_stop=74.432208)
b.downloadTiles()
b.stitchTiles()
b.georeference()
b.generate_previews()
```

#### Бездорожье

бездорожье_1

```Batchfile
from YaBiGooo import YaBiGooo
b = YaBiGooo(zoom=19, max_threads=4, DEBUG=True,
            lat_start=63.053533, lat_stop=63.051569,
            lon_start=74.394575, lon_stop=74.400202)
b.downloadTiles()
b.stitchTiles()
b.georeference()
b.generate_previews()
```
бездорожье_2

```Batchfile
from YaBiGooo import YaBiGooo
b = YaBiGooo(zoom=19, max_threads=4, DEBUG=True,
            lat_start=62.991970, lat_stop=62.991109,
            lon_start=74.429545, lon_stop=74.432571)
b.downloadTiles()
b.stitchTiles()
b.georeference()
b.generate_previews()
```

#### Flare Zone

```Batchfile
from YaBiGooo import YaBiGooo
b = YaBiGooo(zoom=19, max_threads=4, DEBUG=True,
            lat_start=62.997186, lat_stop=62.995970,
            lon_start=74.382949, lon_stop=74.385969)
b.downloadTiles()
b.stitchTiles()
b.georeference()
b.generate_previews()
```

#### Small Bridge

```Batchfile
from YaBiGooo import YaBiGooo
b = YaBiGooo(zoom=19, max_threads=4, DEBUG=True,
            lat_start=63.040489, lat_stop=63.039655,
            lon_start=74.454551, lon_stop=74.457410)
b.downloadTiles()
b.stitchTiles()
b.georeference()
b.generate_previews()
```

#### Ponds/Small Lakes

lakes

```Batchfile
from YaBiGooo import YaBiGooo
b = YaBiGooo(zoom=19, max_threads=4, DEBUG=True,
            lat_start=63.048581, lat_stop=63.040566,
            lon_start=74.389181, lon_stop=74.420831)
b.downloadTiles()
b.stitchTiles()
b.georeference()
b.generate_previews()
```

ponds

```Batchfile
from YaBiGooo import YaBiGooo
b = YaBiGooo(zoom=19, max_threads=4, DEBUG=True,
            lat_start=63.059485, lat_stop=63.056476,
            lon_start=74.513884, lon_stop=74.521073)
b.downloadTiles()
b.stitchTiles()
b.georeference()
b.generate_previews()
```
