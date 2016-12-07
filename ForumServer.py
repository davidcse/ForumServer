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

def get_post_id_content(groupName,post_id):
    try:
        postContent = database[groupName][post_id]
        return postContent
    except:
        print("Error getting specific post content from " + str(post_id) + " in group " + str(groupName))


def set_post(groupName,post_id,post):
    database[groupName][post_id]= post
    

#------------------------#
#   SERVER PROCEDURES    #
#------------------------#

# fulfills a request for group id's within the server database, for a given range of indexes. 
# @client : obj, client socket
# @rangeStart : int , start of the post range
# @rangeEnd : int , end of the post range 
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


# fulfills a request for post id's within a group to the client. 
# @client : obj, client socket
# @groupName : str, name of the group
# @start : int , start of the post range
# @end : int , end of the post range 
def fulfill_postrange_request(client,groupName,start,end):
    posts = get_posts(groupName)
    response_postarray = posts[(start-1):end]
    strBuffer = StringIO()
    json.dump(response_postarray,strBuffer)
    if(verbose): print("Preparing to send GETPOSTRANGE response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue())


# fulfills a group items request for the client. 
# @client : obj, client socket
# @group_dictionary: dictionary, where key is groupname and value is all the posts in the group, including post content. 
def fulfill_group_items_request(client, group_dictionary):
    strBuffer = StringIO()
    json.dump(group_dictionary,strBuffer)
    if(verbose): print("Preparing to send SG response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue())


# fulfills a getpost request for the client. 
# @client : obj, client socket
# @post_identifiers : list , list[0] = group that post belongs to, list[1] = post id
def fulfill_post_id_request(client,groupName,postId):
    strBuffer = StringIO()
    content = get_post_id_content(groupName,postId)
    if(content == None):
        return
    resp = {postId : content}
    json.dump(resp,strBuffer)
    if(verbose): print("Preparing to send SG response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue())
            

    
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


def perform_protocol_group_items(contentHeaders):
    # extract the groups for which post items are requested.
    try:
        jso = json.loads(contentHeaders)
        if(verbose) : print(jso)
        requested_groups_array = jso["GROUPS"]
    except:
        print("client did not send a valid contentHeader for requested groups : " + str(contentHeaders))
        return
    # create mapping of the group and the items it contains
    responseDict = {}
    try:
        for g in requested_groups_array:
            responseDict[g] = database[g]
        return responseDict
    except Exception as error:
        print("Client requested a set of group that does not exist on server")
    return


def perform_protocol_postrange(contentHeaders):
    reponseArray = []
    try:
        jso = json.loads(contentHeaders)
        if(verbose) : print(jso)
        parentGroup = jso["GROUPID"]
        s = int(jso["START"])
        e = int(jso["END"])
        responseArray[parentGroup,s,e]
        return responseArray
    except:
        print("client did not send a valid contentHeader for requested groups : " + str(contentHeaders))
        return

            
def perform_protocol_postid(contentHeaders):
    identifiers = []
    try:
        jso = json.loads(contentHeaders)
        if(verbose) : print(jso)
        identifiers.append(jso["GROUPID"])
        identifiers.append(jso["POSTID"])
        return identifiers
    except:
        print("client did not send a valid contentHeader for a request for post : " + str(contentHeaders))
    return 

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
    try:
        # Typically fork at this point

        # Receive up to 1024 bytes 
        resp = (connect.recv(1024)).strip()
        if(verbose): print("received message : " + str(resp) + " from : " + str(address))
        
        # separate the type of protocol from the contentHeaders
        clientRequest = resp.split(":",1)
        
        # Check against list of known protocols, to fulfill the request.
        if(clientRequest[0]=="GETGROUPRANGE"):
            group_ranges = perform_protocol_grouprange(clientRequest[1])
            if(group_ranges != None):
                fulfill_grouprange_request(connect, group_ranges[0],group_ranges[1])
        elif(clientRequest[0]=="GETPOSTRANGE"):
            post_id_params = perform_protocol_postrange(clientRequest[1])
            if(post_id_params != None):
                fulfill_postrange_request(connect,post_id_params[0],post_id_params[1],post_id_params[2])
        elif(clientRequest[0]=="GETGROUPITEMS"):
            group_dictionary = perform_protocol_group_items(clientRequest[1])
            if(group_dictionary != None):
                fulfill_group_items_request(connect,group_dictionary)
        elif(client_Request[0] =="GETPOSTID"):
            post_id_params = perform_protocol_postid(clientRequest[1])
            if(post_id_params  != None):
                fulfill_post_id_request(connect,post_id_params[0],post_id_params[1])
        else:
            # client violated protocol in some way.                        
            print("client did not send a valid protocol matched to a request")

        #send acknowledgement that data transfer is finished. 
        connect.send("FIN")           
        if(verbose): print("\n Finished request: " + str(resp) +" from " + str(address))
        
    # Issue with connected client socket.
    except:
        print("Server encountered client not available, closing connection...")
        connect.close()
        break

#close the server
s.close()
