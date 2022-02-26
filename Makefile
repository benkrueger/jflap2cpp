CC=g++
CFLAGS=-g -std=c++17 -pthread
SRC=main.cpp
EXE=scanner

srcgen: 
	python3 jflap2cpp.py test2.jff

all: $(SRC)
	$(CC) $(CFLAGS) $(SRC) -o $(EXE)
clean_src:
	rm -rf token.hpp scanner.hpp
run: all
	./$(EXE)
	
clean: $(EXE)
	rm -rf $(EXE) $(JSFL)
	rm -rf token.hpp scanner.hpp