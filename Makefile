influxdb-setup:
	docker exec -it shorts_influxdb influx -execute "CREATE DATABASE shorts_db WITH DURATION 4w"
	docker exec -it shorts_influxdb influx -execute "CREATE USER shorts WITH PASSWORD 'shorts'"
	docker exec -it shorts_influxdb influx -execute 'GRANT WRITE ON "shorts_db" TO "shorts"'
