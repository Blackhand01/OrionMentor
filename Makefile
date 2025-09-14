.PHONY: run-flask run-gradio test fmt

run-flask:
	python -m orionmentor.app.server

run-gradio:
	python demo/gradio_app.py

test:
	pytest -q
#source venv-orionmentor/bin/activate