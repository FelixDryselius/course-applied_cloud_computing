import sys
import os
import insertBlob
import subprocess
from celery import Celery

CELERY_BROKER_URL = 'pyamqp://airfoil:group8@10.10.10.8/g8host'
CELERY_RESULT_BACKEND = 'rpc://'

task_name = sys.argv[0][:-3]
celery = Celery(task_name, broker= CELERY_BROKER_URL, backend= CELERY_RESULT_BACKEND)
celery.conf['CELERY_TASK_SERIALIZER'] = 'json'
celery.conf['CELERY_RESULT_SERIALIZER'] = 'json'
celery.conf['CELERY_ACCEPT_CONTENT'] = ['json', 'pickle']

@celery.task
def airfoil_calc(file_name):
    #Creating msh files and convert them to xml
    if not os.path.exists("/home/fenics/shared/murtazo/cloudnaca/msh/"+file_name):
        level = file_name.split("a")[0][1:]
        angle = file_name.split("n")[0].split("a")[1]
        nodes = file_name.split(".")[0].split("n")[1]
        os.chdir("/home/fenics/shared/murtazo/cloudnaca")
        subprocess.run(["./runme.sh", angle, angle, "1", nodes, level])
        os.chdir("/home/fenics/shared/murtazo/cloudnaca/msh")
        subprocess.run(["dolfin-convert", file_name.split(".")[0]+".msh", file_name])
        os.chdir("/home/fenics/shared/murtazo/navier_stokes_solver")
    #Do the airfoil
    subprocess.run(["./airfoil", "10", "0.0001", "10.", "0.01", "../cloudnaca/msh/"+file_name])
    currentPath = os.getcwd()
    pathToResults = currentPath +"/results/"
    insertBlob.insertingAllResults(file_name, pathToResults)
    return True
