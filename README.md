# gis-script
Simple GIS script that creates / updates database containing GPS tracking data.

## Usage
```
python3 main.py <route_file.kml> <country>
```

Before running the script:
- download needed country [OSM](http://download.geofabrik.de/),
- create .db file through QGIS, 
- export polylines
- save that layer as .kml named \<country>.
