import os
import sys
import shutil
import pathlib

# 🔥 PosixPath → WindowsPath 패치 (Windows 필수)
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

# 🔥 YOLO 경로 등록
sys.path.append(r"C:\Users\yyj23\yolov5")
sys.path.append(r"C:\Users\yyj23")

YOLO_DIR = r"C:\Users\yyj23\yolov5"
IMAGE_DIR = r"C:\Users\yyj23\test\images"
WEIGHTS_PATH = r"C:\Users\yyj23\yolov5\best.pt"
RUN_NAME = "braille"

def run_detection():
    from yolov5.detect import run   # 이제 정상 import 됨

    save_dir = fr"{YOLO_DIR}\runs\detect\{RUN_NAME}"
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)

    run(
        weights=WEIGHTS_PATH,
        source=IMAGE_DIR,
        imgsz=(896, 896),
        conf_thres=0.20,
        iou_thres=0.60,
        save_txt=True,
        save_conf=True,
        project=fr"{YOLO_DIR}\runs\detect",
        name=RUN_NAME,
        exist_ok=True,
    )