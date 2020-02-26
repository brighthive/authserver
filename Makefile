COMMIT_TAG		:= $(shell git log | grep commit | head -1 | cut -d' ' -f2 | cut -c1-5)
ORGANIZATION	:= brighthive
PROJECT_NAME	:= authserver
VERSION 		:= 1.1.0
AWS_ECR_REPO	:= 396527728813.dkr.ecr.us-east-2.amazonaws.com

image:
	docker build -t $(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)-$(COMMIT_TAG) .
	docker tag $(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)-$(COMMIT_TAG) $(AWS_ECR_REPO)/$(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)-$(COMMIT_TAG)
	docker push $(AWS_ECR_REPO)/$(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)-$(COMMIT_TAG)

aws_login:
	$(aws ecr get-login --no-include-email --region us-east-2)

release: clean image
	docker tag $(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)-$(COMMIT_TAG) $(AWS_ECR_REPO)/$(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)
	docker push $(AWS_ECR_REPO)/$(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)
	docker tag $(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)-$(COMMIT_TAG) $(AWS_ECR_REPO)/$(ORGANIZATION)/$(PROJECT_NAME):latest
	docker push $(AWS_ECR_REPO)/$(ORGANIZATION)/$(PROJECT_NAME):latest

clean:
	docker rmi -f $(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)-$(COMMIT_TAG)
	docker rmi -f $(AWS_ECR_REPO)/$(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)-$(COMMIT_TAG)
	docker rmi -f $(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)
	docker rmi -f $(AWS_ECR_REPO)/$(ORGANIZATION)/$(PROJECT_NAME):$(VERSION)
	docker rmi -f $(ORGANIZATION)/$(PROJECT_NAME):latest
	docker rmi -f $(AWS_ECR_REPO)/$(ORGANIZATION)/$(PROJECT_NAME):latest
	docker system prune -f



