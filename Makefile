.PHONY: install start stop clean

install:
	@echo "📦 Installing dependencies..."
	npm install
	cd web-analyst-web/frontend && npm install
	cd web-analyst-web/backend && \
		(test -d venv || python3 -m venv venv) && \
		. venv/bin/activate && \
		pip install -r requirements.txt

start:
	@echo "🚀 Starting all services..."
	@trap 'kill 0' EXIT; \
	cd web-analyst-web/backend && . venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload & \
	cd web-analyst-web/frontend && npm run dev & \
	wait

clean:
	@echo "🧹 Cleaning..."
	rm -rf node_modules web-analyst-web/frontend/node_modules
	rm -rf web-analyst-web/backend/__pycache__ web-analyst-web/backend/.pytest_cache
