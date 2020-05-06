
import cv2
video_cap = cv2.VideoCapture(0)
while True:
    rec , frame = video_cap.read()
    cv2.imshow('Video',frame)
    if cv2.waitKey(1) & 0xFF == ord('c'):
        cv2.imwrite("./Capture/1"+".png",frame)