IMAGE_NAME := detect-solar
IMAGES_DIR := $(shell pwd)/images

build_image:
	docker build -t $(IMAGE_NAME) .

docker_run: build_image
	echo $(IMAGES_DIR)
	docker run -v $(IMAGES_DIR):/images -it $(IMAGE_NAME)