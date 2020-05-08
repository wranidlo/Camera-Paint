import cv2
import imutils
import numpy as np
import random

# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
#          BRUSHES MODULE
# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

# ----------------------------------
#         VARIABLES & CLASSES
# ----------------------------------
size_x = 1000
size_y = 1000


canvas_matrix = np.empty((size_x, size_y, 3), dtype='uint8')
canvas_matrix.fill(255)
step = [canvas_matrix]


class Brush(object):
    # constant multiplier used to create default variant of a brush
    sizeBase = 0
    # dynamic multiplier used create variants of different sizes
    sizeCurrent = 20
    rotation = 0
    opacity = 1.0
    shape_matrix = [[]]

    def __init__(self, shape_matrix, sizeBase: int = None, sizeCurrent: int = None, rotation: int = None, opacity: float= None):
        if sizeBase is None:
            self.sizeBase = 1
        else:
            self.sizeBase = sizeBase
        if sizeCurrent is None:
            self.sizeCurrent = 20
        else:
            self.sizeCurrent = sizeCurrent
        if rotation is None:
            self.rotation = 0.0
        else:
            self.rotation = rotation
        if opacity is None:
            self.opacity = 0.0
        else:
            self.opacity = opacity
        if len(shape_matrix) % 2 == 0 or len(shape_matrix[0]) % 2 == 0:
            print('Shape matrix must have odd lengths!')
            self.shape_matrix = [[1.0]]
        else:
            self.shape_matrix = shape_matrix

    def get_transformed_brush(self):
        for i in range(len(self.shape_matrix)):
            for j in range(len(self.shape_matrix[i])):
                self.shape_matrix[i][j] *= 255.0
        default_brush = cv2.resize(self.shape_matrix, (len(self.shape_matrix)*self.sizeBase, len(self.shape_matrix[0]) *self.sizeBase), interpolation=cv2.INTER_AREA)
        resized_brush = cv2.resize(default_brush, (default_brush.shape[0] * self.sizeCurrent, default_brush.shape[1] *self.sizeCurrent), interpolation=cv2.INTER_AREA)
        rotated_brush = imutils.rotate_bound(resized_brush, self.rotation)
        for i in range(len(rotated_brush)):
            for j in range(len(rotated_brush[i])):
                rotated_brush[i][j] *= self.opacity
                rotated_brush[i][j] /= 255.0
        return rotated_brush


# pre-defined brushes
influence_pencil = np.full((11, 11), 1.0)
b = Brush(influence_pencil, 10, 1, 30, 1.0)
b_pencil = b.get_transformed_brush()


# ----------------------------------
#           MAIN FUNCTIONS
# ----------------------------------

def draw(x: int, y: int, shape, color):
    global canvas_matrix
    x = x - int(len(shape) / 2)
    y = y - int(len(shape[0])/2)
    for i in range(0, len(shape)):
        for j in range(0, len(shape[0])):
            if not is_out_of_bounds(canvas_matrix, x+i, y+j):
                for k in range(0, 3):
                    c = limit_color_value(int(canvas_matrix[x+i, y+j, k]*(1-shape[i, j]))+(int(shape[i, j]*color[k])))
                    canvas_matrix[x+i, y+j, k] = c


# ----------------------------------
#         UTILITY FUNCTIONS
# ----------------------------------


def is_out_of_bounds(image, x: int, y: int) -> bool:  # used to check if brush goes out of bounds
    height = image.shape[0]
    width = image.shape[1]

    if x < 0 or x > width or y < 0 or y > height:
        return True
    else:
        return False


def limit_color_value(value:int) -> int:  # prevent color value overflow
    if value < 0:
        return 0
    elif value > 255:
        return 255
    else:
        return value
