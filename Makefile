.PHONY : build run-local

# Provide environment variables to tasks
.EXPORT_ALL_VARIABLES:

version=$(shell git log | head -1 | cut -d ' ' -f2)
region=$(or ${AWS_DEFAULT_REGION},'NOT_PROVIDED')
profile=$(or ${AWS_PROFILE},'NOT_PROVIDED')

clean:
	rm -rf ./.eggs ./build/ ./dist/ *.egg-info AUTHORS ChangeLog

requirements:
	pip install -r requirements.txt

build:
	docker build -t prometheus-opendistro-exporter .

run-local:
	docker run -it --rm \
	-p 9210:9210 \
	prometheus-opendistro-exporter \
	$(extra_args)
