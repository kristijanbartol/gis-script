import sys
import math
from copy import deepcopy

polylines_template = '{}_polylines.kml'

route_lines = [[(None, None), (None, None), None]]     # ((x0, y0), (x1, y1), d)


def dist(p1, p2, m):
    return math.fabs((p2[1] - p1[1]) * m[0] - (p2[0] - p1[0]) * m[1] + p2[0] * p1[1] - p2[1] * p1[0]) / \
           math.sqrt((p2[1] - p1[1]) ** 2 + (p2[0] - p1[0]) ** 2)


if __name__ == '__main__':
    x_max = -sys.float_info.max
    x_min = sys.float_info.max
    y_max = -sys.float_info.max
    y_min = sys.float_info.max

    with open(sys.argv[1]) as route_file:
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
                route_lines = route_lines[1:-1]

    # select real roads that are (at least partly) inside edge points and store
    selected_roads = [[(None, None), (None, None)]]
    with open(polylines_template.format(sys.argv[2])) as fpoly:
        i = 0
        for line in fpoly.readlines():
            if 'LineString' in line:
                stripped = line\
                    .replace('<LineString><coordinates>', '')\
                    .replace('</coordinates></LineString>', '')\
                    .strip()
                print(stripped)
                input()
                coordinates = stripped.split(' ')
                for point in coordinates:
                    x, y = float(point.split(',')[0]), float(point.split('')[1])
                    selected_roads[i][1] = (x, y)
                    selected_roads.append([(x, y), None])
                    print(x, y)
                    input()
                i += 1
    selected_roads = selected_roads[1:-1]

    # za svaku liniju rute nadi najblizu liniju stvarne prometnice
    for route_line in route_lines:
        mean_point = ((route_line[0][0] + route_line[1][0]) / 2, (route_line[0][1] + route_line[1][1]) / 2)
        min_dist = sys.float_info.max
        for road in selected_roads:
            d = dist(road[0], road[1], mean_point)
            if d < min_dist:
                min_dist = d
        # izracunatu udaljenost spremi u d
        route_line[2] = min_dist

    # generiraj novi KML u kojem se nalaze podaci o koordinatama linija i pogreskama (description)
    pass


# (None, (x0, y0)), ((x0, y0), None)
# (None, (x0, y0)), ((x0, y0), (x1, y1)), ((x1, y1), None)
