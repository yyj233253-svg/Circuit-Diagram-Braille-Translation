# Circuit-Diagram-Braille-Translation
yolov5와 open cv를 통해 회로도를 인식하고 점자로 점역하는 프로그램입니다.
해당 결과의 예시 : example_result
가중치 파일 : weight 
프로그램 코드 : yyj_finalcode (프로그램코드, dataset(test, train, valid), yolov5...)
설명서, 프로젝트 요약

프로그램 코드는 아래와 같이 구성되어있습니다.
main.py
->detect.py
->snap_labels.py
->braillie_canvas.py
->dotline.py
->blend_results.py

위 파일들과 yolo v5을 다운 받고 weight의 best.pt 파일을 꼭 다운 받아야합니다. 
(설명서를 바탕으로 위 코드에 있는 경로들을 꼭 수정해주셔야 합니다.)

그리고 train, valid, test 중 사진 하나를 선택해서 해당 사진의 경로로 설정하고 프로그램을 실행해보면 됩니다.
그리고 해당 데이터의 class는 data yalm에 저장되어 있습니다. 각 소자의 종류, 방향성에 따라 분류했습니다.
