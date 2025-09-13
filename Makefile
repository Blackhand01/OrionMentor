PY=python
ACT=source .venv/bin/activate

.PHONY: setup dev api ui ingest test fmt lint bench demo screenshots gif docker-build docker-run

setup:
	$(PY) -m venv .venv && $(ACT) && pip install -r requirements.txt
	@echo "Copy .env.example to .env and edit keys if needed."

dev:
	uvicorn app.api:app --reload --port 8000

api:
	uvicorn app.api:app --reload --port 8000

ui:
	$(PY) ui/gradio_app.py

ingest:
	$(PY) scripts/ingest.py

test:
	pytest -q

fmt:
	ruff format && ruff check --fix

lint:
	ruff check

bench:
	$(PY) scripts/benchmark.py

screenshots:
	$(PY) scripts/capture_screens.py

gif:
	# Richiede ffmpeg: brew install ffmpeg
	ffmpeg -y -i assets/demo.mp4 -vf "fps=12,scale=1280:-1:flags=lanczos" assets/demo.gif

docker-build:
	docker build -t orionmentor:latest -f docker/Dockerfile .

docker-run:
	docker run -it --rm -p 8000:8000 -p 7860:7860 --env-file .env -v $(PWD)/data:/app/data orionmentor:latest
