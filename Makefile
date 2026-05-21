run:
	powershell -ExecutionPolicy Bypass -File scripts/run.ps1

reindex:
	powershell -ExecutionPolicy Bypass -File scripts/reindex.ps1

eval:
	powershell -ExecutionPolicy Bypass -File scripts/eval.ps1

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f
