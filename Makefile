test:
	docker run --rm -v `pwd`:/app shorts-main pytest --cov=shorts tests
