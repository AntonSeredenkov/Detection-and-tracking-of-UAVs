import cv2
import time
import ArgsAcceptor


class VideoCap:
    def __init__(self, file_name="", motion_threshold=10, median_blur_value=5, show_fps=True, debug=False):
        self.file_name = file_name
        self.cap = cv2.VideoCapture(self.file_name if self.file_name else 0)
        self.prev_frame = None
        self.debug = debug

        self.motion_threshold = motion_threshold
        self.median_blur_value = median_blur_value

        self.x1_roi, self.y1_roi, self.x2_roi, self.y2_roi = 0, 0, 0, 0
        self.choose_roi = False

        # self.tracker = cv2.TrackerMIL_create()
        self.tracker = cv2.TrackerKCF_create()
        self.init_tracker = False

        self.show_fps = show_fps
        self.prev_time = 0
        self.current_time = 0

        self.video_capture()

    def on_mouse(self, event, x, y, flags, param):
        if not self.choose_roi:
            if event == cv2.EVENT_LBUTTONDOWN:  #нажатие ЛКМ
                self.x1_roi, self.y1_roi = x, y
            elif event == cv2.EVENT_LBUTTONUP:  #отпуск ЛКМ
                self.x2_roi, self.y2_roi = x, y
                if abs(self.x2_roi - self.x1_roi) > 0 and abs(self.y2_roi - self.y1_roi) > 0:
                    self.choose_roi = True
                    self.init_tracker = True

    def combine_shapes(self, a, b):  #объединение прямоугольных контуров, которые ложатся друг на друга
        x = min(a[0], b[0])
        y = min(a[1], b[1])
        w = b[0] + b[2] - a[0]
        h = b[1] + b[3] - a[1]
        return x, y, w, h

    def track_object(self, frame):
        ok, bbox = self.tracker.update(frame)
        if ok:
            # Удалось найти/отследить объект
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
        else:
            cv2.putText(frame, "Объект потерян", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            self.choose_roi = False
            self.x1_roi, self.y1_roi, self.x2_roi, self.y2_roi = 0, 0, 0, 0
            self.tracker = cv2.TrackerKCF_create()

    def detect_object(self, frame, gray):
        frame_diff = cv2.absdiff(self.prev_frame, gray)

        # Применение порогового значения
        _, threshold = cv2.threshold(frame_diff, self.motion_threshold, 255, cv2.THRESH_BINARY)

        # Поиск контура
        contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Объединение контуров, если они накладываются друг на друга
        res_contours = []
        for i in range(1, len(contours)):
            (x1, y1, w1, h1) = cv2.boundingRect(contours[i - 1])
            (x2, y2, w2, h2) = cv2.boundingRect(contours[i])
            if abs(x2 + w2 - x1) <= (w1 + w2) and abs(y2 + h2 - y1) <= (h1 + h2):
                res_contours.append(self.combine_shapes((x1, y1, w1, h1), (x2, y2, w2, h2)))
            else:
                res_contours.append((x1, y1, w1, h1))

        if self.debug:
            cv2.imshow("Motion Detection_difference", frame_diff)
        # Отображение прямоугольников вокруг обнаруженных объектов
        for contour in res_contours:
            (x, y, w, h) = contour
            # Пропуск слишком маленьких объектов
            if w * h <= 500:
                continue
            # Отображение маленьких объектов
            if w * h <= 2500:
                x_mid = x + w // 2
                y_mid = y + h // 2
                cv2.rectangle(frame, (x_mid - 25, y_mid - 25), (x_mid + 25, y_mid + 25), (255, 0, 0), 2)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    def video_capture(self):
        cv2.namedWindow("Motion Detection")
        cv2.setMouseCallback('Motion Detection', self.on_mouse)
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # gray = cv2.GaussianBlur(gray, (25, 25), 0)
            gray = cv2.medianBlur(gray, self.median_blur_value)

            if self.prev_frame is None:
                self.prev_frame = gray
                continue

            # Инициализация трекера
            if self.init_tracker:
                self.tracker.init(frame,
                                  (self.x1_roi, self.y1_roi, self.x2_roi - self.x1_roi, self.y2_roi - self.y1_roi))
                self.init_tracker = False

            if self.choose_roi:
                self.track_object(frame)
            else:
                self.detect_object(frame, gray)

            # Вычисление FPS
            if self.show_fps:
                self.current_time = time.time()
                fps = 1 / (self.current_time - self.prev_time)
                self.prev_time = self.current_time
                # Отображение FPS на кадре
                cv2.putText(frame, f"FPS: {int(fps)}", (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 3)

            # Отображение кадра
            cv2.imshow("Motion Detection", frame)

            # Обновление предыдущего кадра
            self.prev_frame = gray

            # Обработка нажатий клавиши
            key = cv2.waitKey(2)

            if key == ord('q') or key == ord('й'):
                break
            if key == ord('w') or key == ord('ц'):
                self.choose_roi = False
                self.x1_roi, self.y1_roi, self.x2_roi, self.y2_roi = 0, 0, 0, 0
                self.tracker = cv2.TrackerKCF_create()


    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    args_acceptor = ArgsAcceptor.ArgsAcceptor()
    check, err = args_acceptor.check_values()
    if check:
        args = args_acceptor.get_args()
        capture = VideoCap(file_name=args.video, show_fps=args.fps, median_blur_value=args.blur,
                           motion_threshold=args.threshold, debug=args.debug)
    else:
        print(err)
