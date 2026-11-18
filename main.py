import json     # json 라이브러리 불러오기
import os
import time     # 시간 측정 라이브러리 불러오기


# --------------------------------
# (공통) 두 행렬의 곱셈 및 누적 계산
# --------------------------------

def mac(pattern, filter_data):

    score = 0.0   # 점수를 저장할 변수
    n = len(pattern)    # 배열의 크기 확인
    for i in range(n):  # 행(가로) 반복
        for j in range(n):  # 열(세로) 반복
            score += pattern[i][j] * filter_data[i][j]  # pattern[i][j] = 입력 패턴의 숫자 / score += ... = 곱한 값을 점수에 누적
    return score    # 최종 점수 반환


# --------------------------------
# (공통) 두 점수를 비교하여 최종 결과 결정
# --------------------------------

def classify(score_a, score_b, label_a="A", label_b="B"):
    EPSILON = 1e-9  # EPSILON = 0.000000001
    diff = abs(score_a - score_b)   # abs = 절댓값을 구하는 함수
    if diff < EPSILON:
        return "UNDECIDED"  # 두 점수의 차이가 EPSILON보다 작으면 결과를 결정하지 않겠다.
    if score_a > score_b:
        return label_a
    else:
        return label_b


# --------------------------------
# (모드2) 정규화 함수 만들기
# --------------------------------

def normalize_label(label):
    label = str(label).strip().lower()
    if label in ["+", "cross"]:
        return "Cross"
    if label == "x":
        return "X"
    return "UNDECIDED"


# --------------------------------
# (모드1) 사용자에게 행렬을 입력받는 함수
# --------------------------------

def input_matrix(name, n):  # input_matrix = 함수 / name = 행렬의 이름을 전달받는 변수 / n = 행렬의 크기를 전달받는 변수

    matrix = [] # 입력받은 숫자를 저장할 빈 리스트를 만듬
    print(f"{name} ({n}줄 입력, 공백 구분)")   # 사용자에게 한 줄 입력받기
    for i in range(n):  # n번 반복하는 반복문
        while True: # 조건이 참인 동안 계속 반복하는 반복문 (사용자가 잘못된 형식으로 입력했을 때 올바르게 입력할 때까지 입력받기 위함)
            try:    # 오류가 발생할 가능성이 있는 코드 실행
                row = input().split()   # input() = 사용자에게 키보드 입력을 받음 / .split() = 입력된 문자열을 공백 기준으로 분리
                if len(row) != n:   # len(row) = 리스트에 들어있는 데이터 개수 / != 같지 않다는 의미
                    raise ValueError    # 강제로 ValueError 오류를 발생시킴
                row = list(map(float, row))     # 입력받은 문자열을 숫자로 변환 / map(float, row) = 각각 실수형(1 > 1.0)으로 변환됨
                matrix.append(row)  # 입력받은 한 행을 전체 행렬에 추가
                break   # while True 반복문 종료

            except ValueError:  # 오류 발생 시 처리
                print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")

    return matrix   # 최종 행렬 반환


# --------------------------------
# (공통) 연신 시간 측정 함수
# --------------------------------

def measure_time(pattern, filter_data, repeat=10):  # 반복 측정

    total_time = 0
    for _ in range(repeat):
        start = time.perf_counter()    # start = 연산 시작 시간
        mac(pattern, filter_data)
        end = time.perf_counter()   # end = 연산 종료 시간
        total_time += end - start   # end - start: 걸린 시간(초)
    return (total_time / repeat) * 1000   # * 1000: 밀리초(ms)로 변환


# --------------------------------
# 메인 실행 로직
# --------------------------------
def main():
    print("\n=== Mini NPU Simulator ===\n")
    print("[모드 선택]\n")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    mode = input("선택: ").strip()

    if mode == "1":
        print("\n#---------------------------------------")
        print("# [1] 필터 입력")
        print("#---------------------------------------")
        filter_a = input_matrix("필터 A", 3)
        filter_b = input_matrix("필터 B", 3)

        print("\n#---------------------------------------")
        print("# [2] 패턴 입력")
        print("#---------------------------------------")
        pattern = input_matrix("패턴", 3)

        score_a = mac(pattern, filter_a)
        score_b = mac(pattern, filter_b)
        result = classify(score_a, score_b)
        avg_time = measure_time(pattern, filter_a)

        print("\n#---------------------------------------")
        print("# [3] MAC 결과")
        print("#---------------------------------------")
        print(f"A 점수: {score_a}")
        print(f"B 점수: {score_b}")
        print(f"연산 시간(평균/10회): {avg_time:.3f} ms")
        
        if result == "UNDECIDED":
            print(f"판정: 판정 불가 (|A-B| < 1e-9)")
        else:
            print(f"판정: {result}")

    elif mode == "2":
        if not os.path.exists("data.json"):
            print("data.json 파일이 없습니다!")
            return

        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        
        filters = data.get("filters", {})
        patterns_dict = data.get("patterns", {})

        print("\n#---------------------------------------")
        print("# [1] 필터 로드")
        print("#---------------------------------------")
        for f_key in filters.keys():
            # size_5 -> size_5 (공백 맞춰서 출력)
            print(f"✓ {f_key:<7} 필터 로드 완료 (Cross, X)")

        print("\n#---------------------------------------")
        print("# [2] 패턴 분석 (라벨 정규화 적용)")
        print("#---------------------------------------")
        
        results_summary = []
        perf_stats = {}

        for case_id, case_info in patterns_dict.items():
            pattern = case_info.get("input")
            expected = normalize_label(case_info.get("expected", ""))
            
            # ID에서 사이즈 추출 (size_5_1 -> 5)
            size_val = case_id.split("_")[1]
            f_group = filters.get(f"size_{size_val}", {})
            f_cross = f_group.get("cross")
            f_x = f_group.get("x")

            # 연산 및 시간 측정
            s_cross = mac(pattern, f_cross)
            s_x = mac(pattern, f_x)
            avg_t = measure_time(pattern, f_cross)
            
            # 성능 데이터 저장
            if size_val not in perf_stats:
                perf_stats[size_val] = []
            perf_stats[size_val].append(avg_t)

            # 판정 및 결과 저장
            pred = classify(s_cross, s_x, "Cross", "X")
            status = "PASS" if pred == expected else "FAIL"
            
            print(f"- -- {case_id} ---")
            print(f"Cross 점수: {s_cross:.16f}")
            print(f"X 점수: {s_x:.16f}")
            
            fail_msg = " (동점 규칙)" if pred == "UNDECIDED" else ""
            print(f"판정: {pred} | expected: {expected} | {status}{fail_msg}")
            
            results_summary.append({
                "id": case_id, 
                "status": status, 
                "reason": "동점(UNDECIDED) 처리 규칙에 따라 FAIL" if pred == "UNDECIDED" else "오답"
            })

        print("\n#---------------------------------------")
        print("# [3] 성능 분석 (평균/10회)")
        print("#---------------------------------------")
        print(f"{'크기':<10}{'평균 시간(ms)':<18}{'연산 횟수':<10}")
        print("-" * 40)
        for s in sorted(perf_stats.keys(), key=int):
            avg_val = sum(perf_stats[s]) / len(perf_stats[s])
            ops = int(s) * int(s)
            print(f"{s+'×'+s:<12}{avg_val:<20.3f}{ops:<10}")

        print("\n#---------------------------------------")
        print("# [4] 결과 요약")
        print("#---------------------------------------")
        total = len(results_summary)
        passed = len([r for r in results_summary if r["status"] == "PASS"])
        
        print(f"총 테스트: {total}개")
        print(f"통과: {passed}개")
        print(f"실패: {total - passed}개")

        if total - passed > 0:
            print("\n실패 케이스:")
            for r in results_summary:
                if r["status"] == "FAIL":
                    print(f"- {r['id']}: {r['reason']}")

if __name__ == "__main__":
    main()
            
else:
    if mode != "1" and mode != "2":
        print("잘못된 모드를 선택했습니다.")
