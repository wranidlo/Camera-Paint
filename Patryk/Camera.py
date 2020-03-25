import numpy as np
import cv2


smaller_rectangle = []
bigger_rectangle = []


def draw_rect(frame):
    global smaller_rectangle, bigger_rectangle
    rows, cols, _ = frame.shape
    print(rows, cols)
    smaller_rectangle = [(int(9 * cols / 20), int(7 * rows / 20)), (int(11 * cols / 20), int(13 * rows / 20))]
    cv2.rectangle(frame, smaller_rectangle[0], smaller_rectangle[1], (255, 0, 0))
    bigger_rectangle = [(int(7 * cols / 20), int(5 * rows / 20)), (int(13 * cols / 20), int(15 * rows / 20))]
    cv2.rectangle(frame, bigger_rectangle[0], bigger_rectangle[1], (0, 0, 255))
    return frame


def capture():
    cap = cv2.VideoCapture(0)

    while(True):
        ret, frame = cap.read()
        frame = draw_rect(frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()


def main():
    capture()


if __name__ == "__main__":
    main()
