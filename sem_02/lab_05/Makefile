DIR_SRC         := src
DIR_HEADER      := src
DIR_OUT         := out
DIR_CUI         := ui
DIR_CGUI        := gui
DIR_UI          := ui

ADD_DIRS_SRC    := $(foreach dir, $(shell find -L $(DIR_SRC)/ -type d), $(dir:$(DIR_SRC)/%=%))
ADD_DIRS_HEADER := $(foreach dir, $(shell find -L $(DIR_HEADER)/ -type d), $(dir:$(DIR_HEADER)/%=%))
ADD_DIRS_UI     := $(foreach dir, $(shell find -L $(DIR_UI)/ -type d), $(dir:$(DIR_UI)/%=%))

ADD_DIRS_CUI    := $(foreach dir, $(shell find -L $(DIR_HEADER)/$(DIR_CUI)/ -type d), $(dir:$(DIR_HEADER)/$(DIR_CUI)/%=%))
ADD_DIRS_CGUI   := $(foreach dir, $(shell find -L $(DIR_HEADER)/$(DIR_CUI)/$(DIR_CGUI)/ -type d), \
					  $(dir:$(DIR_HEADER)/$(DIR_CUI)/$(DIR_CGUI)/%=%))

ADD_DIRS_OUT    := $(ADD_DIRS_SRC) $(DIR_UI) $(foreach dir, $(ADD_DIRS_UI), $(DIR_UI)/$(dir))

DIRS_OUT        := $(DIR_OUT) $(shell echo "$(foreach dir, $(ADD_DIRS_OUT), $(DIR_OUT)/$(dir))" | tr ' ' '\n' | sort -u)

SRCS := $(wildcard $(DIR_SRC)/*.cpp) \
	    $(foreach dir, $(ADD_DIRS_SRC), $(wildcard $(DIR_SRC)/$(dir)/*.cpp))
OBJS := $(SRCS:$(DIR_SRC)/%.cpp=$(DIR_OUT)/%.o)
DEPS := $(wildcard $(DIR_OUT)/*.d) \
	    $(foreach dir, $(ADD_DIRS_OUT), $(wildcard $(DIR_OUT)/$(dir)/*.d))
UIS  := $(wildcard $(DIR_UI)/*.ui) \
		$(foreach dir, $(ADD_DIRS_UI), $(wildcard $(dir)/*.ui))

HEADERS_CUI  := $(wildcard $(DIR_HEADER)/$(DIR_CUI)/*.h) \
		        $(foreach dir, $(ADD_DIRS_CUI), $(wildcard $(DIR_HEADER)/$(DIR_CUI)/$(dir)/*.h))
HEADERS_CGUI := $(wildcard $(DIR_HEADER)/$(DIR_CUI)/$(DIR_CGUI)/*.h) \
		        $(foreach dir, $(ADD_DIRS_CGUI), $(wildcard $(DIR_HEADER)/$(DIR_CUI)/$(DIR_CGUI)/$(dir)/*.h))
SRCS_CUI     := $(wildcard $(DIR_SRC)/$(DIR_CUI)/*.cpp) \
		        $(foreach dir, $(ADD_DIRS_CUI), $(wildcard $(DIR_SRC)/$(DIR_CUI)/$(dir)/*.cpp))

MOC_CUIS    := $(foreach file, $(HEADERS_CUI), $(dir $(file:$(DIR_HEADER)/%=$(DIR_OUT)/%))moc_$(notdir $(file:%.h=%.cpp)))
UI_HEADERS  := $(foreach file, $(HEADERS_CGUI), $(dir $(file:$(DIR_HEADER)/%=$(DIR_OUT)/%))ui_$(notdir $(file)))

FLAGS    = -std=c++17 -Wall -Werror -Wpedantic -Wextra -I$(DIR_HEADER) \
		   $(foreach dir, $(ADD_DIRS_HEADER), -I$(DIR_HEADER)/$(dir))  \
		   -I$(DIR_OUT)/$(DIR_CUI)/$(DIR_CGUI)                        \
		   $(foreach dir, $(ADD_DIRS_CGUI), -I$(DIR_OUT)/$(DIR_CUI)/$(DIR_CGUI)/$(dir))
LFLAGS   = $(shell pkg-config --libs Qt5Widgets)
ADDFLAGS =

MOCFLAGS = -I$(DIR_HEADER) $(foreach dir, $(ADD_DIRS_CUI), -I$(DIR_HEADER)/$(DIR_CUI)/$(dir)) 

.PHONY: build debug clean run test default

default: drun

run: build
run:
	./app.out

test:
	@echo FLAGS: $(FLAGS)

drun: debug
drun:
	./app.out

$(DIR_OUT)/.build%: | $(DIR_OUT)
	rm -rf $(DIR_OUT)/*
	rm -f $(DIR_OUT)/.build*
	rm -f *.out
	touch $@

build: $(DIR_OUT)/.buildrelease app.out

debug: FLAGS += -g3
debug: $(DIR_OUT)/.builddebug app.out

$(DIRS_OUT):
	mkdir -p $@

$(DIR_OUT)/%.o: ADDFLAGS = 
$(DIR_OUT)/main.o $(SRCS_CUI:$(DIR_SRC)/%.cpp=$(DIR_OUT)/%.o): \
	ADDFLAGS = $(shell pkg-config --cflags Qt5Widgets)  \
	-I$(DIR_OUT)/$(DIR_CUI)                  \
	$(foreach dir, $(ADD_DIRS_CUI), -I$(DIR_OUT)/$(DIR_CUI)/$(dir))

$(DIR_OUT)/%.o: $(DIR_SRC)/%.cpp | $(DIRS_OUT)
	@g++ $(FLAGS) $(ADDFLAGS) -MM -MF $(@:%.o=%.d) -MT $@ -c -o /dev/null \
		 $(@:$(DIR_OUT)/%.o=$(DIR_SRC)/%.cpp)
	g++ $(FLAGS) $(ADDFLAGS) -c -o $@ $(@:$(DIR_OUT)/%.o=$(DIR_SRC)/%.cpp)

define ui_to_header =
$(subst ui_,, $(1:$(DIR_OUT)/$(DIR_CUI)/$(DIR_CGUI)/%.h=$(DIR_UI)/%.ui))
endef
define ui_recipe =
	uic -o $@ $<
endef
define generate_ui_rule =
source := $(call ui_to_header, $1)
$1: $${source} ; $${ui_recipe}
endef

define moc_to_header =
$(subst moc_,, $(1:$(DIR_OUT)/%.cpp=$(DIR_HEADER)/%.h))
endef
define moc_recipe =
 	moc $(MOCFLAGS) -o $@ $<
endef
define generate_moc_rule =
source := $(call moc_to_header, $1)
$1: $${source} ; $${moc_recipe}
endef

app.out: $(OBJS) | $(DIRS_OUT)
	g++ $(FLAGS) -o app.out $(OBJS) $(LFLAGS)

include $(DEPS)

# Generate moc and ui dependencies
$(foreach file, $(MOC_CUIS), $(eval $(subst moc_,, $(file:.cpp=.o)): $(file)))
$(foreach file, $(MOC_CUIS), $(eval $(call generate_moc_rule, $(file))))
$(DIR_OUT)/main.o: $(UI_HEADERS)
$(foreach file, $(UI_HEADERS), $(eval $(subst ui_,, $(file:.h=.o)): $(file)))
$(foreach file, $(UI_HEADERS), $(eval $(call generate_ui_rule, $(file))))

clean:
	rm -f $(DIR_OUT)/.build*
	rm -rf $(DIR_OUT)/*

