#!/usr/bin/python
from operator import itemgetter
import sys



data_file=open("/home/adi-sin/Desktop/2.txt", "w")




current_word = None
#current_count = 0
word = None
text = '"full_text":'
dictn = []

# input comes from STDIN
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()

    # parse the input we got from mapper.py
    word = line.split(',')

    for sent in word:

        if text in sent:
            #sent.replace(text,'')

            print(sent[13:])
            dictn.append(sent[13:])

            

            
        	
op_tw = set(dictn)       	 

for item in op_tw:
    data_file.write("%s\n" % item)      


    

     
            



    



