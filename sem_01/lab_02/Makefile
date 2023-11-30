.PHONY: run clean default

default: run

out:
	mkdir -p out/

run: out/form.py | out
run:
	./main.py

out/form.py: ui/form.ui | out
	pyuic5 -o out/form.py ui/form.ui

clean:
	rm -rf out/

