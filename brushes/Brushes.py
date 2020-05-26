import cv2
import imutils
import numpy as np
import random
from enum import Enum
import math
import time

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
size_x = 480
size_y = 640

selection_type = SelectionTypes.PICK
selection_exists = False

# The canvas that stores actual image
canvas_matrix = np.empty((size_x, size_y, 3), dtype='uint8')
canvas_matrix.fill(255)

canvas_matrix_temp = canvas_matrix.copy()

# Matrix that stores selected pixels locations
selection_matrix = np.empty((size_x, size_y), dtype='bool_')
selection_matrix.fill(False)

step = [canvas_matrix.copy()]
current_step = 0



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
b_pencil = Brush(influence_pencil, 10, 1, 0, 1.0)
pencil = b_pencil.get_transformed_brush()
influence_brush = np.full((11, 11), 0.0)
for x in range(0, len(influence_brush)):
    for y in range(0, len(influence_brush[0])):
        influence_brush[x, y] = 1 - (((pow((5-x), 2))+(pow((5-y), 2)))/50)
b_brush = Brush(influence_brush, 2, 1, 0, 1.0)
brush = b_brush.get_transformed_brush()
influence_spray = np.full((11,11), 0.0)
for x in range(0, len(influence_spray)):
    for y in range(0, len(influence_spray[0])):
        influence_spray[x, y] = (random.randint(0, 10)/10)
b_spray = Brush(influence_spray, 10, 1, 0, 1.0)
spray = b_spray.get_transformed_brush()

# ----------------------------------
#           MAIN FUNCTIONS
# ----------------------------------

# DIRECT CANVAS MODIFIERS


def draw(x: int, y: int, shape, color):
    global canvas_matrix, canvas_matrix_temp
    x = x - int(len(shape) / 2)
    y = y - int(len(shape[0])/2)
    for i in range(0, len(shape)):
        for j in range(0, len(shape[0])):
            if not is_out_of_bounds(canvas_matrix, x+i, y+j):
                for k in range(0, 3):
                    c = limit_color_value(int(canvas_matrix[x+i, y+j, k]*(1-shape[i, j]))+(int(shape[i, j]*color[k])))
                    canvas_matrix[x+i, y+j, k] = c
    refresh_temp()


def desaturate(amount:float):  # float 0.0 - 1.0 as amount
    global canvas_matrix

    for x in range(0, len(canvas_matrix)):
        for y in range(0, len(canvas_matrix[0])):
            if selection_exists and selection_matrix[x][y] is False:
                continue
            true_value = true_color_value(canvas_matrix[x][y])
            blend_value_blue = limit_color_value(int(true_value * amount + canvas_matrix[x][y][0] * (1 - amount)))
            blend_value_green = limit_color_value(int(true_value * amount + canvas_matrix[x][y][1] * (1 - amount)))
            blend_value_red = limit_color_value(int(true_value * amount + canvas_matrix[x][y][2] * (1 - amount)))

            canvas_matrix[x][y][0] = blend_value_blue
            canvas_matrix[x][y][1] = blend_value_green
            canvas_matrix[x][y][2] = blend_value_red

    refresh_temp()

# UNDO/REDO RELATED


def save_step():
    global step, current_step, canvas_matrix
    if current_step != len(step)-1:
        l = len(step)-1-current_step
        for x in range(0, l):
            step.pop()
    step.append(canvas_matrix.copy())
    current_step = len(step)-1


def b_undo():
    global canvas_matrix, current_step, step
    if current_step == 0:
        return
    else:
        current_step = current_step - 1
        canvas_matrix = step[current_step].copy()
        refresh_temp()


def b_redo():
    global canvas_matrix, current_step, step
    if current_step == len(step)-1:
        return
    else:
        current_step = current_step+1
        canvas_matrix = step[current_step].copy()
        refresh_temp()

# SELECTORS


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


def selector_Circle(center_pos, end_pos):  # expected tuple(x, y) as position
    global selection_exists

    radius = math.sqrt((end_pos[0] - center_pos[0])**2 + (end_pos[1] - center_pos[1])**2)

    selection = np.empty((size_x, size_y), dtype='bool_')
    selection.fill(False)

    for x in range(0, len(canvas_matrix)):
        for y in (0, len(canvas_matrix[0])):
            if (x - center_pos[0])**2 + (y - center_pos[1])**2 <= radius**2:
                selection[x][y] = True

    join_new_selection(selection)
    selection_exists = is_selection_empty(selection_matrix)
    return


# ----------------------------------
#         UTILITY FUNCTIONS
# ----------------------------------


def refresh_temp():
    global canvas_matrix, canvas_matrix_temp
    np.copyto(canvas_matrix_temp, canvas_matrix)
    selection_apply()


def clean_canvas():
    canvas_matrix.fill(255)
    save_step()
    refresh_temp()


def clear_steps():
    global step, current_step
    step = [canvas_matrix.copy()]
    current_step = 0


def is_out_of_bounds(image, x: int, y: int) -> bool:  # used to check if brush goes out of bounds
    width = image.shape[0]
    height = image.shape[1]

    if x < 0 or x > width-1 or y < 0 or y > height-1:
        return True
    else:
        if selection_exists:
            if selection_matrix[x, y]:
                return False
            else:
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


def check_neighbors_selection(x, y):

    for temp_x in range(-1, 2):
        for temp_y in range(-1, 2):
            if not selection_matrix[x+temp_x, y+temp_y]:
                return True
    return False

def check_neighbors_color(x, y, color):

    neighbors = []
    for temp_x in range(-1, 2):
        for temp_y in range(-1, 2):
            if not (temp_y==0 and temp_x==0):
                if not is_out_of_bounds(canvas_matrix, x+temp_x, y+temp_y):
                    if (canvas_matrix[x+temp_x, y+temp_y] == color).all():
                        neighbors.append([x+temp_x, y+temp_y])
    return neighbors


def negative(x, y):
    global canvas_matrix_temp
    canvas_matrix_temp[x, y, 0] = 255 - canvas_matrix_temp[x, y, 0]
    canvas_matrix_temp[x, y, 1] = 255 - canvas_matrix_temp[x, y, 1]
    canvas_matrix_temp[x, y, 2] = 255 - canvas_matrix_temp[x, y, 2]


def selection_apply():
    for x in range(0, size_x):
        for y in range(0, size_y):
            if selection_matrix[x, y]:
                if x == 0 or x == size_x-1 or y == 0 or y == size_y-1:
                    negative(x, y)
                if check_neighbors_selection(x, y):
                    negative(x, y)


def fill(x, y, color):
    global canvas_matrix, canvas_matrix_temp
    queue = [[x, y]]
    color_origin = np.empty(3)
    np.copyto(color_origin, canvas_matrix[x][y])
    if (color == color_origin).all():
        return
    canvas_matrix[queue[0][0]][queue[0][1]] = color
    while len(queue) > 0:
        temp = check_neighbors_color(queue[0][0], queue[0][1], color_origin)
        for temp_x in temp:
            queue.append(temp_x)
            canvas_matrix[temp_x[0]][temp_x[1]] = color
        queue.pop(0)

    refresh_temp()
    save_step()



def test():
    global step
    draw(50,50,pencil,[0,0,180])
    save_step()


    draw(100,100,brush,[255,0,0])
    save_step()

    draw(250,250,spray,[0,100,0])
    b_undo()
    b = input('sth')
    if b == 'a':
        b_redo()

    for z in range(40, 170):
        for t in range(40, 170):
            selection_matrix[z, t] = True


    selection_exists = True
    draw(170,170,spray,[0,100,0])
    save_step()
    selection_matrix.fill(False)
    selection_exists = False

    draw(140, 190, brush, [255, 0, 0])
    draw(0, 0, brush, [255, 0, 0])
    save_step()

    #fill(350, 350, [0,255,100])
    #save_step()

    print(current_step)
    while 1:

        cv2.imshow('o', step[0])
        cv2.waitKey(10)
