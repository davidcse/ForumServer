import socket
import json
from StringIO import StringIO 

#----------------------#
#   GLOBAL DATA        #
#----------------------#
server = ""
port = 1200

# Filepath to the json-formatted text file
DATABASE_FILE_ADDR = "./Data/ServerDataFile.txt"

#sample Data
sampleData1 = {
        'comp.programming': {
                "programming post 1":{
                        "author1":"paul",
                        "subject":"Sort a Python dictionary by value",
                        "body":"The very first sentence"
                    },
                "programming post 2":{
                        "author1":"Seth",
                        "subject":"How to print to stderr in Python 2.7?",
                        "body":"The very second sentence"
                    },
                "programming post 3":{
                        "author1":"Bob",
                        "subject":"How to print to stderr in Python 3.4?",
                        "body":"The very second sentence"
                    }
                
            },
        'comp.os.threads': {
                "threads post 1":{
                        "author1":"George",
                        "subject":"multithreading",
                        "body":"use p_threads"
                    },
                "threads post 2":{
                        "author1":"Manuel",
                        "subject":"semaphores",
                        "body":"Has p() and v()"
                    },
                "threads post 3":{
                        "author1":"Robert",
                        "subject":"mutex",
                        "body":"mutex lock down"
                    },
                "threads post 4":{
                        "author1":"Wilson",
                        "subject":"multiprocessors",
                        "body":"spin locks"
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
        return targetGroup
    except:
        print("Error getting posts for group : " + str(groupName) + ", could not find in database")
        return None

#------------------------#
#   SERVER PROCEDURES    #
#------------------------#

def fulfill_grouprange_request(client,rangeStart, rangeEnd):
    groups = get_all_groups()
    if(verbose) : print("all groups on server " + str(groups))
    range_groups = []
    for i in range(rangeStart-1,rangeEnd):
        try:
            g = groups[i]
            print("range " + str(i) + ' is ' + str(g))
            range_groups.append(g)
        except:
            break
    strBuffer = StringIO()
    json.dump(range_groups,strBuffer)
    if(verbose): print("Preparing to send grouprange response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue())

def fulfill_grouparray_request(client, group_dictionary):
    strBuffer = StringIO()
    json.dump(group_dictionary,strBuffer)
    if(verbose): print("Preparing to send SG response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue())


def fulfill_AG_request(client):
    groups = get_all_groups()
    strBuffer = StringIO()
    json.dump(groups,strBuffer)
    if(verbose): print("Preparing to send AG response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue())

def fulfill_SG_request(client):
    groups = database
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

#-------------------#
#   PROTOCOLS       #
#-------------------#
# gets groups from the server app data, within a certain range. 
def perform_protocol_grouprange(contentHeaders):
    try:
        contentJso = json.loads(contentHeaders)
        start = int(contentJso['START'])
        end = int(contentJso['END'])
        if(verbose): print("grouprange for client request is [" +str(start) + "," + str(end) + "]")
        return [start,end]
    except:
        if(verbose): print("error trying to extract group ranges")
    return 


def perform_protocol_grouparray(contentHeaders):
    try:
        jso = json.loads(contentHeaders)
        print(jso)
        requestArray = jso["GROUPS"]
    except:
        print("client did not send a valid contentHeader for requested groups : " + str(contentHeaders))
        return
    # created request array, so fulfill the request. 
    responseDict = {}
    try:
        for i in requestArray:
            responseDict[i] = database[i]
    except KeyError:
        print("Client requested a group that does not exist on server")
    return responseDict
            
                        
                        

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
        # Check against list of protocols, to fulfill the request. 
        else:
            clientRequest = resp.split(":",1)
            if(clientRequest[0]=="GETGROUPRANGE"):
                group_ranges = perform_protocol_grouprange(clientRequest[1])
                fulfill_grouprange_request(connect, group_ranges[0],group_ranges[1])
            elif(clientRequest[0]=="GETGROUPARRAY"):
                group_dictionary = perform_protocol_grouparray(clientRequest[1])
                fulfill_grouparray_request(connect,group_dictionary)
            else:
               print("client did not send a valid protocol matched to a request")

        # Send an answer
        connect.send("FIN")

        # And there could be a lot more here!

        if(verbose): print("\n Finished request: " + str(resp) +" from " + str(address))
        # And loop for / wait for another client

#close the server
s.close()
