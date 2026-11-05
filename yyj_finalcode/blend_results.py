# blend_results.py
import os
import cv2
import glob
import matplotlib.pyplot as plt

# 경로 설정
BRAILLE_DIR = r"C:\Users\yyj23\braille_result"
DOTLINE_DIR = r"C:\Users\yyj23\dotline_result"
OUT_DIR     = r"C:\Users\yyj23\final_result\blend"
os.makedirs(OUT_DIR, exist_ok=True)

def run_blend():
    print("\n===== [Step 5] 점자 + 회로 Overlay Blend 시작 =====")

    braille_files = glob.glob(os.path.join(BRAILLE_DIR, "*_braille.png"))
    if not braille_files:
        print("[BLEND] braille 이미지 없음. Step3이 실행되었는지 확인하세요.")
        return

    total = 0

    for bpath in braille_files:
        base = os.path.basename(bpath).replace("_braille.png", "")

        dot_path = os.path.join(DOTLINE_DIR, base + "_dotline.jpg")
        if not os.path.exists(dot_path):
            print(f"[Skip] dotline 없음 → {base}")
            continue

        braille_img = cv2.imread(bpath)
        dotline_img = cv2.imread(dot_path)

        if braille_img is None or dotline_img is None:
            print(f"[ERR] 이미지 읽기 실패 → {base}")
            continue

        # 🔥 크기 통일을 정확하게 (inter_nearest 필수)
        #H, W = dotline_img.shape[:2]
       # braille_img = cv2.resize(braille_img, (W, H), interpolation=cv2.INTER_NEAREST)

        blended = cv2.addWeighted(dotline_img, 0.6, braille_img, 0.4, 0)

       

        out_path = os.path.join(OUT_DIR, base + "_final_overlay.jpg")
        cv2.imwrite(out_path, blended)

        total += 1

    print(f"[BLEND] 완료! 총 {total}개 이미지 생성됨.")