# snap_labels.py
import os
import glob

YOLO_DIR = r"C:\Users\yyj23\yolov5"
RUN_NAME = "braille"
LABEL_IN = fr"{YOLO_DIR}\runs\detect\{RUN_NAME}\labels"
LABEL_OUT = fr"{YOLO_DIR}\runs\detect\{RUN_NAME}_snapped\labels"

IMG_SIZE = 896
threshold_x = 20 / IMG_SIZE
threshold_y = 20 / IMG_SIZE

def align(values, threshold):
    indexed = sorted([(v, i) for i, v in enumerate(values)])
    groups = [indexed[0]]
    out = {}
    for v, idx in indexed[1:]:
        if abs(v - groups[-1][0]) < threshold:
            groups.append((v, idx))
        else:
            avg = sum(val for val, _ in groups) / len(groups)
            for _, i in groups: out[i] = avg
            groups = [(v, idx)]
    avg = sum(val for val, _ in groups) / len(groups)
    for _, i in groups: out[i] = avg
    return out

def run_snap():
    os.makedirs(LABEL_OUT, exist_ok=True)
    files = glob.glob(os.path.join(LABEL_IN, "*.txt"))

    for path in files:
        name = os.path.basename(path)
        lines = [ln.strip() for ln in open(path) if ln.strip()]

        if not lines:
            open(os.path.join(LABEL_OUT, name), "w").close()
            continue

        data = [line.split() for line in lines]
        xs = [float(d[1]) for d in data]
        ys = [float(d[2]) for d in data]

        ax = align(xs, threshold_x)
        ay = align(ys, threshold_y)

        new_lines = [
            f"{d[0]} {ax[i]:.6f} {ay[i]:.6f} {d[3]} {d[4]}\n"
            for i, d in enumerate(data)
        ]

        with open(os.path.join(LABEL_OUT, name), "w") as f:
            f.writelines(new_lines)

if __name__ == "__main__":
    run_snap()