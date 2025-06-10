import pandas as pd
import json
from collections import defaultdict

# 엑셀 파일 불러오기
filepath = "cjfl.xlsx"
df = pd.read_excel(filepath)

# 조 편성 정보
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
    "2학년-여자부-C조": ["2-1", "2-2", "2-2", "2-6"],  # 2-2가 중복되어 있어서 수정 필요할 수 있음
    "3학년-남자부-A조": ["3-2", "3-3", "3-4", "3-6"],
    "3학년-남자부-B조": ["3-1", "3-5", "3-7", "3-12"],
    "3학년-여자부-A조": ["3-4", "3-10", "3-11", "3-12"],
    "3학년-여자부-B조": ["3-2", "3-6", "3-7", "3-8"]
}

# 결과 초기화
results = {
    group: {
        team: {
            "승점": 0,
            "승": 0,
            "패": 0,
            "총점": 0,
            "실점": 0,
            "맞대결": {},
            "isWildcard": False
        } for team in teams
    } for group, teams in group_data.items()
}

# 조 이름 생성
df["조_이름"] = df.apply(lambda row: f"{row['학년']}학년-{row['성별']}자부-{row['조']}", axis=1)

# 점수 누적
for _, row in df.dropna(subset=["승팀", "패팀", "점수(승팀)", "점수(패팀)"]).iterrows():
    group = row["조_이름"]
    if group not in results:
        continue
    win = f"{row['학년']}-{int(row['승팀'])}"
    lose = f"{row['학년']}-{int(row['패팀'])}"
    ws, ls = row["점수(승팀)"], row["점수(패팀)"]

    if win in results[group]:
        results[group][win]["승점"] += 3
        results[group][win]["승"] += 1
        results[group][win]["총점"] += ws
        results[group][win]["실점"] += ls
        results[group][win]["맞대결"][lose] = "승"
    if lose in results[group]:
        results[group][lose]["패"] += 1
        results[group][lose]["총점"] += ls
        results[group][lose]["실점"] += ws
        results[group][lose]["맞대결"][win] = "패"

# 와일드카드 계산 (수정된 부분)
from collections import defaultdict

# 각 학년+성별별로 2등 팀들을 수집
second_places = defaultdict(list)

for group, teams in results.items():
    # 3학년은 와일드카드 대상이 아님
    if group.startswith("3학년"):
        continue
    
    # 조 내에서 순위 정렬 (승점 우선, 득실차 차선)
    sorted_teams = sorted(
        teams.items(),
        key=lambda item: (
            -item[1]["승점"],  # 승점 내림차순
            -(item[1]["총점"] - item[1]["실점"])  # 득실차 내림차순
        )
    )
    
    # 2등 팀이 존재하는 경우에만
    if len(sorted_teams) >= 2:
        # 학년-성별 키 생성 (예: "1학년-남자부")
        grade_gender = "-".join(group.split("-")[:2])
        second_team = sorted_teams[1]  # (팀명, 팀정보) 형태
        second_places[grade_gender].append({
            "group": group,
            "team": second_team[0],
            "data": second_team[1]
        })

# 각 학년-성별별로 최고 2등 팀을 와일드카드로 선정
for grade_gender, candidates in second_places.items():
    if not candidates:
        continue
    
    # 2등 팀들 중에서 최고 성적 팀 선정
    best_second = max(
        candidates,
        key=lambda x: (
            x["data"]["승점"],  # 승점 우선
            x["data"]["총점"] - x["data"]["실점"]  # 득실차 차선
        )
    )
    
    # 와일드카드 표시
    group_name = best_second["group"]
    team_name = best_second["team"]
    results[group_name][team_name]["isWildcard"] = True
    
    print(f"🏆 와일드카드: {grade_gender} - {team_name} (승점: {best_second['data']['승점']}, 득실차: {best_second['data']['총점'] - best_second['data']['실점']})")

# 경기 일정 JSON 만들기
schedule_json = defaultdict(list)
for _, row in df.iterrows():
    grade = int(row["학년"])
    schedule_json[grade].append({
        "날짜": str(row["날짜"].date()) if pd.notna(row["날짜"]) else "",
        "성별": row["성별"],
        "조": row["조"],
        "경기": row["경기"],
        "승팀": str(int(row["승팀"])) if pd.notna(row["승팀"]) else None,
        "점수승": int(row["점수(승팀)"]) if pd.notna(row["점수(승팀)"]) else None,
        "점수패": int(row["점수(패팀)"]) if pd.notna(row["점수(패팀)"]) else None,
        "패팀": str(int(row["패팀"])) if pd.notna(row["패팀"]) else None,
    })

# JSON 파일 저장
with open("팀별점수.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

with open("학년별경기일정.json", "w", encoding="utf-8") as f:
    json.dump(schedule_json, f, ensure_ascii=False, indent=2)

print("✅ 저장 완료")

# 디버깅용: 각 조별 순위 출력
print("\n📊 각 조별 순위:")
for group, teams in results.items():
    if not teams:  # 빈 조는 건너뛰기
        continue
    print(f"\n{group}:")
    sorted_teams = sorted(
        teams.items(),
        key=lambda item: (
            -item[1]["승점"],
            -(item[1]["총점"] - item[1]["실점"])
        )
    )
    for i, (team, data) in enumerate(sorted_teams, 1):
        wildcard_str = " 🏆(와일드카드)" if data["isWildcard"] else ""
        print(f"  {i}등: {team} - 승점:{data['승점']}, 득실차:{data['총점']-data['실점']}{wildcard_str}")