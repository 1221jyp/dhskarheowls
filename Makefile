# 최종 실행 타겟
all: preprocess commit

# 1. 전처리 실행
preprocess:
	@echo "🔄 Running Python preprocessing..."
	python cjfl.py

# 2. Git 커밋 및 푸시
commit: preprocess
	@echo "✅ Committing and pushing to GitHub..."
	git add .
	git commit -m "Update: 최신 전처리 결과 반영"
	git push origin main
