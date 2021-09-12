test:
	docker exec shorts_app_test pytest -vv --cov-report term-missing --cov=shorts tests

test-runner-start:
	docker-compose -f docker-compose-test.yml up -d
	docker exec shorts_app_test ./build/check_psql.sh

test-runner-stop:
	docker-compose -f docker-compose-test.yml down
