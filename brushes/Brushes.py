import cv2
import imutils
import numpy as np
import random
from enum import Enum

# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
#          BRUSHES MODULE
# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

# ----------------------------------
#               ENUMS
# ----------------------------------


class SelectionTypes(Enum):
    PICK = 0    # Overwrite current selection
    ADD = 1     # Add to current selection
    SUB = 2     # Subtract from current selection
    MUL = 3    # Leave only shared selection

# ----------------------------------
#         VARIABLES & CLASSES
# ----------------------------------
size_x = 380
size_y = 540

selection_type = SelectionTypes.PICK
selection_exists = False

# The canvas that stores actual image
canvas_matrix = np.empty((size_x, size_y, 3), dtype='uint8')
canvas_matrix.fill(255)

# Matrix that stores selected pixels locations
selection_matrix = np.empty((size_x, size_y), dtype='bool_')
selection_matrix.fill(False)

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
        for i in range(len(self.shape_matrix)):
            for j in range(len(self.shape_matrix[i])):
                self.shape_matrix[i][j] /= 255.0
        return rotated_brush


# pre-defined brushes
influence_pencil = np.full((11, 11), 1.0)
b = Brush(influence_pencil, 10, 1, 0, 1.0)
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


def save_step():
    global step
    step.append(canvas_matrix)


def selector_Rect(start_pos, end_pos):  # expected tuple(x, y) as position
    global selection_exists

    h_flip = False  # horizontal iteration direction
    v_flip = False  # vertical iteration direction

    if start_pos[0] < end_pos[0]:
        h_flip = True
    if start_pos[1] < end_pos[1]:
        v_flip = True

    selection = np.empty((size_x, size_y), dtype='bool_')
    selection.fill(False)

    row_range = [0, 0]
    column_range = [0, 0]

    if not h_flip:
        row_range = [start_pos[0], end_pos[0]]
    else:
        row_range = [end_pos[0], start_pos[0]]

    if not v_flip:
        column_range = [start_pos[1], end_pos[1]]
    else:
        column_range = [end_pos[1], start_pos[1]]

    for i in range(row_range[0], row_range[1] + 1):
        for j in range(column_range[0], column_range[1] + 1):
            selection[i][j] = True

    join_new_selection(selection)
    selection_exists = is_selection_empty(selection_matrix)
    return

def selector_ColorPicker(picker_pos, margin:float):   # expected tuple(x, y) as position, float 0.0 - 1.0 as margin
    global selection_exists

    color = canvas_matrix[picker_pos[0]][picker_pos[1]]

    selection = np.empty((size_x, size_y), dtype='bool_')
    selection.fill(False)

    for x in range(0, len(canvas_matrix)):
        for y in range(0, len(canvas_matrix[0])):
            if compare_colors(color, canvas_matrix[x][y], margin):
                selection[x][y] = True
            else:
                selection[x][y] = False

    join_new_selection(selection)
    selection_exists = is_selection_empty(selection_matrix)
    return

def selector_MagicWand():   # TO DO!!!!!!
    pass

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

# SELECTION SECTION


def is_selection_empty(selection):
    for x in range(0, len(selection)):
        for y in range(0, len(selection[0])):
            if selection[x][y]:
                return True
    return False


def join_new_selection(new_selection):
    global selection_matrix
    global selection_exists

    if selection_type == SelectionTypes.PICK:   # Just overwrite selection and let the system know that it exists
        selection_matrix = new_selection
        return
    elif selection_type == SelectionTypes.ADD:
        if not selection_exists:    # if selection doesn't exist, just behave as PICK mode
            selection_matrix = new_selection
            return
        else: # if selection exists, add all new pixels
            for x in range(0, len(selection_matrix)):
                for y in range(0, len(selection_matrix[0])):
                    if new_selection[x][y]:
                        selection_matrix[x][y] = True
            return
    elif selection_type == SelectionTypes.SUB:
        if selection_exists:        # if selection exists, subtract all new pixels
            for x in range(0, len(selection_matrix)):
                for y in range(0, len(selection_matrix[0])):
                    if new_selection[x][y]:
                        selection_matrix[x][y] = False
            return
        else:       # if selection doesn't exist, there's nothing to subtract
            return
    elif selection_type == SelectionTypes.MUL:
        if selection_exists:
            for x in range(0, len(selection_matrix)):
                for y in range(0, len(selection_matrix[0])):
                    if new_selection[x][y] and selection_matrix[x][y]:
                        selection_matrix[x][y] = True
                    else:
                        selection_matrix[x][y] = False
            return
        else:       # if selection doesn't exist, there's nothing to multiply
            return

def true_color_value(color) -> float:
    return (color[0] + color[1] + color[2]) / 3.0

def compare_colors(original_color, new_color, margin) -> bool:
    origin_value = true_color_value(original_color)
    new_value = true_color_value(new_color)

    if origin_value - (255 * margin) <= new_value <= origin_value + (255 * margin):
        return True
    else:
        return False



draw(0,0,b_pencil,[255,0,0])
draw(200,200,b_pencil,[255,0,0])


# while 1:
   #  cv2.imshow('i',canvas_matrix)
   #  cv2.waitKey(1)