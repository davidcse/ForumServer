import socket
import json
import traceback
import threading
import logging
import time
import collections
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

#----------------------#
#   GLOBAL DATA        #
#----------------------#
server = ""
port = 60000

# Filepath to the json-formatted text file
DATABASE_FILE_ADDR = "./ServerDataFile.txt"

# LOCKS
global dbLock
global fileLock
dbLock = threading.RLock()
fileLock = threading.RLock()

#sample Data
sampleData1 = {
        'comp.programming': {
                "programming post 1":{
                        "Group" : "comp.programming",
                        "Author":"paul",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"Sort a Python dictionary by value",
                        "Body":"The very first sentence"
                    },
                "programming post 2":{
                        "Group" : "comp.programming",
                        "Author":"Seth",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"How to print to stderr in Python 2.7?",
                        "Body":"The very second sentence"
                    },
                "programming post 3":{
                        "Group" : "comp.programming",
                        "Author":"Bob",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"How to print to stderr in Python 3.4?",
                        "Body":"The very second sentence"
                    }
                
            },
        'comp.os.threads': {
                "threads post 1":{
                        "Group" : "comp.os.threads",
                        "Author":"George",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"multithreading",
                        "Body":"use p_threads"
                    },
                "threads post 2":{
                        "Group" : "comp.os.threads",
                        "Author":"Manuel",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"semaphores",
                        "Body":"Has p() and v()"
                    },
                "threads post 3":{
                        "Group" : "comp.os.threads",
                        "Author":"Robert",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"mutex",
                        "Body":"mutex lock down"
                    },
                "threads post 4":{
                        "Group" : "comp.os.threads",
                        "Author":"Wilson",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"multiprocessors",
                        "Body":"spin locks"
                    },
                "threads post 5":{
                        "Group" : "comp.os.threads",
                        "Author":"David",
                        "Date": "12/6/2017 3:10P",
                        "Subject":"multiprocessors and cores",
                        "Body":"For multiple processors, it is different.\n You have to take into consideration the many cores.\nTake a look at the architecture of the running program.\nThen in code use spinlock.\nThis is the right way to do things.\nThe performance should be better.\nThe end."
                    }
            },
        'comp.lang.python':{
                'python post 1':{
                        "Group" : "comp.lang.python",
                        "Author":"Vinny",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"learn python ",
                        "Body":"python is the best"
                    },
				'python post 2':{
                        "Group" : "comp.lang.python",
                        "Author":"Paul",
                        "Date": "12/6/2017 3:15P",
                        "Subject":"learn python advanced ",
                        "Body":"python can be very advanced"
                    },
				'python post 3':{
                        "Group" : "comp.lang.python",
                        "Author":"Bradly",
                        "Date": "12/6/2017 3:15P",
                        "Subject":"I think I just broke my python ",
                        "Body":"I think I broke it guys.I can't find my compiler. Any advice?"
                    }	
					
            },
        'comp.lang.java':{
                    'java post 1':{
                        "Group" : "comp.lang.java",
                        "Author":"Vinny",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"learn java ",
                        "Body":"java is the best"
                    },
					'java post 2':{
                        "Group" : "comp.lang.java",
                        "Author":"Shaun",
                        "Date": "12/6/2017 3:14P",
                        "Subject":"The truth about java and why it is king! ",
                        "Body":"java is the best thats is my entire argument gg"
                    },
					'java post 3':{
                        "Group" : "comp.lang.java",
                        "Author":"Shaun",
                        "Date": "12/6/2017 3:05P",
                        "Subject":"Java enums ",
                        "Body":"I forgot what I was taught in 219! Can someone explain enums again and what is lmgtfy?"
                    }
            },
        'comp.lang.c':{
                    'c post 1':{
                        "Group" : "comp.lang.c",
                        "Author":"Robert",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"learn C ",
                        "Body":"C is the best"
                    },
					'c post 2':{
                        "Group" : "comp.lang.c",
                        "Author":"King",
                        "Date": "12/6/2017 3:01P",
                        "Subject":"Learn how to sort in c",
                        "Body":"1 2 3 4 5 "
                    },
					'c post 3':{
                        "Group" : "comp.lang.c",
                        "Author":"Patsy",
                        "Date": "12/6/2017 3:04P",
                        "Subject":"My company says I'm to blame!",
                        "Body":"I am not a patsy like that! I git pushed! I swear!"
                    }
            },
        'comp.lang.javascript':{
                    'javascript post 1':{
                        "Group" : "comp.lang.javascript",
                        "Author":"Robert",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"learn Javascript ",
                        "Body":"Javascript is the best"
                    },
					'javascript post 2':{
                        "Group" : "comp.lang.javascript",
                        "Author":"Jimmy",
                        "Date": "12/6/2017 3:01P",
                        "Subject":"learn Javascript lesson 2",
                        "Body":"Javascript is the best round 2"
                    },
					'javascript post 3':{
                        "Group" : "comp.lang.javascript",
                        "Author":"Jimmy, but Slim",
                        "Date": "12/8/2017 3:02P",
                        "Subject":"learn Javascript lesson 3",
                        "Body":"Javascript is the best round 3"
                    }
            },
        'comp.lang.prolog':{
                'prolog post 1':{
                        "Group" : "comp.lang.prolog",
                        "Author":"Robert",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"learn Javascript ",
                        "Body":"Javascript is the best"
                },
				'prolog post 2':{
                        "Group" : "comp.lang.prolog",
                        "Author":"Rob, but Angry",
                        "Date": "12/7/2017 3:00P",
                        "Subject":"learn Javascript 2",
                        "Body":"Javascript is pretty good"
                },
				'prolog post 3':{
                        "Group" : "comp.lang.prolog",
                        "Author":"Fred",
                        "Date": "12/11/2017 3:00P",
                        "Subject":"learn Javascript 3",
                        "Body":"Javascript is the ultimate language"
                }
            },
        'comp.lang.sml':{
                'sml post 1':{
                        "Group" : "comp.lang.sml",
                        "Author":"Robert",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"learn sml ",
                        "Body":"sml is the best"
                },
				'sml post 2':{
                        "Group" : "comp.lang.sml",
                        "Author":"Timmy",
                        "Date": "12/6/2017 3:30P",
                        "Subject":"learn sml 2",
                        "Body":"sml is the best and I have 2 feet"
                },
				'sml post 3':{
                        "Group" : "comp.lang.sml",
                        "Author":"Dale Dimmadome",
                        "Date": "12/6/2017 3:50P",
                        "Subject":"learn sml 3",
                        "Body":"sml is the best. Thank you for attending lesson 3"
                }
            },
        'comp.lang.ruby':{
                'ruby post 1':{
                        "Group" : "comp.lang.ruby",
                        "Author":"Sam",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"learn Ruby from a veteran!",
                        "Body":"Rubys are worth more than sapphires"
                },
				'ruby post 2':{
                        "Group" : "comp.lang.ruby",
                        "Author":"Robby",
                        "Date": "12/6/2017 3:30P",
                        "Subject":"learn ruby ",
                        "Body":"ruby is the best"
                },
				'ruby post 3':{
                        "Group" : "comp.lang.ruby",
                        "Author":"Marky Mark AKA Dean",
                        "Date": "12/11/2017 3:00P",
                        "Subject":"learn ruby ",
                        "Body":"Dean says Sarah likes him more than Ruby"
                }
            },
        'comp.framework.angularjs':{
                'ruby post 1':{
                        "Group" : "comp.framework.angularjs",
                        "Author":"Andrew Denn",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"learn angularjs ",
                        "Body":"angularjs is the best"
                },
				'ruby post 2':{
                        "Group" : "comp.framework.angularjs",
                        "Author":"TennisBoi69",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"learn angular from a cube himself",
                        "Body":"I have 6 faces. People say I'm bipolar."
                },
				'ruby post 3':{
                        "Group" : "comp.framework.angularjs",
                        "Author":"R.O.B.",
                        "Date": "12/6/2017 3:00P",
                        "Subject":"learn angularjs 3",
                        "Body":"i'm tired of angles."
                }
            },
        'comp.framework.jquery':{
                'jquery post 1':{
                        "Group" : "comp.framework.jquery",
                        "Author":"DaveGotMoney",
                        "Date": "12/6/2017 3:40P",
                        "Subject":"JQUERY how to query101",
                        "Body":"101 101 101 101 Error 200"
                    },
				'jquery post 2':{
                        "Group" : "comp.framework.jquery",
                        "Author":"Robert",
                        "Date": "12/6/2017 3:55P",
                        "Subject":"learn jquery from a beginner",
                        "Body":"I know nothing ask Dave."
                    },
				'jquery post 3':{
                        "Group" : "comp.framework.jquery",
                        "Author":"Vincent",
                        "Date": "12/10/2017 3:00P",
                        "Subject":"I couldn't learn from Rob!",
                        "Body":"I guess I shoulda asked Dave? Right ;("
                    }
            },
			'comp.framework.REXX':{
                'REXX post 1':{
                        "Group" : "comp.framework.REXX",
                        "Author":"MoneyMitch",
                        "Date": "12/6/2017 3:40P",
                        "Subject":"who IS Rex?",
                        "Body":"A T-Rex has small hands"
                    },
				'REXX post 2':{
                        "Group" : "comp.framework.REXX",
                        "Author":"BobDaniels",
                        "Date": "12/15/2017 3:55P",
                        "Subject":"REXX",
                        "Body":"My friend's dad codes in REXX. I know a guy you could say."
                    },
				'REXX post 3':{
                        "Group" : "comp.framework.REXX",
                        "Author":"Rad Raphael55",
                        "Date": "12/10/2017 3:24P",
                        "Subject":"Problems with grammar",
                        "Body":"Where are the MANPAGES? Where is my family? Why has everyone abandonded me?"
                    }
            },
			'comp.Ubuntu':{
                'Ubuntu post 1':{
                        "Group" : "comp.Ubuntu",
                        "Author":"Ubuntu god",
                        "Date": "12/6/2017 3:44P",
                        "Subject":"INTRO TO UBUNTU",
                        "Body":"First download your ubuntu please. Hands up."
                    },
				'Ubuntu post 2':{
                        "Group" : "comp.Ubuntu",
                        "Author":"BobbyD",
                        "Date": "12/1/2017 3:55P",
                        "Subject":"Ubuntu",
                        "Body":"ubuntu is the best hands down. I have no arms"
                    },
				'Ubuntu post 3':{
                        "Group" : "comp.Ubuntu",
                        "Author":"SilverSurfer",
                        "Date": "12/10/2017 3:24P",
                        "Subject":"What is the best version?",
                        "Body":"I just have the version that JWONG told me to install. Any preferences?"
                    }
            },
			'comp.General':{
                'General post 1':{
                        "Group" : "comp.General",
                        "Author":"Charlie",
                        "Date": "12/6/2017 3:44P",
                        "Subject":"General question",
                        "Body":"Generally speaking, why do computer use bits?"
                    },
				'General post 2':{
                        "Group" : "comp.General",
                        "Author":"Dennis",
                        "Date": "12/1/2017 3:55P",
                        "Subject":"What does a computer cost? Am I using a computer right now?",
                        "Body":"I have steadily lost control of my life. This is a memory."
                    },
				'General post 3':{
                        "Group" : "comp.General",
                        "Author":"SunGod",
                        "Date": "12/10/2017 3:24P",
                        "Subject":"What is a power supply?",
                        "Body":"I just have the version that JWONG told me to install. Any preferences?"
                    }
            },
			'comp.Parrot':{
                'Parrot post 1':{
                        "Group" : "comp.Parrot",
                        "Author":"A bird",
                        "Date": "12/1/2017 3:00P",
                        "Subject":"learn parrot",
                        "Body":"parrot is the best"
                    },
				'Parrot post 2':{
                        "Group" : "comp.Parrot",
                        "Author":"A red bird",
                        "Date": "12/2/2017 3:01P",
                        "Subject":"learn parrot2",
                        "Body":"Just a brief lesson 2 on parrot. This is a language lol."
                    },
				'Parrot post 3':{
                        "Group" : "comp.Parrot",
                        "Author":"Bird lover",
                        "Date": "12/3/2017 3:46P",
                        "Subject":"learn parrot3",
                        "Body":"This has been lesson 3. Thank you. Goodnight my fans!"
                    }
            }
    }

#application data
database = collections.OrderedDict()
# debug logging toggle variable
verbose = 0

#------------------------#
#   GET / SET DATA(BASE) #
#------------------------#

def send_end_protocol(client):
    fin = "\n.\n"
    client.send(fin.encode())

# returns an array of groupnames on this database
def get_all_groups():
    groupList = []
    dbLock.acquire()
    for key,value in database.items():
        groupList.append(key)
    dbLock.release()
    return groupList

# returns the entire dictionary of post contents for the group on this database
def get_posts(groupName):
    try:
        targerGroup = None
        dbLock.acquire()
        targetGroup = database[groupName]
    except:
        print("Error getting posts for group : " + str(groupName) + ", could not find in database")
    finally:
        dbLock.release()
        return targetGroup

# returns the names of the posts only, from this parent group. 
def get_posts_name_date(groupName):
    try:
        targerGroup = None
        dbLock.acquire()
        targetGroup = database[groupName]
        dbLock.release()
        post_keys = list(targetGroup)
        post_name_date = {}
        for i in post_keys:
            post_name_date[i] = {"Date":targetGroup[i]["Date"], "Subject":targetGroup[i]["Subject"]}
        return post_name_date
    except:
        if verbose: print("Error getting posts for group : " + str(groupName) + ", could not find in database")
        dbLock.release()
        return None

# returns the contents of the specific post under the given group. 
def get_post_id_content(groupName,post_id):
    try:
        dbLock.acquire()
        postContent = database[groupName][post_id]
        dbLock.release()
        return postContent
    except:
        if verbose: print("Error getting specific post content from " + str(post_id) + " in group " + str(groupName))
        dbLock.release()

# modifies the contents of the post on the server
def set_post(groupName,post_id,post):
    dbLock.acquire()
    database[groupName][post_id]= post
    dbLock.release()
    

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
            if verbose: print("range " + str(i) + ' is ' + str(g))
            range_groups.append(g)
        except:
            break
    strBuffer = StringIO()
    json.dump(range_groups,strBuffer, indent=4, sort_keys=True)
    if(verbose): print("Preparing to send grouprange response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue().encode())


# fulfills a request for post id's within a group to the client. 
# @client : obj, client socket
# @groupName : str, name of the group
# @start : int , start of the post range
# @end : int , end of the post range 
def fulfill_postrange_request(client,groupName,start,end):
    posts = get_posts_name_date(groupName)
    if posts == None:
        strBuff = StringIO()
        resp = ["NOGRP"]
        json.dump(resp,strBuff, indent=4, sort_keys=True)
        client.send(strBuff.getvalue().encode())
        return
    if verbose: print(posts)
    post_list = list(posts)[start-1:end]
    post_date_dict = {}
    for i in post_list:
        post_date_dict[i] = posts[i]
    strBuffer = StringIO()
    json.dump(post_date_dict,strBuffer, indent=4, sort_keys=True)
    if(verbose): print("Preparing to send GETPOSTRANGE response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue().encode())
    


# fulfills a group items request for the client. 
# @client : obj, client socket
# @group_dictionary: dictionary, where key is groupname and value is all the posts in the group, including post content. 
def fulfill_group_items_request(client, group_dictionary):
    strBuffer = StringIO()
    json.dump(group_dictionary,strBuffer, indent=4, sort_keys=True)
    if(verbose): print("Preparing to send SG response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue().encode())


# fulfills a getpost request for the client. 
# @client : obj, client socket
# @post_identifiers : list , list[0] = group that post belongs to, list[1] = post id
def fulfill_post_id_request(client,groupName,postId):
    strBuffer = StringIO()
    content = get_post_id_content(groupName,postId)
    if verbose : print("post id content " + str(content))
    if(content == None):
        return
    resp = {postId : content}
    json.dump(resp,strBuffer, indent=4, sort_keys=True)
    if(verbose): print("Preparing to send SG response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue().encode())
            
def fulfill_setpost_id_request(client,postData):
    uniqueTime = time.strftime("%c")
    group = postData["GROUP"]
    dbLock.acquire()
    postId = uniqueTime+"_"+str(len(list(database[group])))
    dbLock.release()
    # build content
    content = {
        "Group" : group,
        "Author": postData["AUTHOR"],
        "Date": uniqueTime,
        "Subject": postData["SUBJECT"],
        "Body":postData["BODY"]
    }
    set_post(group,postId,content)
    # tell the client confirmation 
    strBuffer = StringIO()
    resp = ["CREATE_POST_SUCCESSFUL"]
    json.dump(resp,strBuffer, indent=4, sort_keys=True)
    if(verbose): print("Preparing to send SG response: " + strBuffer.getvalue())
    client.send(strBuffer.getvalue().encode())

#----------------------#
#  DATA MANAGEMENT     #
#----------------------#

#reads a json text file, parses into a python dict
def load_json_data(filePath):
    file = open(filePath, 'r')
    raw_data = file.read()
    jso = json.loads(raw_data)
    file.close()
    if(verbose): print(jso)
    return jso

# stores json data, writing it to text file at the filePath
def store_json_data(filePath,data):
    #dump data into the buffer
    streamBuffer = StringIO()
    json.dump(data, streamBuffer, indent=4, sort_keys=True)
    # write buffer to file
    saveFile = open(filePath,"w")
    saveFile.write(streamBuffer.getvalue())
    saveFile.close()

    
def save_file():
    dbLock.acquire()
    store_json_data(DATABASE_FILE_ADDR,database)
    dbLock.release()
    
def init_database_object():
    global database
    global sampleData1
    #Try loading data file, else create one with sample data and load it.
    try:
        dbLock.acquire()
        tempDict = load_json_data(DATABASE_FILE_ADDR)
        for i in tempDict:
            database[i] = tempDict[i]
    except:
        store_json_data(DATABASE_FILE_ADDR,sampleData1)
        tempDict = load_json_data(DATABASE_FILE_ADDR)
        for i in tempDict:
            database[i] = tempDict[i]
        if(verbose):
            print("SAMPLEDATA1: ")
            print(sampleData1)
            print("Database:")
            print(database)
    finally:
        dbLock.release()

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


def perform_protocol_postrange(contentHeaders):
    reponseArray = []
    try:
        jso = json.loads(contentHeaders)
        if(verbose) : print(jso)
        parentGroup = jso["GROUPID"]
        s = int(jso["START"])
        e = int(jso["END"])
        responseArray = [parentGroup,s,e]
        return responseArray
    except:
        if verbose: print("client did not send a valid contentHeader for requested groups : " + str(contentHeaders))
        return
    

def perform_protocol_group_items(contentHeaders):
    # extract the groups for which post items are requested.
    try:
        jso = json.loads(contentHeaders)
        if(verbose) : print(jso)
        requested_groups_array = jso["GROUPS"]
    except:
        if verbose: print("client did not send a valid contentHeader for requested groups : " + str(contentHeaders))
        return
    # create mapping of the group and the items it contains
    responseDict = {}
    try:
        dbLock.acquire()
        for g in requested_groups_array:
            responseDict[g] = database[g]
        return responseDict
    except Exception as error:
        if verbose: print("Client requested a set of group that does not exist on server")
    finally:
        dbLock.release()
    return



            
def perform_protocol_postid(contentHeaders):
    identifiers = []
    if verbose : print("Evaluating protocol : " + str(contentHeaders))
    try:
        jso = json.loads(contentHeaders)
        if(verbose) : print(jso)
        identifiers.append(jso["GROUPID"])
        identifiers.append(jso["POSTID"])
        return identifiers
    except:
        if verbose: print("client did not send a valid contentHeader for a request for post : " + str(contentHeaders))
    return 

    
def perform_protocol_setpost_id(contentHeaders):
    if verbose : print("Evaluating protocol : " + str(contentHeaders))
    try: 
        jso = json.loads(contentHeaders)
        if(verbose): print(jso)
        return jso
    except Exception as err:
        if verbose: print("client did not send a valid contentHeader for a request for post : " + str(contentHeaders))
        if verbose: print("Error is : " + str(err))
    return 
 
# MAIN FUNCTION FOR THREADS
def handleClient(client, addr):
    client.settimeout(1)
    while True:
        try:
            # Receive up to 1024 bytes, and try to convert to string
            resp = client.recv(1024)
            resp = resp.decode()
            resp = str(resp)
            resp = resp.strip()
            if(verbose): print("received message : " + str(resp) + " from : " + str(addr))
        
            # separate the type of protocol from the contentHeaders
            clientRequest = resp.split(":",1)
        
            # Check against list of known protocols, to fulfill the request.
            if(clientRequest[0]=="GETGROUPRANGE"):
                group_ranges = perform_protocol_grouprange(clientRequest[1])
                if(group_ranges != None):
                    fulfill_grouprange_request(client, group_ranges[0],group_ranges[1])
            elif(clientRequest[0]=="GETPOSTRANGE"):
                post_id_params = perform_protocol_postrange(clientRequest[1])
                if(post_id_params != None):
                    fulfill_postrange_request(client,post_id_params[0],post_id_params[1],post_id_params[2])
            elif(clientRequest[0]=="GETGROUPITEMS"):
                group_dictionary = perform_protocol_group_items(clientRequest[1])
                if(group_dictionary != None):
                    fulfill_group_items_request(client,group_dictionary)
            elif(clientRequest[0] =="GETPOSTID"):
                post_id_params = perform_protocol_postid(clientRequest[1])
                if(post_id_params  != None):
                    fulfill_post_id_request(client,post_id_params[0],post_id_params[1])
            elif(clientRequest[0]=="SETPOSTID"):
                post_data = perform_protocol_setpost_id(clientRequest[1])
                if(post_data  != None):
                    fulfill_setpost_id_request(client,post_data)
                    save_file()
            else:
                # client violated protocol in some way.                        
                print("client did not send a valid protocol matched to a request")

            #send acknowledgement that data transfer is finished. 
            send_end_protocol(client)
            print("\n Finished request: " + str(resp) +" from " + str(addr))
        
        except socket.timeout:
            if verbose: print("timeout, continue to listen")

        # Issue with connected client socket.
        except Exception as error :
            if verbose: print("Server encountered error, or maybe client not available, closing connection... \n" + str(error))
            print("Closed client connection: " + str(addr))
            client.close()
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
for i in range(0,10,1):
    try: 
        s.bind((server,port))
        if(verbose): print('Server binded at : ' + str(port))
        break
    except OSError as bindingError:
        print(str(bindingError))
        port = port + 1
        print("Trying another socket : " + str(port))
    except socket.error as bindingError:
        print(str(bindingError))
        port = port + 1
        print("Trying another socket : " + str(port))


# listen for clients, queueing up to 10 requests for backlog
s.listen(10)
print('server is listening at port :'+ str(port))


# Wait for a connection
while True:
    connect, address = s.accept()
    # SPAWN NEW THREAD
    print("New client connected successfully: "+ str(address))
    t = threading.Thread(target=handleClient, args=(connect,address))
    t.start()
    

#close the server
s.close()
