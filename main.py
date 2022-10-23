import os
from flask import Flask, render_template
from database.database import Database
import database.SQL_requests as R
from utils.utils import read_config
from math import fabs
from colour import Color
import bisect

config = read_config("config.json")
DB = Database(config)

app = Flask(__name__, static_url_path="/static", static_folder="static")


separator = '~'


def floatListToString(data):
    return separator.join(list(map(str, data)))


def stringToFloatList(data):
    return list(map(float, data.split(separator)))


# def dist(x1,y1, x2,y2):
#     return sqrt((x2-x1)**2 + (y2-y1)**2)
def list_check(_list, _value):
    return bisect.bisect_right(_list, _value)

def square(x1, y1, x2, y2, x3, y3):
    return 0.5 * fabs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))


@app.route('/')
def mainPage():
    polygons = []
    points = set()
    color_1 = Color("#F4AE9F")
    color_2 = Color("#85240F")
    colors_bar = list(color_2.range_to(color_1, 10))
    colors_svg = list(color_1.range_to(color_2, 351))
    elements = DB.execute(R.selectElements, [], False, True)

    minPer = minX = minY =  99999999999999
    maxPer = maxX = maxY = -99999999999999

    for el in elements:
        n1 = DB.execute(R.selectNodeById, [el['n1']])
        n2 = DB.execute(R.selectNodeById, [el['n2']])
        n3 = DB.execute(R.selectNodeById, [el['n3']])

        points.add(floatListToString([n1['x'], n1['y']]))
        points.add(floatListToString([n2['x'], n2['y']]))
        points.add(floatListToString([n3['x'], n3['y']]))

        minX = min(minX, n1['x'], n2['x'], n3['x'])
        minY = min(minY, n1['y'], n2['y'], n3['y'])
        maxX = max(maxX, n1['x'], n2['x'], n3['x'])
        maxY = max(maxY, n1['y'], n2['y'], n3['y'])

        per = square(n1['x'], n1['y'], n2['x'], n2['y'], n3['x'], n3['y'])
        maxPer = max(maxPer, per)
        minPer = min(minPer, per)

        polygons.append([n1['x'], n1['y'], n2['x'], n2['y'], n3['x'], n3['y'], per, str(per)[:5]])

    resultPoints = list(map(stringToFloatList, points))

    delt = (350 - 0) / 350
    data = [0]
    for i in range(350):
        data.append(data[-1] + delt)



    for p in polygons:
        lc = list_check(data, p[6])
        p[6] = colors_svg[lc]
    print(points)
    return render_template('index.html', polygons=polygons, points=resultPoints,
                           minX=minX, minY=minY, width=maxX-minX, height=maxY-minY, colors=colors_bar)


@app.errorhandler(404)
def error404(err):
    print(err)
    return "404 страница не найдена"


@app.errorhandler(500)
def error500(err):
    print(err)
    return "500 внутренняя ошибка сервера"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', config['listen_port']))
    app.run(port=port, debug=bool(config['debug']))
