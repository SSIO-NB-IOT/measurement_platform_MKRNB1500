
AC=arduino-cli
OPTIONS=--fqbn arduino:samd:mkrnb1500
DEV=/dev/ttyACM0
SKETCH_NAME=Parametrage

all: deploy

install:
	snap install arduino-cli
	$(AC) core update-index
	$(AC) core update-index
	$(AC) core install arduino:samd
	$(AC) lib install MKRNB
	$(AC) lib install MQTT


deploy: 
	cd $(SKETCH_NAME)
	$(AC) compile $(OPTIONS) $(SKETCH_NAME)
	$(AC) upload -p $(DEV) $(OPTIONS) $(SKETCH_NAME)

.PHONY: all