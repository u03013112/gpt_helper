TAG=v2
ACCOUNT=u03013112
IMAGE=${ACCOUNT}/gpt:${TAG}

all:
	docker build -t ${IMAGE} .
push:
	docker push ${IMAGE} 