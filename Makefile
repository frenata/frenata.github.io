SRC=src/posts
POST=posts
CSS=css/style.css
SRCS     := $(wildcard $(SRC)/*.md)
POSTS    := $(patsubst $(SRC)/%.md,$(POST)/%.html,$(SRCS))

all: clean post index

clean:
	rm -f $(POST)/*
	rm -f index.html

post: $(POSTS)

index:
	python3 mkindex.py
	pandoc -s -f markdown -t html -o index.html index.md -c css/style.css
	rm index.md

$(POST)/%.html: $(SRC)/%.md | $(POST)
	pandoc -s -f markdown -t html -o $@ $< -c ../css/style.css
