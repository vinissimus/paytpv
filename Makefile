.PHONY: test

test:
	pytest --flake8 --cov=paytpv paytpv/tests
