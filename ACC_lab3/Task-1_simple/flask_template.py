import os
import random
import time
import json
from celery import Celery
from celery.result import AsyncResult
from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify, send_from_directory


#START CELERY CONFIG

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

#Celery configuration
app.config['CELERY_BROKER_URL'] = 'pyamqp://rabbit_test_user:1234@localhost/rabbit_test_vhost'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'


#Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)


#START CELERY METHODS

@celery.task
def example_celery_method(): #This is just an example
	time.sleep(4)
	return 'I have sleept for 4 seconds'


#END CELERY METHODS
#START FLASK METHODS

#This is just to render the simple webpage
@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'GET':
		return render_template('index.html')

#This is a curl test method without celery worker input
@app.route('/test', methods=['GET'])
def test_curl():
	if request.method == 'GET':
		return 'hello, World'

#This is a curl test method with celery worker input
@app.route('/celery_test', methods=['GET'])
def test_celery_curl():
	if request.method == 'GET':
		task = example_celery_method.delay()
		async_result = AsyncResult(id=task.task_id, app=celery)
		processing_result = async_result.get()
		return str(processing_result)


if __name__ == '__main__':
    app.run(debug=True)

#if __name__ == '__main__':
#	app.run(host='0.0.0.0', debug=True)




