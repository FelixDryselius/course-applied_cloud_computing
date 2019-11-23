#!flask/bin/python
from flask import Flask
#from tinydb import TinyDB, Query
#import subprocess
#import os
#import sys
import readBlob
import time
from tasks import airfoil_calc

app = Flask(__name__)

#START test data and methods
#db = TinyDB('db.json')
xml_files = ['r2a0n200.xml', 'r3a3n200.xml', 'r1a9n200.xml', 'r0a6n200.xml', 'r3a9n200.xml', 'r3a15n200.xml', 'r3a24n200.xml', 'r1a24n200.xml', 'r2a9n200.xml', 'r2a12n200.xml', 'r3a12n200.xml', 'r2a30n200.xml', 'r2a15n200.xml', 'r1a27n200.xml', 'r0a12n200.xml', 'r0a0n200.xml', 'r3a18n200.xml', 'r1a15n200.xml', 'r0a21n200.xml', 'r1a12n200.xml', 'r2a18n200.xml', 'r2a3n200.xml', 'r3a6n200.xml', 'r1a30n200.xml', 'r0a27n200.xml', 'r2a24n200.xml', 'r1a18n200.xml', 'r3a30n200.xml', 'r2a6n200.xml', 'r3a0n200.xml', 'r2a27n200.xml', 'r0a15n200.xml', 'r0a18n200.xml', 'r0a9n200.xml', 'r0a30n200.xml', 'r1a6n200.xml', 'r0a24n200.xml', 'r3a27n200.xml', 'r1a0n200.xml', 'r3a21n200.xml', 'r2a21n200.xml', 'r1a3n200.xml', 'r1a21n200.xml', 'r0a3n200.xml']
xml_files.sort()

#@app.route('/test', methods=['GET'])
#def airfoil():
#    airfoilDB = Query()
#    final_result = {}
#    for xml_file in xml_files[0:5]:
#        dbResponse = db.search(airfoilDB.filename == xml_file)
#        if (not dbResponse):
#            data = airfoil_calc.delay(xml_file)
#            result = data.get()
#            record = {'filename': xml_file, 'result': result}
#            db.insert(record)
#            final_result[xml_file] = result
#        else:
#            final_result[xml_file] = dbResponse[0]['result']
#    return final_result

#END test data and methods


@app.route('/exact_call/<level>/<angle>/<node>/', methods=['GET'])  
def exact_call(level,angle,node):
    filename = "r{}a{}n{}.xml".format(level,angle,node)
    
    if not readBlob.check_if_result_exists(filename):
        airfoil_calc.delay(filename)
    
    error_message = ""    
    t = 0
    while not readBlob.check_if_result_exists(filename):
        time.sleep(1)
        t += 1
        if t > 1000:
            error_message = filename+' failed to be calculated within 1000s. '
            break

    if len(error_message == 0):
        error_message = "Succeeded!"

    return error_message+"The result is calculated, contact admin to download."
    
#    return fullFileName 



@app.route('/range_call/<level>/<first_angle>/<last_angle>/<node>/', methods=['GET'])  
def range_call(level,first_angle,last_angle,node):

    firstFullFileName = "r{}a{}n{}.xml".format(level,first_angle,node)
    lastFullFileName = "r{}a{}n{}.xml".format(level,last_angle,node)
    
    firstIndex = xml_files.index(firstFullFileName)
    lastIndex = xml_files.index(lastFullFileName) 

    filesToCalc = xml_files[firstIndex:(lastIndex+1)]

    for fullFileName in filesToCalc:            
        if not readBlob.check_if_result_exists(fullFileName):
            airfoil_calc.delay(fullFileName)
    
    print("The result is calculated, contact admin to download.")

    return filesToCalc

@app.route('/parameter/<first_angle>/<last_angle>/<ndiv>/<nodes>/<level>', methods=['GET'])
def user_defined_call(first_angle,last_angle,ndiv,nodes,level):
    filenames = []
    first_angle = int(first_angle)
    last_angle = int(last_angle)
    ndiv = int(ndiv)
    nodes = int(nodes)
    level = int(level)
    step = int((last_angle-first_angle)/ndiv)
    for l in range(level+1):
        for a in range(first_angle,last_angle+step,step):
            filenames.append("r{}a{}n{}.xml".format(l,a,nodes))

    for filename in filenames:
        if not readBlob.check_if_result_exists(filename):
            airfoil_calc.delay(filename)
    
    error_message = ""
    
    for filename in filenames:
        t = 0
        while not readBlob.check_if_result_exists(filename):
            time.sleep(1)
            t += 1
            if t > 1000:
                error_message += filename+' failed to be calculated within 1000s. '
                break

    if len(error_message) == 0:
        error_message = "Succeeded!"

    return error_message + " The result is calculated, contact admin to download."



if __name__ == '__main__':
    
    app.run(host='0.0.0.0',debug=True)
