UIS := $(wildcard ui/*.ui)
PYUIS := $(UIS:ui/%.ui=out/%.py)

.PHONY: run clean default

default: run

out:
	mkdir -p out/

run: $(PYUIS) | out
run:
	./main.py

out/%.py : ui/%.ui | out
	pyuic5 -o $@ $^

clean:
	rm -rf out/

