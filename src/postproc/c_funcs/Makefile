
# @ symbol supresses the line from being printed in the terminal

ifeq ($(OS),Windows_NT)
	peak_find_fcns.o: peak_find_fcns.c
		@gcc -c peak_find_fcns.c -o peak_find_fcns.o -D DLL_EXPORTS
		@gcc peak_find_fcns.o -o peak_find_fcns.dll -s -shared -Wl,--subsystem,windows
		@echo "Compiled peak_find_fcns.c"


	clean:
		@rm -f peak_find_fcns.o
		@rm -f peak_find_fcns.dll

else


endif
