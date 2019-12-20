from random import random
import matplotlib.pyplot as plt
import matplotlib.tri
from matplotlib.patches import Circle
from imageio import imread, mimsave
from warnings import filterwarnings
from PIL import Image
from os.path import basename, dirname
from os import listdir, remove

class Point:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __repr__(self):
        return "( " + str(self.x) + ", " + str(self.y) + " )"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def distance(self, other):
        return pow(pow(self.x - other.x, 2) + pow(self.y - other.y, 2), 0.5)

    def is_in_circle(self, triangle):
        O = triangle.outer_center()
        return O.distance(triangle.vertexs[0]) > O.distance(self)

class Edge:
    def __init__(self, a = Point(), b = Point()):
        self.vertexs = [a, b]

    def __repr__(self):
        return ' < ' + str(self.vertexs) + ' > '

    def __eq__(self, other):
        return (self.vertexs[0] == other.vertexs[0] and self.vertexs[1] == other.vertexs[1])\
               or (self.vertexs[0] == other.vertexs[1] and self.vertexs[1] == other.vertexs[0])

class Triangle:
    def __init__(self, a: Point, b: Point, c: Point):
        self.vertexs = [a, b, c]
        self.edge = [Edge(a, b), Edge(b, c), Edge(c, a)]

    def __repr__(self):
        return 'triangle vertexs：' + '< ' + str(self.vertexs) + ' >'
    
    def outer_center(self):
        A, B, C = self.vertexs
        O = Point()

        D = 4 * ((B.x - A.x) * (C.y - A.y) - (C.x - A.x) * (B.y - A.y))

        D1 = 2 * ((B.x + A.x) * (B.x - A.x) + (B.y + A.y) * (B.y - A.y)) * (C.y - A.y) - 2 * (
        (C.x + A.x) * (C.x - A.x) + (C.y + A.y) * (C.y - A.y)) * (B.y - A.y)
        D2 = 2 * ((C.x + A.x) * (C.x - A.x) + (C.y + A.y) * (C.y - A.y)) * (B.x - A.x) - 2 * (
        (B.x + A.x) * (B.x - A.x) + (B.y + A.y) * (B.y - A.y)) * (C.x - A.x)

        O.x = D1 / D
        O.y = D2 / D
        return O

    def inner_center(self):
        A, B, C = self.vertexs
        c, a, b = A.distance(B), B.distance(C), C.distance(A)
        X = (a * A.x + b * B.x + c * C.x) / (a + b + c)
        Y = (a * A.y + b * B.y + c * C.y) / (a + b + c)
        return Point(X, Y)

class Delaunay:
    def __init__(self, width = 50, height = 50, total = 30, mode = "super"):
        self.triangles = []

        if mode == "super":
            A = Point(-width * 10000, -height * 10000)
            B = Point(width * 10000, -height * 10000)
            C = Point(width * 10000, height * 10000)
            D = Point(-width * 10000, height * 10000)
        elif mode == "picture":
            A = Point(0, 0)
            B = Point(width, 0)
            C = Point(width, height)
            D = Point(0, height)

        self.frame = [A, B, C, D]

        T1 = Triangle(A, B, D)
        T2 = Triangle(B, C, D)

        self.triangles.append(T1)
        self.triangles.append(T2)

    def add_point(self, point):
        edge_buffer = []
        for triangle in self.triangles[:]:
            if point.is_in_circle(triangle):
                edge_buffer.extend(triangle.edge)
                self.triangles.remove(triangle)
        edge_buffer = list(filter(lambda x: edge_buffer.count(x) == 1, edge_buffer))
        for edge in edge_buffer:
            self.triangles.append(Triangle(edge.vertexs[0], edge.vertexs[1], point))

    def remove_supervertexs(self, op, save):
        for triangle in self.triangles[:]:
            v = triangle.vertexs
            is_frame = [p in self.frame for p in v]
            if any(is_frame):
                self.triangles.remove(triangle)
                self.clean_triangles(triangle, op, save)

    def clean_triangles(self, triangle, op, save):
        global count
        frame = list(filter(lambda x: x in self.frame, triangle.vertexs))
        for f in frame:
            for v in triangle.vertexs:
                if f != v:
                    plt.plot([v.x, f.x], [v.y, f.y], "w")
        if op == 'y':
            plt.pause(0.001)
            if save == 'y':
                plt.savefig(path + "\\%s.png" % count)
        count += 1

    def draw_triangles(self, mode, op, save, path):
        global count
        for i, triangle in enumerate(self.triangles):
            v = triangle.vertexs
            plt.plot([v[0].x, v[1].x], [v[0].y, v[1].y], mode)
            plt.plot([v[0].x, v[2].x], [v[0].y, v[2].y], mode)
            plt.plot([v[1].x, v[2].x], [v[1].y, v[2].y], mode)
            if op == 'y':
                plt.pause(0.001)
                if save == 'y':
                    plt.savefig(path + "\\%s.png" % count)
            count += 1

    def draw_circles(self, ax):
        for triangle in self.triangles:
            O = triangle.circle_center()
            ax.add_patch(Circle(xy = (O.x, O.y), radius = O.distance(triangle.vertexs[0]), fill = False))

class Triangulate_Picture:
    def __init__(self, path, pixel_num = 100):
        with Image.open(path) as img:
            self.img = img.convert('RGBA')
        self.path = path
        self.pixel_num = pixel_num
        self.name = basename(path)[:-4]

    def get_pixel_color(self, x, y):
        return self.img.load()[x, self.img.height - y - 1]

    def draw_picture(self):
        width, height, total = self.img.width, self.img.height, self.pixel_num

        dpi = 50
        fig = plt.gcf()
        fig.set_size_inches(width / dpi, height / dpi)
        ax = fig.add_subplot(111)

        dt = Delaunay(width, height, total, "picture")

        vertices = [Point(width * random(), height * random()) for i in range(total)]
        for point in vertices:
            dt.add_point(point)
        trs = dt.triangles

        frame = [Point(0, 0), Point(width, 0), Point(width, height), Point(0, height)]
        vertices.extend(frame)
        X = [i.x for i in vertices]
        Y = [i.y for i in vertices]

        center = [tri.inner_center() for tri in trs]
        color = [self.get_pixel_color(int(p.x), int(p.y)) for p in center]

        for i in range(len(trs)):
            x = [j.x for j in trs[i].vertexs]
            y = [j.y for j in trs[i].vertexs]
            c = [j / 255 for j in color[i]]
            plt.fill(x, y, facecolor = c, edgecolor = c)

        plt.axis('off')
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        plt.savefig(r"%s\%s_%s.png" % (dirname(self.path), self.name, str(self.pixel_num)), transparent=True, pad_inches=0)
        plt.show()

def do_delaunay(X, Y, vertices, width, height, total, op, circle, save, path):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    center = Point(sum(X) / total, sum(Y) / total)
    ax.set(xlim=(center.x - width, center.x + width), ylim=(center.y - height, center.y + height))
    plt.scatter(X, Y)
    if path:
        plt.savefig(path + "\\%s.png" % 0)
    plt.pause(0.01)

    dt = Delaunay(width, height, total)

    for point in vertices:
        dt.add_point(point)

    ax.triplot(matplotlib.tri.Triangulation(X, Y), 'r-')
    if path:
        plt.savefig(path + "\\%s.png" % 1)
    plt.pause(2)

    dt.draw_triangles("b-", op, save, path)

    dt.remove_supervertexs(op, save)

    if circle == "y":
        dt.draw_circles(ax)

    if op == 'y' and save == 'y':
        plt.savefig(path + "\\%s.png" % count)
        images = []
        filenames = listdir(path)
        filenames = list(filter(lambda i: i[:-4].isdigit(), filenames))
        filenames.sort(key=lambda i: int(i[:-4]))
        for filename in filenames:
            images.append(imread(path + '\\' + filename))
            remove(path + '\\' + filename)
        mimsave(path + '\\%s_%s_%s_demo.gif' % (width, height, total), images, duration=0.15)
        print('图片已保存至 "%s" 路径下，文件名为 "%s_%s_%s_demo.gif"。' % (path, width, height, total))
    elif op == 'n' and save == 'y':
        plt.savefig(path + '\\%s_%s_%s_demo.png' % (width, height, total))
        print('图片已保存至 "%s" 路径下，文件名为 "%s_%s_%s_demo.png"。' % (path, width, height, total))

    plt.show()

def option_1():
    vertices = []
    total = int(input("请输入点的总数："))
    print("请输入每个点的x,y坐标")
    for _ in range(total):
        x, y = map(float, input().split())
        vertices.append(Point(x, y))
    op = input("是否需要动态演示（y/n）：")
    circle = input("是否显示外接圆（y/n）：")
    save = input("是否保存为gif文件（y/n）：") if op == "y" else input("是否保存为png文件（y/n）：")
    path = input("请输入存储路径：") if save == "y" else None

    X, Y = [i.x for i in vertices], [i.y for i in vertices]
    width = max(X) - min(X) + 1
    height = max(Y) - min(Y) + 1

    do_delaunay(X, Y, vertices, width, height, total, op, circle, save, path)

def option_2():
    width, height, total = map(int, input("请输入点集的宽度，高度，总数（以空格分隔）：").split())
    op = input("是否需要动态演示（y/n）：")
    circle = input("是否显示外接圆（y/n）：")
    save = input("是否保存为gif文件（y/n）：") if op == "y" else input("是否保存为png文件（y/n）：")
    path = input("请输入存储路径：") if save == "y" else None

    vertices = [Point(width * random(), height * random()) for i in range(total)]
    X, Y = [i.x for i in vertices], [i.y for i in vertices]

    do_delaunay(X, Y, vertices, width, height, total, op, circle, save, path)

def option_3():
    file_path = input("请输入图片路径：")
    point_num = int(input("请输入点的数量："))
    tri_picture = Triangulate_Picture(file_path, point_num)
    tri_picture.draw_picture()
    print('图片已保存至 "%s" 路径下，文件名为 "%s"。' % (dirname(file_path), basename(file_path)[:-4] + "_" + str(point_num) + ".png"))

if __name__ == "__main__":
    filterwarnings("ignore", ".*GUI is implemented.*")
    select = {1: option_1, 2: option_2, 3: option_3, 4: exit}
    while True:
        print("可进行的操作：\n1、给定点集的Delaunay三角剖分\n2、随机点集的三角剖分\n3、图片三角化\n4、退出")
        op = int(input("请输入操作序号："))
        count = 2
        select[op]()
        print("\n")