CC=g++
CFLAGS=-std=c++11 -O3 -I.
DEPS_HPP = circom.hpp calcwit.hpp fr.hpp
DEPS_O = main.o calcwit.o fr.o fr_asm.o

ifeq ($(shell uname),Darwin)
	NASM=nasm -fmacho64 --prefix _
endif
ifeq ($(shell uname),Linux)
	NASM=nasm -felf64
endif
	
all: commitmentproof_63DDAF7A-FB4F-4DB3-86C3-F641B6C9CC30
	
%.o: %.cpp $(DEPS_HPP)
	$(CC) -c $< $(CFLAGS)

fr_asm.o: fr.asm
	$(NASM) fr.asm -o fr_asm.o
	
commitmentproof_63DDAF7A-FB4F-4DB3-86C3-F641B6C9CC30: $(DEPS_O) commitmentproof_63DDAF7A-FB4F-4DB3-86C3-F641B6C9CC30.o
	$(CC) -o commitmentproof_63DDAF7A-FB4F-4DB3-86C3-F641B6C9CC30 *.o -lgmp 
