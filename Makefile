install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest

lint:
	ruff check .
	black --check .

format:
	black .
	ruff check . --fix

build-data:
	python -m russian_markets_lab.cli build-all

dashboard:
	streamlit run src/russian_markets_lab/dashboard/app.py
