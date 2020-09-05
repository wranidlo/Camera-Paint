import cv2
import numpy as np
import math


# when started put object to track into smaller rectangle and press space
# to end press ESC

def get_back_histogram(image, hist):
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (27, 27))
    struct_element = cv2.calcBackProject([image], [0, 1], hist, [0, 150, 0, 256], 1)
    cv2.filter2D(struct_element, -1, disc, struct_element)
    return struct_element


def calculate_center(best_contour, last_center):
    centroid = cv2.moments(best_contour)
    if centroid['m00'] != 0:
        x_dimension, y_dimension = (int(centroid['m10'] / centroid['m00']), int(centroid['m01'] / centroid['m00']))
        return x_dimension, y_dimension
    else:
        return last_center


def calculate_contours(histogram_mask):
    histogram_gray = cv2.cvtColor(histogram_mask, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(histogram_gray, 0, 255, 0)
    contour, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contour


def masking_histogram(frame, histogram):
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    struct_element = get_back_histogram(frame_hsv, histogram)
    _, thresh = cv2.threshold(struct_element, 150, 255, cv2.THRESH_TOZERO)
    thresh = cv2.merge((thresh, thresh, thresh))
    return cv2.bitwise_and(thresh, frame)


class camera:
    first_place = []
    second_place = []

    def __init__(self):
        self.histogram_created_check = False

        self.histogram = None
        self.cap = cv2.VideoCapture(0)

        _, frame = self.cap.read()
        self.rows, self.cols, _ = frame.shape
        print(self.rows, self.cols)
        self.last_center = (int(self.rows / 2), int(self.cols / 2))

    def draw_place(self, frame):
        rows, cols, _ = frame.shape
        self.first_place = [(int(9.5 * cols / 20), int(9.5 * rows / 20)),
                            (int(10.5 * cols / 20), int(10.5 * rows / 20))]
        cv2.rectangle(frame, self.first_place[0], self.first_place[1], (255, 0, 0))
        self.second_place = [(int(9 * cols / 20), int(7 * rows / 20)), (int(11 * cols / 20), int(13 * rows / 20))]
        cv2.rectangle(frame, self.second_place[0], self.second_place[1], (0, 0, 255))
        return frame

    def create_histogram(self, frame):
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        hsv_frame = hsv_frame[self.first_place[0][1]: self.first_place[1][1],
                    self.first_place[0][0]: self.first_place[1][0]]

        histogram = cv2.calcHist([hsv_frame], [0, 1], None, [150, 256], [0, 150, 0, 256])

        return cv2.normalize(histogram, histogram, 0, 255, cv2.NORM_MINMAX), hsv_frame

    def scan_object_fast(self):

        while self.cap.isOpened():
            ret, frame = self.cap.read()

            frame = cv2.flip(frame, 1)

            if self.histogram_created_check is False:
                frame = self.draw_place(frame)

            cv2.namedWindow('Scan', cv2.WINDOW_NORMAL)

            if cv2.waitKey(1) & 0xFF == 32:
                self.histogram_created_check = True
                self.histogram, _ = self.create_histogram(frame)
                break
            cv2.destroyAllWindows()
        cv2.destroyAllWindows()
        return self.histogram

    def search_for_object(self):
        ret, frame = self.cap.read()

        frame = cv2.flip(frame, 1)

        frame = self.draw_place(frame)
        self.histogram, _ = self.create_histogram(frame)
        return frame

    def scan_object(self):
        ret, frame = self.cap.read()

        frame = cv2.flip(frame, 1)

        frame = self.draw_place(frame)

        if cv2.waitKey(1) & 0xFF == 32:
            self.histogram_created_check = True
            self.histogram, _ = self.create_histogram(frame)
        return frame

    def set_histogram_created_check_not(self):
        self.histogram_created_check = False

    def get_center(self):
        ret, frame = self.cap.read()

        frame = cv2.flip(frame, 1)

        if self.histogram_created_check:
            hist_masked_image = masking_histogram(frame, self.histogram)
            kernel = np.ones((5, 5), np.uint8)
            hist_masked_image = cv2.erode(hist_masked_image, kernel)
            hist_masked_image = cv2.dilate(hist_masked_image, kernel)
            contour_list = calculate_contours(hist_masked_image)
            try:
                max_cont = max(contour_list, key=cv2.contourArea)
                cnt_centroid = calculate_center(max_cont, self.last_center)
                if math.sqrt((self.last_center[0] - cnt_centroid[0]) ** 2 +
                             (self.last_center[1] - cnt_centroid[1]) ** 2) > 100:
                    cnt_centroid = self.last_center
                else:
                    self.last_center = cnt_centroid
            except ValueError:
                # print("out")
                cnt_centroid = self.last_center
            cv2.circle(frame, cnt_centroid, 5, [255, 0, 255], -1)
        else:
            frame = self.draw_place(frame)

        return frame, cnt_centroid

    def check_quality(self, frame):
        hist_masked_image = masking_histogram(frame, self.histogram)
        erode_kernel = np.ones((5, 5), np.uint8)
        dilate_kernel = np.ones((5, 5), np.uint8)
        hist_masked_image = cv2.erode(hist_masked_image, erode_kernel)
        hist_masked_image = cv2.dilate(hist_masked_image, dilate_kernel)
        contour_list = calculate_contours(hist_masked_image)
        return len(contour_list)


def main():  # This main is for test purpose only
    usage = camera()

    cv2.namedWindow('Scan', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Scan', 800, 600)
    while usage.histogram_created_check is False:
        frame = usage.scan_object()
        cv2.imshow('Scan', frame)
    cv2.destroyAllWindows()
    cv2.namedWindow('Live', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Live', 800, 600)
    while usage.cap.isOpened():
        img, _ = usage.get_center()
        cv2.imshow('Live', img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    usage.cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
