.PHONY: test
test:
	pytest $(args)
	pytest --flake8 --cov=paytpv $(args)
