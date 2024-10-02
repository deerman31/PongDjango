COMPOSE = docker compose -f ./src/compose.yml

all: up

up:
	@echo "\033[1;33mStarting containers\033[0m"
	@$(COMPOSE) up -d --build
	@$(COMPOSE) up

down:
	@echo "\033[1;33mStopping containers\033[0m"
	@$(COMPOSE) down


start:
	@echo "\033[1;33mStarting containers\033[0m"
	@$(COMPOSE) start


stop:
	@echo "\033[1;33mStopping containers\033[0m"
	@$(COMPOSE) stop

restart:
	@echo "\033[1;33mRestarting containers\033[0m"
	@$(COMPOSE) restart


clean:
	@echo "\033[1;33mCleaning containers\033[0m"
	@$(COMPOSE) down -v --rmi all --remove-orphans

fclean:
	@echo "\033[1;33mCleaning containers\033[0m"
	@$(COMPOSE) down -v
	@echo "\033[1;33mPruning Docker\033[0m"
	@docker system prune -a --force
	@echo "\033[1;33mRemoving Docker Volumes\033[0m"
	@docker volume prune --force

re:
	@$(MAKE) down
	@$(MAKE) all

status:
	@echo "\n\033[1;33mContainers\033[0m"
	@docker ps -a
	@echo "\n\033[1;33mImages\033[0m"
	@docker images
	@echo "\n\033[1;33mVolumes\033[0m"
	@docker volume ls
	@echo "\n\033[1;33mNetworks\033[0m"
	@docker network ls

