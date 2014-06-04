#!/bin/bash

SHELL=/bin/bash
WGET=/usr/bin/wget
PYTHON=/usr/bin/python

CORPUS_FILE=ur3_20140114_public.atf
NAMES_FILE=names.txt
WORDS_FILE=words.txt

OUTPUT_NAMES_FILE=names_p.csv
OUTPUT_WORDS_FILE=words_p.csv
OUTPUT_SIGNS_FILE=sign_frequency.txt

all:  $(CORPUS_FILE) $(NAMES_FILE) $(WORDS_FILE) 
	@echo "Generating p-scores of names based on names..."
	$(PYTHON) ./frequency.py $(NAMES_FILE) $(NAMES_FILE) > $(OUTPUT_NAMES_FILE)
	@echo "Generating p-scores of randomly-chosen words based on names..."
	$(PYTHON) ./frequency.py $(NAMES_FILE) $(WORDS_FILE) > $(OUTPUT_WORDS_FILE)
	@echo "Generating sign chain frequencies for names..."
	$(PYTHON) ./signs.py $(NAMES_FILE) > $(OUTPUT_SIGNS_FILE)

words: $(WORDS_FILE)

$(CORPUS_FILE):
	if [ ! -f "$(CORPUS_FILE)" ]; then \
		@echo "Getting full corpus file from GitHub repo..."; \
		$(WGET) https://raw.githubusercontent.com/brandontoner/wwucsseniorprojectcuneiform/master/data/ur3_20140114_public.atf -O $(CORPUS_FILE); \
	fi

$(NAMES_FILE):
	if [ ! -f "$(NAMES_FILE)" ]; then \
		@echo "Getting names file from GitHub repo..."; \
		$(WGET) https://raw.githubusercontent.com/brandontoner/wwucsseniorprojectcuneiform/master/data/names.txt -O $(NAMES_FILE); \
	fi

$(WORDS_FILE):
	@echo "Generating a collection of random words from the corpus..."
	$(SHELL) ./make_words.sh > $(WORDS_FILE)

clean:
	rm -f $(WORDS_FILE) $(OUTPUT_NAMES_FILE) $(OUTPUT_WORDS_FILE) $(OUTPUT_SIGNS_FILE)
