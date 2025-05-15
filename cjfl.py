import pandas as pd

# 1. 경기 결과 데이터 불러오기
df = pd.read_excel("경기결과 정리표.xlsx")  # 파일명은 네가 갖고 있는 이름으로 수정

# 2. 조 편성 정보 정의
group_data = {
    "1학년-남자부-A조": ["1-4", "1-7", "1-9", "1-11"],
    "1학년-남자부-B조": ["1-3", "1-5", "1-8", "1-12"],
    "1학년-남자부-C조": ["1-1", "1-2", "1-6", "1-10"],
    "1학년-여자부-A조": ["1-1", "1-2", "1-5", "1-8"],
    "1학년-여자부-B조": ["1-6", "1-9", "1-10", "1-11"],
    "1학년-여자부-C조": ["1-3", "1-4", "1-7", "1-12"],
    "2학년-남자부-A조": ["2-1", "2-5", "2-6", "2-12"],
    "2학년-남자부-B조": ["2-7", "2-9", "2-10", "2-11"],
    "2학년-남자부-C조": ["2-2", "2-3", "2-4", "2-8"],
    "2학년-여자부-A조": ["2-3", "2-9", "2-10", "2-11"],
    "2학년-여자부-B조": ["2-4", "2-7", "2-8", "2-12"],
    "2학년-여자부-C조": ["2-1", "2-2", "2-6"],
    "3학년-남자부-A조": ["3-2", "3-3", "3-4", "3-6"],
    "3학년-남자부-B조": ["3-1", "3-5", "3-7", "3-12"],
    "3학년-여자부-A조": ["3-4", "3-10", "3-11", "3-12"],
    "3학년-여자부-B조": ["3-2", "3-6", "3-7", "3-8"]
}

# 3. 결과 저장용 딕셔너리 초기화
results = {
    group: {
        team: {"승점": 0, "승": 0, "패": 0, "총점": 0}
        for team in teams
    } for group, teams in group_data.items()
}

# 4. 학년-성별-조 컬럼 추가
df["조_이름"] = df.apply(lambda row: f"{row['학년']}학년-{row['성별']}자부-{row['조']}", axis=1)

# 5. 경기결과 반영
for _, row in df.dropna(subset=["승팀", "패팀", "점수(승팀)", "점수(패팀)"]).iterrows():
    group_key = row["조_이름"]
    if group_key not in results:
        continue

    win_team = f"{row['학년']}-{int(row['승팀'])}"
    lose_team = f"{row['학년']}-{int(row['패팀'])}"
    win_score = row["점수(승팀)"]
    lose_score = row["점수(패팀)"]

    # 승팀 처리
    if win_team in results[group_key]:
        results[group_key][win_team]["승점"] += 3
        results[group_key][win_team]["승"] += 1
        results[group_key][win_team]["총점"] += win_score

    # 패팀 처리
    if lose_team in results[group_key]:
        results[group_key][lose_team]["패"] += 1
        results[group_key][lose_team]["총점"] += lose_score

# 6. 결과 확인 예시
import json
# print(json.dumps(results["1학년-남자부-A조"], indent=2, ensure_ascii=False))
for group_name, teams in results.items():
    print(f"\n=== {group_name} ===")
    for team, stats in teams.items():
        print(f"{team}: {stats}")

with open("전처리_결과.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

