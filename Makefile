build:
	@docker compose --env-file .env build

run:
	@docker compose --env-file .env up

