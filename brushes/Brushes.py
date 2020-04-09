import cv2
import imutils

# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
#          BRUSHES MODULE
# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

# ----------------------------------
#         VARIABLES & CLASSES
# ----------------------------------


class Brush(object):
    # constant multiplier used to create default variant of a brush
    sizeBase = 0
    # dynamic multiplier used create variants of different sizes
    sizeCurrent = 20
    rotation = 0
    opacity = 1.0
    influance_matrix = [[]]

    def __init__(self, influance_matrix, sizeBase:int=None, sizeCurrent:int=None, rotation:int=None, opacity:float=None):
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
        if len(influance_matrix)%2 == 0 or len(influance_matrix[0])%2 == 0:
            print('Influance matrix must have odd lengths!')
            self.influance_matrix = [[1.0]]

    def get_transformed_brush(self):
        for i in range(len(self.influance_matrix)):
            for j in range(len(self.influance_matrix[i])):
                self.influance_matrix[i][j] *= 255.0
        default_brush = cv2.resize(self.influance_matrix, (len(self.influance_matrix)*self.sizeBase, len(self.influance_matrix[0]*self.sizeBase)), interpolation=cv2.INTER_AREA)
        resized_brush = cv2.resize(default_brush, (default_brush.shape[0] * self.sizeCurrent, default_brush.shape[1] * self.sizeCurrent), interpolation=cv2.INTER_AREA)
        rotated_brush = imutils.rotate_bound(resized_brush, self.rotation)
        for i in range(len(rotated_brush)):
            for j in range(len(rotated_brush[i])):
                rotated_brush[i][j] *= self.opacity
                rotated_brush[i][j] /= 255.0
        return rotated_brush


# ----------------------------------
#           MAIN FUNCTIONS
# ----------------------------------

# ----------------------------------
#         UTILITY FUNCTIONS
# ----------------------------------


def is_out_of_bounds(image, x: int, y: int) -> bool:  # used to check if brush goes out of bounds
    height = image.shape[0]
    width = image.shape[1]

    if x < 0 or x > width or height < 0 or y > height:
        return False
    else:
        return True


def limit_color_value(value:int) -> int:  # prevent color value overflow
    if value < 0:
        return 0
    elif value > 255:
        return 255
    else:
        return value
