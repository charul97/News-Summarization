from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from googlesearch import search
from gensim.summarization import summarize, keywords
import webbrowser
import requests
import os, time
import urllib.request
from  urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from tkinter import *
from multiprocessing import Process
import json
import logging
import tweepy
from threading import Thread
from http.client import IncompleteRead
from twython import TwythonStreamer
from twython import Twython

#default
x = "Salman Khan"

#code for extraction of data from twitter begins

APP_KEY = "PsP0vF2uonC2RsWXtmR3iogPI"
APP_SECRET = "8E8CzY7Aydh2V7NR1xkD8U7j73Dara0Eom4BeW2IK6F6lfyXj9"
OAUTH_TOKEN = "958244433278971904-U1bNIIPSlJjPSEFi51DpKtAmV0BHo0N"
OAUTH_TOKEN_SECRET = "scAV1sp4qlQE01rsRK2hP3x5zmh8jx8Yd2p0v5WX2TCbR"
STORAGE_PATH= "/home/adi-sin/Desktop/tweety/"
filter_terms=[x]

auth = tweepy.OAuthHandler(APP_KEY, APP_SECRET)
# Setting your access token and secret
auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    # Creating the API object while passing in auth information
api = tweepy.API(auth) 

twitter = Twython(APP_KEY, APP_SECRET)
authi = twitter.get_authentication_tokens()

class TooLongTermException(Exception):
    def __init__(self, index):
        self.index = index

    def get_too_long_index(self):
        return self.index


class StreamListener(TwythonStreamer):
    def __init__(self, APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                 comm_list):
        super().__init__(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        self.tweet_list = comm_list

    def on_success(self, data):
        self.tweet_list.append(data)
        logging.info("tweet captured")

    def on_error(self, status_code, data):
        logging.error(status_code)
        logging.error(data)
        if int(status_code) == 406:
            data = str(data)
            try:
                index = int(data.strip().split()[4])
                logging.error("to remove index:" + str(index))
                raise TooLongTermException(index)
            except ValueError:
                logging.debug("ValueError while trying to extract number")





def twitter_listener(
    APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, comm_list):    
    streamer = StreamListener(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
    comm_list)
    while True:
        try:
            streamer.statuses.filter(track=[', '.join(filter_terms)])
        except requests.exceptions.ChunkedEncodingError:
            print('error, but under control\n')
            pass
        except IncompleteRead:
            print('incompletetereaderror, but under control')
            pass
        except TooLongTermException as e:
            index_to_remove = e.get_too_long_index()
            filter_terms.pop(index_to_remove)



def twitter_writer(comm_list):
    internal_list = []
    time_start = time.time()
    while True:
        if len(internal_list) > 100:
            file_name = STORAGE_PATH + str(round(time.time())) + ".json"
            with open(file_name, 'w+', encoding='utf-8') as output_file:
                json.dump(internal_list, output_file, indent=4)
                internal_list = []
                logging.info('------- Data dumped -------')
                time_stop = time.time()
                logging.info('Time taken for 100 tweets: {0:.2f}s'.format(
                    time_stop - time_start
                ))
                time_start = time.time()
        else:
            for i in range(len(comm_list)):
                internal_list.append(comm_list.pop())
            time.sleep(1)

#code for extraction of data from twitter ends



#function with which twitter code is run
def twit():

    start = time.time()


    comm_list =[]

    listener = Thread(target = twitter_listener, args = (
        APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, comm_list ))
    listener.start()
    writer = Thread(target = twitter_writer, args = (comm_list,))
    writer.start()
    writer.join()
    listener.join() 

    #for streaming data directly into hdfs from flume
    os.system('flume-ng agent -n TwitterAgent -f /home/adi-sin/apache-flume-1.6.0-bin/conf/flume.conf')



# function with which twitter code stops, folder is stored into hdfs and mapreduce is run.
def hadoop():
    os.system('start-all.sh')
    os.system('jps')
    
    # these two lines will run one-time because output folder is specified 
    os.system('hadoop fs -put /home/adi-sin/Desktop/tweety /Deloitte')
    os.system('hadoop jar /home/adi-sin/Desktop/hadoop-*streaming*.jar -mapper /home/adi-sin/Desktop/deloitte_final/code/hadoop/mapper.py -reducer /home/adi-sin/Desktop/deloitte_final/code/hadoop/reducer.py -input /Deloitte/tweety -output /Deloitte/op3')
 




def web():


    info = ""
    sumr1 = "Nothing to show"
    sumr2 = "Nothing to show"



    x= e1.get()
    #scraping starts
    class AppURLopener(urllib.request.FancyURLopener):
        version = "Mozilla/5.0"


    output_file=open('/home/adi-sin/Desktop/1.txt', 'w')
    for j in search(x, tld='com', lang='en', num=10, stop=1, pause=2):
        print(j)
    
        try:
            opener= AppURLopener()
            response= opener.open(j)
            soup = BeautifulSoup(response, 'html.parser')
    
            i=0
            name_box=" "
            while name_box :
                i=i+1
        
                try:
                    name_box = soup.find_all('p')[i].get_text() or "." 
         
                    info = info+name_box
                    output_file.write("%s\n" % name_box)
                    print(name_box)
                    #print(i)
        
                except:
                    break
        except:
            break
        

        
        
        
    output_file.close()

    print(info)

    #scraping ends, info contains the whole data/news content scraped from web.


    #summarization starts
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    #twitter text file is read and stored into content2
    with open('/home/adi-sin/Desktop/2.txt', 'r') as content_file:
        content2 = content_file.read()

    sumr2 = summarize(content2, word_count=200)


    #web scraped text file is read and stored into content1 
    with open('/home/adi-sin/Desktop/1.txt', 'r') as content_file:
        content1 = content_file.read()


    sumr1 = summarize(content1, word_count=400)

    text1.insert(INSERT, sumr1)
    text2.insert(INSERT, sumr2)

    #keywords for plotting
    kw1 = keywords(info)
    kw2 = keywords(content2)

    #result1 stores the summary of scraped news
    with open('/home/adi-sin/Desktop/result1', 'w') as f:
        f.write(sumr1)
    

    #result2 stores the summary of tweets   
    with open('/home/adi-sin/Desktop/result2', 'w') as f:
        f.write(sumr2)
    

#result1 and result2 need to be displayed to user


#code for UI starts
master = Tk()


filename = PhotoImage(file = "/home/charul/Desktop/del3.png")
background_label = Label(master, image=filename)
background_label.place(anchor=N, x= 180, bordermode=OUTSIDE, height=210, width=320)


Label(master, text="Your search",font=("Helvetica", 16), fg="red", bg="#BBDEFB", padx=20, pady=40).grid(row=3, column=1, sticky=E)


e1 = Entry(master)

e1.grid(row=3, column=2,columnspan= 4, rowspan=2, sticky=W)

Button(master, text='Start Live Streaming Twitter Data', command=twit, bg="#0D47A1", fg="white",activebackground="black", activeforeground="white", bd=4, width=30 ).grid(row=13, column=1, sticky=E, pady=10, padx=20)
Button(master, text='Stop Twitter Streaming', command=hadoop,bg="#0D47A1", fg="white",activebackground="black", activeforeground="white", bd=4, width=30).grid(row=13, column=3, sticky=W, pady=10)
Button(master, text='Show Results', command=web, bg="#0D47A1", fg="white",activebackground="black", activeforeground="white", bd=4).grid(row=15, column=3, sticky=W, pady=10, padx= 0)

text1 = Text(master,height=30, bg="black", fg="white")
text2 = Text(master,height=30, bg="black", fg="white")

text1.grid(row = 18,column=1, padx=40)
text1.insert(INSERT, "Summarized result from Web")



text2.grid(row = 18,column=3, padx=40)
text2.insert(INSERT, "Summarized result from Twitter")

master.configure(background='#BBDEFB')
mainloop( )

#code for UI ends
