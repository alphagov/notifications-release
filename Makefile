.PHONY: install refreeze-requirements run venv

install: venv
	.venv/bin/pip install -r requirements.txt

refreeze-requirements:
	uv pip compile requirements.in -o requirements.txt --python .venv/bin/python

run: install
	.venv/bin/python -m flask --app app.app run --debug

venv:
	python3 -m venv .venv
	@echo "----------------------------------------"
	@echo "Dependencies installation is handled by the install target."
	@echo "To activate the virtual environment, run 'source .venv/bin/activate'."
	@echo "To run the application, use 'make run'."
	@echo "----------------------------------------"
