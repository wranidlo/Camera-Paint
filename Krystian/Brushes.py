import cv2

# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
#          BRUSHES MODULE
# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
# This file contains all functions
# that apply a brush to the image.
# Any other methods than the ones
# from "BRUSHES" section should not
# be used outside of this module.

# ----------------------------------
#             VARIABLES
# ----------------------------------

# ----------------------------------
#              BRUSHES
# ----------------------------------

# ----------------------------------
#         UTILITY FUNCTIONS
# ----------------------------------


def is_out_of_bounds(image, x: int, y: int):
    # used to check if brush goes out of bounds
    height = image.shape[0]
    width = image.shape[1]

    if x < 0 or x > width or height < 0 or y > height:
        return False
    else:
        return True
