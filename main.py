import sys
import math
import os
import time
from copy import deepcopy

kml_head = '''<?xml version="1.0" encoding="UTF-8"?>\n
              <kml xmlns="http://www.opengis.net/kml/2.2">\n
              <Document id="root_doc">\n'''
kml_tail = '''</Document>\n
              </kml>'''
kml_body_template = '''<Placemark>\n
                            <name>Line{}</name>\n
                            <description>{}</description>\n
                            <LineString>\n
                                <coordinates>{},{} {},{}</coordinates>
                            </LineString>\n
                            </Placemark>\n'''

polylines_template = '{}_polylines.kml'
eps = 1e-4

# https://en.wikipedia.org/wiki/Decimal_degrees
# 1e-8 degrees = 1.0247mm
conversion_coef = 1.0247
quantum = 1e-8

route_lines = [[(None, None), (None, None), None]]     # ((x0, y0), (x1, y1), d)


def dist(p1, p2, m):
    if p2[0] - p1[0] < eps and p2[1] - p1[1] < eps:
        return math.fabs(p1[0] - m[0]) + math.fabs(p1[1] - m[1])
    return math.fabs((p2[1] - p1[1]) * m[0] - (p2[0] - p1[0]) * m[1] + p2[0] * p1[1] - p2[1] * p1[0]) /\
           math.sqrt((p2[1] - p1[1]) ** 2 + (p2[0] - p1[0]) ** 2)


def to_milimeters(d):
    return d / quantum * conversion_coef


if __name__ == '__main__':
    x_max = -sys.float_info.max
    x_min = sys.float_info.max
    y_max = -sys.float_info.max
    y_min = sys.float_info.max
    nlines = 0

    with open(sys.argv[1], 'r') as route_file:
        start_time = time.time()
        i = 0
        for line in route_file.readlines():
            if line.startswith('<gx:coord>'):
                tags = line.replace('<gx:coord>', '').replace('</gx:coord>', '').replace('\n', '').split(' ')
                x, y = float(tags[0]), float(tags[1])
                route_lines[i][1] = (x, y)
                route_lines.append([(x, y), None, -1])
                i += 1

                # find edge route points
                if x > x_max:
                    x_max = deepcopy(x)
                if x < x_min:
                    x_min = deepcopy(x)
                if y > y_max:
                    y_max = deepcopy(y)
                if y < y_min:
                    y_min = deepcopy(y)
        # remove first and last element
        nlines = deepcopy(i)
        route_lines = route_lines[1:-1]
        print('Read route file {0} in {1:.2f}s'.format(sys.argv[1], time.time() - start_time))

    # select real roads that are (at least partly) inside edge points and store
    selected_roads = [[(None, None), (None, None)]]
    polylines_path = polylines_template.format(sys.argv[2])
    with open(polylines_template.format(sys.argv[2]), 'r') as fpoly:
        start_time = time.time()
        i = 0
        for line in fpoly.readlines():
            if 'LineString' in line:
                stripped = line\
                    .replace('<LineString><coordinates>', '')\
                    .replace('</coordinates></LineString>', '')\
                    .strip()
                coordinates = stripped.split(' ')
                for point in coordinates:
                    x, y = float(point.split(',')[0]), float(point.split(',')[1])
                    selected_roads[i][1] = (x, y)
                    selected_roads.append([(x, y), None])
                    i += 1
        selected_roads = selected_roads[1:-1]
        print('Read polylines file {0} in {1:.2f}s'.format(polylines_path, time.time() - start_time))

    # for each route polyline find closest road line
    i = 0
    start_time = time.time()
    for route_line in route_lines:
        mean_point = ((route_line[0][0] + route_line[1][0]) / 2, (route_line[0][1] + route_line[1][1]) / 2)
        min_dist = sys.float_info.max
        for road in selected_roads:
            d = dist(road[0], road[1], mean_point)
            if d < min_dist:
                min_dist = d
        i += 1
        # store calculated error to route data
        m, s = divmod(time.time() - start_time, 60)
        h, m = divmod(m, 60)
        print('Calculated {0}/{1} route lines\'s errors in {2:0>2}:{3:0>2}:{4:05.2f} -> {5:.4f}mm'
              .format(i, nlines, int(h), int(m), s, to_milimeters(min_dist)))
        route_line[2] = to_milimeters(min_dist)

    # generate new KML where you store coordinates and GPS data errors
    kml_body = ''
    print('Generating new .kml with line coordinates and GPS data errors.')
    for idx, line in enumerate(route_lines):
        kml_body += kml_body_template.format(idx, line[2], line[0][0], line[0][1], line[1][0], line[1][1])
    kml_string = kml_head + kml_body + kml_tail

    route_path, _ = os.path.splitext(sys.argv[1])
    gen_route_path = route_path + '_gen.kml'
    print('Writing result to {}.'.format(gen_route_path))
    with open(gen_route_path, 'w') as route_file:
        route_file.write(kml_string)
