from detect_runs import run_detection
from snap_labels import run_snap
from dotline import run_dotline
from braille_canvas import run_braille
from blend_results import run_blend

if __name__ == "__main__":
    print("==== 전체 파이프라인 시작 ====\n")

    run_detection()
    run_snap()
    run_braille()     
    run_dotline()     
    run_blend()

    print("\n🎉 모든 과정 완료 (Detect → Snap → Dotline → Braille → Blend) 🎉")