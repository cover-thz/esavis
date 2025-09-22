
import cv2

for i in range(5):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(f"index {i} did not work")
    else:
        print(f"camera appears to be at index {i}")


_ = input("Press Enter to exit...")
