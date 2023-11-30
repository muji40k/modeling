.PHONY: run clean default clear

default: run

UIS := $(wildcard ui/*.ui)
UIS_OUT := $(UIS:ui/%.ui=out/%.py)

clear:
	./main.py

out:
	mkdir -p out/

run: $(UIS_OUT) | out
run:
	./main.py

out/%.py: ui/%.ui | out
	pyuic5 -o $@ $^

clean:
	rm -rf out/

