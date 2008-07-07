

yeahbutter: main.cpp event.cpp post.cpp user.cpp util.cpp
	g++ -o $@ -g $?

dummy_analyzer: dummy.cpp post.cpp
	g++ -o $@ -g $?

dummy:
	make dummy_analyzer

all:
	make yeahbutter
	make dummy_analyzer

clean:
	rm yeahbutter dummy_analyzer