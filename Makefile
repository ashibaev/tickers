.PHONY: prepare fill web clear

prepare:
	( \
		python3.7 -m venv .venv; \
		. .venv/bin/activate; \
		pip install -r requirements.txt; \
		pip install -r requirements-dev.txt; \
	)

fill:
	( \
		make clear; \
		docker-compose --file compose-fill-database.yml up --abort-on-container-exit --build; \
	)

web:
	( \
		make clear; \
		docker-compose --file compose-web.yml up --build; \
	)

clear:
	rm -rf *.pyc */__pycache__