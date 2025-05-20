
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
    "2학년-여자부-C조": ["2-1", "2-2", "2-6"],
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

# 와일드카드 계산
from collections import defaultdict
second_places = defaultdict(list)

for group, teams in results.items():
    if not group.startswith(("1학년", "2학년")):
        continue
    div_key = "-".join(group.split("-")[:2])
    sorted_teams = sorted(
        teams.items(),
        key=lambda item: (
            -item[1]["승점"],
            -(item[1]["총점"] - item[1]["실점"])
        )
    )
    if len(sorted_teams) >= 2:
        second_places[div_key].append((group, sorted_teams[1][0], sorted_teams[1][1]))

for div, candidates in second_places.items():
    best = max(
        candidates,
        key=lambda x: (x[2]["승점"], x[2]["총점"] - x[2]["실점"])
    )
    g, t, _ = best
    results[g][t]["isWildcard"] = True

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
with open("전처리_결과_승자승_와일드카드.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

with open("학년별_경기일정.json", "w", encoding="utf-8") as f:
    json.dump(schedule_json, f, ensure_ascii=False, indent=2)

print("✅ 저장 완료")
