import socket
import json
from StringIO import StringIO 

#----------------------#
#   GLOBAL DATA        #
#----------------------#
server = ""
port = 1200

# Filepath to the json-formatted text file
DATABASE_FILE_ADDR = "ServerDataFile.txt"

#sample Data
sampleData1 = {
        'comp.programming': {
                "post1":{
                        "author1":"paul",
                        "subject":"Sort a Python dictionary by value",
                        "body":"The very first sentence"
                    },
                "post2":{
                        "author1":"Seth",
                        "subject":"How to print to stderr in Python?",
                        "body":"The very second sentence"
                    }
            },
        'comp.os.threads': {
                "post1":{
                        "author1":"paul",
                        "subject":"firstpost",
                        "body":"The very first sentence"
                    }
            }
    }

#application data
database = {}
# debug logging toggle variable
verbose = 1

#------------------------#
#   GET / SET DATA(BASE) #
#------------------------#
def get_all_groups():
    groupList = []
    for key,value in database.items():
        groupList.append(key)
    return groupList

def get_posts(groupName):
    try:
        targetGroup = database[groupName]
        postList = []
        for key,value in targetGroup.items():
            postList.append(key)
        return postList
    except:
        print("Error getting posts for group : " + str(groupName) + ", could not find in database")
        return None

#------------------------#
#   SERVER PROCEDURES    #
#------------------------#

def fulfill_AG_request(client):
    groups = get_all_groups()
    strBuffer = StringIO()
    json.dump(groups,strBuffer)
    if(verbose): print("Preparing to send AG response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue())

def fulfill_SG_request(client):
    groups = get_all_groups()
    strBuffer = StringIO()
    json.dump(groups,strBuffer)
    if(verbose): print("Preparing to send SG response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue())

def fulfill_RG_request(client,groupName):
    posts = get_posts(groupName)
    strBuffer = StringIO()
    json.dump(posts,strBuffer)
    if(verbose): print("Preparing to send RG response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue())

def execute_default(client):
    client.send("procedure not found")
    print("client requested a non-existent procedure")

    

#Dictionary of procedure functions, which must be defined above. 
procedures={
        'AG:' : fulfill_AG_request,
        'SG:' : fulfill_SG_request,
        'RG:' : fulfill_RG_request
    }
#Get server's procedure method to handle client request
def getProcedure(procedure_key):
    found_request = procedures.get(procedure_key,execute_default)
    return found_request


#----------------------#
#  DATA MANAGEMENT     #
#----------------------#

#reads a json text file, parses into a python dict
def load_json_data(filePath):
    file = open(filePath, 'r')
    raw_data = file.read()
    jso = json.loads(raw_data)
    file.close()
    if(verbose):
        print(jso)
    return jso

# stores json data, writing it to text file at the filePath
def store_json_data(filePath,data):
    #dump data into the buffer
    streamBuffer = StringIO()
    json.dump(data, streamBuffer)
    # write buffer to file
    saveFile = open(filePath,"w")
    saveFile.write(streamBuffer.getvalue())
    saveFile.close()


def init_database_object():
    global database
    global sampleData1
    #Try loading data file, else create one with sample data and load it.
    try:
        database = load_json_data(DATABASE_FILE_ADDR)
    except:
        store_json_data(DATABASE_FILE_ADDR,sampleData1)
        database = load_json_data(DATABASE_FILE_ADDR)
        if(verbose):
            print("SAMPLEDATA1: ")
            print(sampleData1)
            print("Database:")
            print(database)


#--------------------#
#   SCRIPT           #
#--------------------#

# set up server application data from data file
init_database_object()
# Establish a TCP/IP socket
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
if(verbose): print('Initialized Socket')
# Bind to TCP port 
s.bind((server,port))
if(verbose): print('Server binded at : ' + str(port))
# ... and listen for anyone to contact you
# queueing up to five requests if you get a backlog
s.listen(5)
if(verbose): print('server is listening')


# Wait for a connection
connect, address = s.accept()
while True:
  #      # Wait for a connection
  #      connect, address = s.accept()
        # Typically fork at this point

        # Receive up to 1024 bytes
        resp = (connect.recv(1024)).strip()
        if(verbose): print("received message : " + str(resp) + " from : " + str(address))
        # If the connection is lost
        if(resp == ""):
            connect.close()
        # And if the user has sent a "SHUTDOWN" instruction
        elif(resp=="SHUTDOWN"):
            break
        else:
            requested_procedure = getProcedure(resp)
            requested_procedure(connect)

        # Send an answer
        connect.send("FIN")

        # And there could be a lot more here!

        if(verbose): print("\n Finished request: " + str(resp) +" from " + str(address))
        # And loop for / wait for another client

#close the server
s.close()
