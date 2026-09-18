.PHONY: install run

install:
	python -m pip install -r requirements.txt

run:
	python -m flask --app app.app run

venv:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	@echo "----------------------------------------"
	@echo "Virtual environment created and dependencies installed."
	@echo "To activate the virtual environment, run 'source .venv/bin/activate'."
	@echo "To run the application, use 'make run'."
	@echo "----------------------------------------"