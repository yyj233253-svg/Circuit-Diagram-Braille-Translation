# 회로선 점자 표시 + 소자 마스킹 자동 생성 모듈

import os
import cv2
import numpy as np
import glob

# 사용할 경로들
IMAGE_DIR = r"C:\Users\yyj23\test\images"
SNAP_LABEL_DIR = r"C:\Users\yyj23\yolov5\runs\detect\braille_snapped\labels"
DOTLINE_OUT = r"C:\Users\yyj23\dotline_result"

def run_dotline():
    print("\n===== [Step 4] DOT LINE (회로 점자화) 시작 =====")

    os.makedirs(DOTLINE_OUT, exist_ok=True)

    label_files = glob.glob(os.path.join(SNAP_LABEL_DIR, "*.txt"))
    if not label_files:
        print("[Warning] 스냅된 라벨 파일이 없습니다.")
        return

    for label_path in label_files:

        base = os.path.splitext(os.path.basename(label_path))[0]
        img_path = os.path.join(IMAGE_DIR, base + ".jpg")

        if not os.path.exists(img_path):
            print(f"[Skip] 이미지 없음 → {base}")
            continue

        # 이미지 읽기
        img = cv2.imread(img_path)
        if img is None:
            print(f"[ERR] 이미지 읽기 실패 → {img_path}")
            continue

        H, W = img.shape[:2]
        mask_img = img.copy()
        boxes = []

        # ---- YOLO 스냅 박스 읽기 ----
        for line in open(label_path):
            parts = line.split()
            if len(parts) < 5:
                continue
            _, nx, ny, nw, nh = map(float, parts[:5])

            x1 = int((nx - nw/2) * W)
            y1 = int((ny - nh/2) * H)
            x2 = int((nx + nw/2) * W)
            y2 = int((ny + nh/2) * H)

            boxes.append((x1, y1, x2, y2))

        # ---- 소자 마스킹 ----
        padding = 5
        for x1, y1, x2, y2 in boxes:
            cv2.rectangle(mask_img, (x1-padding, y1-padding),
                          (x2+padding, y2+padding), (255,255,255), -1)

        # ---- 에지 및 직선 검출 ----
        gray = cv2.cvtColor(mask_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 60,
                                minLineLength=50, maxLineGap=15)

        # ---- 점선으로 그리기 ----
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.hypot(x2-x1, y2-y1)
                step = 25
                rad = 3
                if length <= 0:
                    continue

                dx = (x2 - x1) / length
                dy = (y2 - y1) / length

                num = int(length / step)
                for i in range(num + 1):
                    px = int(x1 + dx * step * i)
                    py = int(y1 + dy * step * i)
                    if 0 <= px < W and 0 <= py < H:
                        cv2.circle(mask_img, (px,py), rad, (255,0,0), -1)

        # ---- 결과 저장 ----
        out_path = os.path.join(DOTLINE_OUT, base + "_dotline.jpg")
        cv2.imwrite(out_path, mask_img)

    print("===== [Step 4] DOT LINE 완료 =====")