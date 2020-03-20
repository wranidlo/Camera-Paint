import numpy as np
import cv2


def capture():
    cap = cv2.VideoCapture(0)

    while(True):
        ret, frame = cap.read()

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    capture()


if __name__ == "__main__":
    main()
