# braille_canvas.py (Spyder Windows 버전)
import os, glob, yaml
from PIL import Image, ImageDraw

# ===================== 경로 =====================
IMG_DIRS = [
    r"C:\Users\yyj23\test\images",
    r"C:\Users\yyj23\yolov5\runs\detect\braille",
]

LABEL_DIR = r"C:\Users\yyj23\yolov5\runs\detect\braille_snapped\labels"
DATA_YAML = r"C:\Users\yyj23\data.yaml"
OUT_DIR   = r"C:\Users\yyj23\braille_result"
os.makedirs(OUT_DIR, exist_ok=True)

# ===================== 클래스 이름/매핑 =====================
with open(DATA_YAML, "r", encoding="utf-8") as f:
    NAMES = yaml.safe_load(f)["names"]

BRAILLE = {
    "V1":"⠯⠹⠁⠽","V2":"⠯⠠⠧⠽","V3":"⠯⠠⠧⠽","V4":"⠯⠹⠁⠽",
    "I1":"⠯⠁⠠⠽","I2":"⠯⠠⠁⠽","I3":"⠯⠠⠁⠽","I4":"⠯⠁⠠⠽",
    "R1":"⠯⠠⠗⠽","R2":"⠯⠠⠗⠽",
    "C1":"⠯⠠⠉⠽","C2":"⠯⠠⠉⠽",
    "L1":"⠯⠠⠇⠽","L2":"⠯⠠⠇⠽",
}

# 회전이 필요한 부품들
WIDE_8x3 = {"V1","V3","I1","I3","R2","C2","L2"}

# ===================== 렌더링 설정 =====================
USE_8_DOT   = False
DOT_COLOR   = (0,0,0)
BG_COLOR    = (255,255,255)

USE_MM      = False
DOT_R_RATIO = 0.0030
STEP_RATIO  = 0.018
CELL_GAP_K  = 0.75

DPI         = 300
DOT_DIAM_MM = 1.2
STEP_X_MM   = 2.3
STEP_Y_MM   = 2.3
CELL_GAP_MM = 5.0

TIGHTEN     = 1.00

DEBUG_CENTER = False
CENTER_COLOR = (255, 0, 0)
CENTER_HALF  = 10

# ===================== 유틸 =====================
IMG_EXTS = (".jpg",".jpeg",".png",".bmp",".tif",".tiff",".webp")

def find_image_by_base(base):
    for root in IMG_DIRS:
        for ext in IMG_EXTS:
            p = os.path.join(root, base + ext)
            if os.path.exists(p):
                return p
    for root in IMG_DIRS:
        for ext in IMG_EXTS:
            cand = glob.glob(os.path.join(root, base + "*" + ext))
            if cand:
                return cand[0]
    return None

def mm2px(mm, dpi):
    return int(round(mm * dpi / 25.4))

def compute_pitch(W, H):
    if USE_MM:
        r   = max(1, mm2px(DOT_DIAM_MM, DPI)//2)
        sx  = max(2, mm2px(STEP_X_MM, DPI))
        sy  = max(2, mm2px(STEP_Y_MM, DPI))
        gap = max(2, mm2px(CELL_GAP_MM, DPI))
    else:
        base = min(W, H)
        r   = max(1, int(base * DOT_R_RATIO))
        sx  = max(2, int(base * STEP_RATIO))
        sy  = max(2, int(base * STEP_RATIO))
        gap = int(sx * CELL_GAP_K)

    r   = max(1, int(r   * TIGHTEN))
    sx  = max(2, int(sx  * TIGHTEN))
    sy  = max(2, int(sy  * TIGHTEN))
    gap = max(1, int(gap * TIGHTEN))
    r = min(r, int(0.45 * min(sx, sy)))
    return r, sx, sy, gap

# ===================== 회전 함수 =====================
def rotate90(x, y, cx, cy, cw=True):
    dx, dy = x - cx, y - cy
    if cw:
        nx, ny = -dy, dx
    else:
        nx, ny = dy, -dx
    return cx + nx, cy + ny

# ===================== 점자 렌더링 =====================
def cell_points(cx, cy, sx, sy, r, mask, use8dot):
    rows = 4 if use8dot else 3
    cols = 2

    grid_w = (cols - 1) * sx
    grid_h = (rows - 1) * sy

    x0 = cx - grid_w/2
    y0 = cy - grid_h/2

    pos = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(0,3),(1,3)]
    pts = []
    for d in range(8):
        if d >= 6 and not use8dot:
            continue
        if (mask >> d) & 1:
            gx, gy = pos[d]
            px = x0 + gx*sx
            py = y0 + gy*sy
            pts.append((px, py, r))
    return pts, grid_w, grid_h

def string_to_points(cx, cy, text, r, sx, sy, gap, use8dot):
    pts = []
    rows = 4 if use8dot else 3

    grid_w = (2 - 1) * sx
    grid_h = (rows - 1) * sy

    n = len(text)
    total_w = n*grid_w + (n-1)*gap

    start_cx = cx - total_w/2 + grid_w/2  # 🔥 중앙 정렬 핵심

    for i, ch in enumerate(text):
        code = ord(ch)
        mask = (code - 0x2800) if 0x2800 <= code <= 0x28FF else 0
        scx = start_cx + i*(grid_w + gap)
        dots, _, _ = cell_points(scx, cy, sx, sy, r, mask, use8dot)
        pts.extend(dots)

    return pts, total_w, grid_h

# ===================== 메인 루프 =====================
def run_braille():
    label_files = sorted(glob.glob(os.path.join(LABEL_DIR, "*.txt")))
    processed, missing_img, empty_labels = 0, [], 0

    for lpath in label_files:
        base = os.path.splitext(os.path.basename(lpath))[0]
        ipath = find_image_by_base(base)
        if not ipath:
            missing_img.append(base)
            continue

        lines = [ln.strip() for ln in open(lpath) if ln.strip()]
        if not lines:
            empty_labels += 1
            continue

        W, H = Image.open(ipath).size
        canvas = Image.new("RGB", (W, H), BG_COLOR)
        draw = ImageDraw.Draw(canvas)

        r, sx, sy, gap = compute_pitch(W, H)

        for line in lines:
            parts = line.split()
            if len(parts) < 5:
                continue

            cls_id = int(parts[0])
            x, y = map(float, parts[1:3])
            xc, yc = x*W, y*H

            cname = NAMES[cls_id]
            text  = BRAILLE.get(cname, "⠿")

            dots, _, _ = string_to_points(xc, yc, text, r, sx, sy, gap, USE_8_DOT)

            if cname in WIDE_8x3:
                dots = [(*rotate90(px, py, xc, yc, cw=True), rr) for (px, py, rr) in dots]

            for px, py, rr in dots:
                if 0 <= px < W and 0 <= py < H:
                    draw.ellipse((px-rr, py-rr, px+rr, py+rr), fill=DOT_COLOR)

            if DEBUG_CENTER:
                draw.line((xc-CENTER_HALF, yc, xc+CENTER_HALF, yc), fill=CENTER_COLOR, width=1)
                draw.line((xc, yc-CENTER_HALF, xc, yc+CENTER_HALF), fill=CENTER_COLOR, width=1)

        out = os.path.join(OUT_DIR, base + "_braille.png")
        canvas.save(out)
        processed += 1

    print(f"\nDONE: {processed} images saved → {OUT_DIR}")
    print(f"Missing images: {missing_img}")
    print(f"Empty labels: {empty_labels}")


if __name__ == "__main__":
    run_braille()
