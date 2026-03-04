.PHONY: start install test clean

start:
	@fuser -k 8000/tcp 2>/dev/null || true
	@sleep 1
	@bash -c "source venv/bin/activate && uvicorn main:app --reload --port 8000"

install:
	python3 -m venv venv
	@bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

test:
	@bash -c "source venv/bin/activate && python test_env.py"

clean:
	rm -rf venv __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
