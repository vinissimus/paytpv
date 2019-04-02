.PHONY: test
test:
	bin/pytest $(args)
	bin/pytest --flake8 --cov=paytpv $(args)
