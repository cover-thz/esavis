
# @ symbol supresses the line from being printed in the terminal
# This should work on both Windows and Linux.  On Windows the shared library
# is a DLL, on linux it's a .so file

all: 
ifeq ($(OS),Windows_NT)
	@gcc -c peak_find_fcns.c -o peak_find_fcns.o -D DLL_EXPORTS
	@gcc peak_find_fcns.o -o peak_find_fcns.dll -s -shared -Wl,--subsystem,windows
	@echo "Compiled peak_find_fcns.c"
else
	@gcc -c -fpic -o peak_find_fcns.o peak_find_fcns.c
	@gcc -shared -o peak_find_fcns.so peak_find_fcns.o
endif


clean:
	@rm -f peak_find_fcns.o
ifeq ($(OS),Windows_NT)
	@rm -f peak_find_fcns.dll
else
	@rm -f peak_find_fcns.so
endif

