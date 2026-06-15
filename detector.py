# detector.py
import cv2
import numpy as np
import config


class ColorDetector:
    def __init__(self):
        # 初始化攝影機
        self.cap = cv2.VideoCapture(0)
        # 定義綠色的 HSV 範圍
        self.lower_green = np.array([35, 43, 46])
        self.upper_green = np.array([77, 255, 255])

    def get_direction(self, current_direction):
        """讀取一幀影像，並根據綠色物體位置回傳新方向"""
        ret, frame = self.cap.read()
        if not ret:
            return current_direction  # 如果讀取失敗，維持原方向

        frame = cv2.flip(frame, 1)  # 鏡像翻轉
        h, w, _ = frame.shape
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        new_dir = current_direction  # 預設維持原方向

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 500:
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])

                    rel_x = cX / w
                    rel_y = cY / h

                    # 依九宮格比例判斷方向，並防止180度反向自殺
                    if rel_y < 0.35 and current_direction != "DOWN":
                        new_dir = "UP"
                    elif rel_y > 0.65 and current_direction != "UP":
                        new_dir = "DOWN"
                    elif rel_x < 0.35 and current_direction != "RIGHT":
                        new_dir = "LEFT"
                    elif rel_x > 0.65 and current_direction != "LEFT":
                        new_dir = "RIGHT"

        # 顯示 OpenCV 控制視窗
        cv2.imshow('Camera Control Window', frame)
        cv2.waitKey(1)

        return new_dir

    def release(self):
        """釋放攝影機資源"""
        self.cap.release()
        cv2.destroyAllWindows()