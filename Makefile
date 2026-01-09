APP_NAME=lstm-api
AWS_REGION?=sa-east-1
AWS_ACCOUNT_ID?=$(shell aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "SET_YOUR_ACCOUNT_ID")
ECR_REPO=$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(APP_NAME)
AWS_PROFILE?=default

.PHONY: help setup train run-local test-api docker-build docker-run aws-login aws-push tf-init tf-validate tf-plan tf-apply tf-destroy deploy-all git-push

help:
	@echo "=== LSTM API Makefile ==="
	@echo "Poetry: setup, train, run-local, test-api"
	@echo "Docker: docker-build, docker-run"
	@echo "AWS: aws-login, aws-push"
	@echo "Terraform: tf-init, tf-validate, tf-plan, tf-apply, tf-destroy"
	@echo "Orquestração: deploy-all"

# ===== PYTHON / POETRY =====
setup:
	poetry install

train:
	poetry run python src/ml/train.py

run-local:
	poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000

test-api:
	poetry run python src/scripts/teste_local.py

# ===== DOCKER =====
docker-build:
	docker build -t $(APP_NAME):latest .

docker-run:
	docker run -p 8000:8000 $(APP_NAME):latest

# ===== AWS ECR =====
aws-login:
	aws ecr get-login-password --region $(AWS_REGION) --profile $(AWS_PROFILE) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

aws-push: aws-login docker-build
	docker tag $(APP_NAME):latest $(ECR_REPO):latest
	docker push $(ECR_REPO):latest
	@echo "✓ Image pushed to ECR: $(ECR_REPO):latest"

# ===== GIT =====
git-push:
	git add .
	git commit -m "Update project MVP"
	git push origin main