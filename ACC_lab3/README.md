# ACC_lab3 Task-1

## a) Making VMs up to date:

In order to make the VM up to date (manually writing in the bash promt) 

Do the following in order:

```
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip -y
sudo locale-gen sv_SE.UTF-8
pip3 intsall --upgrade pip
sudo apt-get install rabbitmq-server -y
sudo pip3 install celery
sudo pip3 install matplotlib
sudo pip3 install Flask
```
*Compressd to one line:*
```
sudo apt update && sudo apt upgrade -y; sudo apt install python3-pip -y; sudo locale-gen sv_SE.UTF-8; pip3 install --upgrade pip; sudo apt-get install rabbitmq-server -y; sudo pip3 install celery; sudo pip3 install matplotlib; sudo pip3 install Flask
```



## b) How to transfer and uncompress files:

**To send file(dir) from the machine you have the file on:**

```
scp -i <PATH_to_private_key> -vp <PATH_to_file> <username_on_VM>@<public_IP_to_vm>
```
*The -v and -p flags means verbose and recursively, respectivly*

**To uncompress a file using bash prompt:**
```
tar -xvzf data.tar.gz
```
*-x extract, -v, --verbose, -z compressed with gzip. -f  name of the archive file to operate on.*



## c) How to run the application:
```cd``` into the folder ```~/ACC_lab3/Task-1_simple/``` with two terminals and do:

```sudo celery worker -A apiTest.celery --loglevel=info``` 
```sudo python3 apiTest.py```

Now it should work!


## d) Separate broker and celery worker:

On the VM that runs the RabbitMQ server do the following:

This will create a rabbitMQ user named <YOURUSER> RabbitUser with a vhost <YOURVHOST>
```
rabbitmqctl add_user <YOURUSER> <YOURPASSWORDHERE>
rabbitmqctl add_vhost <YOURVHOST>
rabbitmqctl set_user_tags <YOURUSER> administrator
rabbitmqctl set_permissions -p <YOURVHOST> <YOURUSER> ".*" ".*" ".*" 
rabbitmqctl delete_user guest #Not necessary
```

In the code for Celery broker you should write:
```
'amqp://<user>:<password>@<ip>/<vhost>'
```




# ACC_lab3 Tutorial

Most of the basic tutorial was from [Linode Celery and RabbitMq](https://www.linode.com/docs/development/python/task-queue-celery-rabbitmq/)

Other interesting links for the Flask side are:
[Miguel Grinberg blog](https://blog.miguelgrinberg.com/post/using-celery-with-flask), 
[Shane Lynn blog](https://www.shanelynn.ie/asynchronous-updates-to-a-webpage-with-flask-and-socket-io/), 
[Victor Salimonov blog](https://medium.com/@salimonov/asynchronous-background-tasks-in-flask-application-using-celery-1ba873d260d0)

##To turn the workers into daemons:

First move the files... 
```
sudo cp ~/ACC_lab3/tutorial/celeryd.service /etc/systemd/system
sudo cp ~/ACC_lab3/tutorial/celeryd /etc/default
```

Make directories for the log files and run it (?) as user ubuntu **(if that is your username)**:
```
sudo mkdir /var/log/celery /var/run/celery
sudo chown <YOURSUPERUSER>:<YOURSUPERUSERGROUP> /var/log/celery /var/run/celery
```

Reload the deamons (files), enable on boot, and activate them:
```
sudo systemctl daemon-reload
sudo systemctl enable celeryd
sudo systemctl start celeryd
```
To reset failed status in ```sudo systemctl``` type:

```systemctl reset-failed```

*to check if the workers are running:*
```
cat /var/log/celery/worker1.log
cat /var/log/celery/worker2.log
```


#just to save (old celeryd and celeryd.service)

```
# The names of the workers. This example create two workers
CELERYD_NODES="worker1 worker2"

# The name of the Celery App, should be the same as the python file
# where the Celery tasks are defined
CELERY_APP="apiTest.celery"

# Log and PID directories
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"

# Log level
CELERYD_LOG_LEVEL=INFO

# Path to celery binary, that is in your virtual environment
CELERY_BIN=/usr/local/bin/celery
```

```
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=ubuntu
Group=ubuntu
EnvironmentFile=/etc/default/celeryd
WorkingDirectory=/home/ubuntu/ACC_lab3/Task-1_simple
ExecStart=/bin/sh -c '${CELERY_BIN} multi start ${CELERYD_NODES} \
  -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
  --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'
ExecStop=/bin/sh -c '${CELERY_BIN} multi stopwait ${CELERYD_NODES} \
  --pidfile=${CELERYD_PID_FILE}'
ExecReload=/bin/sh -c '${CELERY_BIN} multi restart ${CELERYD_NODES} \
  -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
  --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'

[Install]
WantedBy=multi-user.target
```