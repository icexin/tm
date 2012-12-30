This is a tiny machine emulator using a assembly like language.   

* *loader.py* parse the source file and translate it into instructions.    
To simplify the parsing, the parser uses the [PLY](www.dabeaz.com/ply/) library.    
* *tm.py* contains the Machine class on which the instructions running.   
* The *instruction* file contains the instructions set.

