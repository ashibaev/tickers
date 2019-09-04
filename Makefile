prepare:
	( \
		python3.7 -m venv .venv; \
		. .venv/bin/activate; \
		pip install -r requirements.txt; \
		pip install -r requirements-dev.txt; \
	)

clear:
	rm -rf .venv *.pyc */__pycache__