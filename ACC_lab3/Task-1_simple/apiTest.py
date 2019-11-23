import os
import random
import time
import json
import matplotlib.pyplot as plt
from celery import Celery
from celery.result import AsyncResult
from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify, send_from_directory


#START CELERY CONFIG

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

#Celery configuration
app.config['CELERY_BROKER_URL'] = 'pyamqp://rabbit_test_user:1234@192.168.1.23:5672/rabbit_test_vhost'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'


#Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)


def my_monitor(app):
    print('monitor started')
    state = app.events.State()
    print(state)
    print(app.connection())
    def announce_succeeded_tasks(event):
        state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = state.tasks.get(event['uuid'])
        print('event exited')

        print('TASK SUCCEEDED: %s[%s] %s' % (
            task.name, task.uuid, task.info(),))

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                'task-succeeded': announce_succeeded_tasks,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)

#END CELERY CONFIG
#START CELERY METHODS


@celery.task
def countTheWord(textList, checkWord):
	frequency = 0
	for word in textList:
		if word == checkWord:
			frequency += 1
	return frequency

@celery.task
def countPronouns():
	start = time.time()

	#TEXT PROCESSING START:
	#Setting path            
	path_to_data = "/home/ubuntu/extVolume/data_full/"

	#Creating file list with path
	file_list = os.listdir(path_to_data)
	edited_tweets = {}

	for filename in file_list:
		tempfile = open(path_to_data+filename, "r")

		lineCount = 0
		for line in tempfile:
			lineCount += 1

			if lineCount%2 == 1 : # Since every other line is empty we only look at uneaven lines.
				jsonTweet = json.loads(line)
				if jsonTweet["retweeted"] == False:
					jsonTweet["text"] = [word.strip(",.?!") for word in jsonTweet["text"].lower().split()]
					edited_tweets[jsonTweet["id"]] = jsonTweet["text"]

		tempfile.close()

	#TEXT PROCESSING END
	#COUNT PRONOUNS START

	frequentPronouns = {"Han": 0, "Hon": 0, "Den": 0, "Det": 0, "Denna": 0, "Denne": 0, "Hen": 0}
	tweetTupleList = edited_tweets.items()

	tweetWordList = [wordList[1] for wordList in tweetTupleList]

	for tweet in tweetWordList:  
		frequentPronouns["Han"] = frequentPronouns["Han"] + countTheWord(tweet, "han")
		frequentPronouns["Hon"] = frequentPronouns["Hon"] + countTheWord(tweet, "hon")
		frequentPronouns["Den"] = frequentPronouns["Den"] + countTheWord(tweet, "den")               
		frequentPronouns["Det"] = frequentPronouns["Det"] + countTheWord(tweet, "det")
		frequentPronouns["Denna"] = frequentPronouns["Denna"] + countTheWord(tweet, "denna")
		frequentPronouns["Denne"] = frequentPronouns["Denne"] + countTheWord(tweet, "denne")
		frequentPronouns["Hen"] = frequentPronouns["Hen"] + countTheWord(tweet, "hen")

	end = time.time()
	elapsed_time = start - end
	return_list = [frequentPronouns, elapsed_time]
	return return_list

#END CELERY METHODS
#START FLASK METHODS

@app.route('/', methods=['GET', 'POST'])
def index():
	completion_time_dictionary = {}
	task_list = []
	async_result_dictionary = {}
	processing_result_dictionary = {}

	if request.method == 'GET':
		return render_template('apiTest.html')

	if request.method == 'POST':
		if request.form['get_pronouns_button'] == 'Get pronouns':
			total_time_start = time.time()
			number_of_calls = int(request.form['number_of_calls'])
			flash("The nr of pronouns is being calculated, please wait...")
			one_key = ''
			for iteration in range(number_of_calls):
				task_list.append(countPronouns.delay())
			
			one_key=task_list[0].task_id
			for task in task_list:
				async_result_dictionary[task.task_id] = AsyncResult(id=task.task_id, app=celery)

			for key in async_result_dictionary.keys():
				processing_result_dictionary[key] = async_result_dictionary[key].get()[0]
				completion_time_dictionary[key] = async_result_dictionary[key].get()[1]
			
			theAnswer = processing_result_dictionary[one_key]
			plt.bar(*zip(*theAnswer.items()))
			CURDIR = os.getcwd()
			plt.savefig(CURDIR+"/"+'test.png', bbox_inches='tight')
			
			for key in completion_time_dictionary.keys():
				flash("For task id: " +str(key) + "the completion time is: " + str(completion_time_dictionary[key]))

			print(processing_result_dictionary)
			print(completion_time_dictionary)
			total_time_end = time.time()
			flash('This is the total time passed: '+ str(total_time_end-total_time_start))
			return render_template('result.html', image_name='test.png')

	return redirect(url_for('index'))

@app.route('/result')
def send_image():
	return send_from_directory(os.getcwd(), 'test.png')



#if __name__ == '__main__':
#    app.run(debug=True)

if __name__ == '__main__':
	#my_monitor(celery)
	app.run(host='0.0.0.0', debug=True)




