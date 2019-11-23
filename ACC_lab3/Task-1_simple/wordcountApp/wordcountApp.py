from celery import Celery
import urllib.request
import os
import json

# Where the downloaded files will be stored
BASEDIR="/home/ubuntu/Task-1_simple/downloadedFiles"

# Create the app and set the broker location (RabbitMQ)
app = Celery('wordcountApp',
	backend='rpc://',
	broker='pyamqp://guest@localhost//')

@app.task
def download(url, filename):
    """
    Download a page and save it to the BASEDIR directory
      url: the url to download
      filename: the filename used to save the url in BASEDIR
    """
    response = urllib.request.urlopen(url)
    data = response.read()
    with open(BASEDIR+"/"+filename,'wb') as file:
        file.write(data)
    file.close()

@app.task
def list():
	""" Return an array of all downloaded files """
	listOfWords = [["hon",2],["han",4],["hen",1]]
	return(listOfWords)

@app.task
def jsonTextProces():

    file = open("small_twitter_extract.json", "r")
    edited_tweets = {}

    lineCount = 0

    for line in file:
        lineCount += 1

        if lineCount%2 == 1 : # Since every other line is empty we only look at uneaven lines.
            jsonTweet = json.loads(line)
            if jsonTweet["retweeted"] == False:
                jsonTweet["text"] = [word.strip(",.") for word in jsonTweet["text"].lower().split()]
                edited_tweets[jsonTweet["id"]] = jsonTweet["text"]
                
    file.close()
    return edited_tweets


@app.task
def countTheWord(textList, checkWord):
    frequency = 0
    for word in textList:
        if word == checkWord:
            frequency += 1
    return frequency

@app.task
def countPronouns():
    frequentPronouns = {"Han": 0, "Hon": 0, "Den": 0, "Det": 0, "Denna": 0, "Denne": 0, "Hen": 0}
    tweetTupleList = jsonTextProces().items()
    tweetWordList = [wordList[1] for wordList in tweetTupleList]

    for tweet in tweetWordList:  
        frequentPronouns["Han"] = frequentPronouns["Han"] + countTheWord(tweet, "han")
        frequentPronouns["Hon"] = frequentPronouns["Hon"] + countTheWord(tweet, "hon")
        frequentPronouns["Den"] = frequentPronouns["Den"] + countTheWord(tweet, "den")               
        frequentPronouns["Det"] = frequentPronouns["Det"] + countTheWord(tweet, "det")
        frequentPronouns["Denna"] = frequentPronouns["Denna"] + countTheWord(tweet, "denna")
        frequentPronouns["Denne"] = frequentPronouns["Denne"] + countTheWord(tweet, "denne")
        frequentPronouns["Hen"] = frequentPronouns["Hen"] + countTheWord(tweet, "hen")

    print (frequentPronouns)

    #barChart(frequentPronouns)

    return frequentPronouns
