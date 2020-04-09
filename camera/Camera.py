import cv2

first_place = []
second_place = []


def draw_place(frame):
    global first_place, second_place
    rows, cols, _ = frame.shape
    first_place = [(int(9 * cols / 20), int(7 * rows / 20)), (int(11 * cols / 20), int(13 * rows / 20))]
    cv2.rectangle(frame, first_place[0], first_place[1], (255, 0, 0))
    second_place = [(int(7 * cols / 20), int(5 * rows / 20)), (int(13 * cols / 20), int(15 * rows / 20))]
    cv2.rectangle(frame, second_place[0], second_place[1], (0, 0, 255))
    return frame


def hand_histogram(frame):
    global first_place, second_place
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    hsv_frame = hsv_frame[first_place[0][1]: first_place[1][1], first_place[0][0]: first_place[1][0]]

    hand_hist = cv2.calcHist(hsv_frame, [0, 1], None, [180, 256], [0, 180, 0, 256])
    return cv2.normalize(hand_hist, hand_hist, 0, 255, cv2.NORM_MINMAX), hsv_frame


def capture():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.namedWindow('hand_hsv', cv2.WINDOW_NORMAL)
    while (True):
        ret, frame = cap.read()
        frame = draw_place(frame)
        cv2.imshow('frame', frame)
        _, hsv_hand = hand_histogram(frame)
        cv2.imshow('hand_hsv', hsv_hand)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()


def main():
    capture()


if __name__ == "__main__":
    main()
