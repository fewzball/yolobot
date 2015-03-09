all:
	@gcc -c -fPIC blowfish.c -o blowfish.o
	# replace soname witih install_name on OSX
	@gcc -shared -Wl,-soname,blowfish.so -o blowfish.so blowfish.o
	@echo "Place blowfish.so in your yolobot/libs directory"

clean:
	@rm -f blowfish.so
	@echo "Cleaned!"

