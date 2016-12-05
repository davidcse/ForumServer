import socket
import json
from StringIO import StringIO
from os import path 

#--------------------#
#   GLOBAL DATA      #
#--------------------#
SERVER = "127.0.0.1"
PORT = 1200
CLIENT_DATA_ADDR = "./ForumClientData.txt"
DEFAULT_STEP = 5
verbose = 1

# dictionary storing user settings for the current client.
userData ={}
currentUserId = ""

# sample data file content if none previously exists.
sampleUserData = {
    '567':{
                'subscribed':['comp.programming','comp.os.threads'],
                'read':{
                        'comp.programming':['post1']
                    }
            }
    }

#key commands
LOGIN_COMMAND = "login_command"
POST_COMMAND = "post_command"
HELP_COMMAND = "help_command"

#-----------------------#
#   DATA MANAGEMENT     #
#-----------------------#

#reads a json text file, parses into a python dict
# @filePath : str, filepath containing json txt file
def load_json_data(filePath):
    file = open(filePath, 'r')
    raw_data = file.read()
    jso = json.loads(raw_data)
    file.close()
    if(verbose): print(jso)
    return jso


# stores json data, writing it to text file at the filePath
# @filePath : str, filepath containing json txt file
# @data: {} , dict obj. containing user data. 
def store_json_data(filePath,data):
    #dump data into the buffer
    streamBuffer = StringIO()
    json.dump(data, streamBuffer)
    # write buffer to file
    saveFile = open(filePath,"w")
    saveFile.write(streamBuffer.getvalue())
    saveFile.close()

# Attempts to load a json txt file for client data, else creates one with sample data
# @filePath : string , where to load and store from the data file. 
def startup_client_file_database(filePath):
    print("Checking default data file address : " + str(filePath))
    global userData
    if(path.exists(filePath)):
        print("Loaded user data at filepath : " + str(filePath))
    else:
        store_json_data(filePath,sampleUserData)
        print("Previous file does not exist at path : " + str(filePath))
        print("Sample user data written to path")

#tries to load client data on local machine, using the loaded data file.
#@param client_id : string , the client id to log on for. 
def login_client_id(client_id):
    global userData
    global currentUserId
    try:
        usersList = load_json_data(CLIENT_DATA_ADDR)
        userData = usersList[client_id]
        print("CLIENT " + str(client_id) + " LOGGED IN SUCCESSFULLY")
        currentUserId = client_id
        return True
    except:
        print("CLIENT LOGIN FAILED : " + str(client_id))
    return False

#------------------------------#
#       USER PREFERENCES       #
#------------------------------#
def get_subscriptions():
    return userData["subscribed"]

def get_read_posts(groupName):
    return userData["read"][groupName]

def mark_as_read(groupName,post):
    userData["read"][groupName].append(post)
    
def get_num_unread_posts(groupName, serverGroupObj):
    try:
        read_posts = get_read_posts(groupName)
    except KeyError:
        if(verbose): print("group : " + str(groupName) + " has no read posts, all is new.")
        read_posts = []
    num_unread = 0
    for i in serverGroupObj:
        if(i not in read_posts):
            num_unread = num_unread + 1
    return num_unread
    

            
                #------------------------------#
                #    CLIENT PROCEDURES         #
                #------------------------------#
                
# Attempts to store user preference data, and closes server socket before exiting.
# @param : server , server's socket
def perform_logout(server):
    print("Performing logging out user")
    global userData
    try:
        #update user preferences and store back into file
        database = load_json_data(CLIENT_DATA_ADDR)
        database[currentUserId] = userData
        store_json_data(CLIENT_DATA_ADDR,database)
    except:
        print("FAILED TO STORE USER DATA AT ADDRESS: " + str(CLIENT_DATA_ADDR))
    print("Closing connection with the server ")
    server.close()
    print("Session Terminated Successfully")



# Contacts server for discussions of a specific group
# @param : server , socket of server
# @param : groupName , the target group we want discussions for
# @param : numStep , number of discussion posts to display at a time. 
def perform_rg(server,groupName, numStep):
    server.send("RG:"+str(groupName))
    server_resp = start_polling(server)
    if(server_resp != None):
        rg_submenu_interface(server_resp,groupName)
    print("Finished executing rg : " + str(groupName))    


# Asks server to display all groups available.
# @param : server , socket of server
# @param : numStep , number of groups to display at a time. 
def perform_ag(server,numStep):
    server.send("AG:")
    response  = start_polling(server)
    if(verbose) : print("Finished executing ag.")
    if(response != None):
        ag_submenu_interface(response)
    print("Finished executing ag.")

# Performs subscription to group functions
# @param : server , socket of server
# @param : numStep , number of subscribed groups to display at a time. 
def perform_sg(server, numStep):
    server.send("SG:")
    response = start_polling(server)
    if(response != None):
        sg_submenu_interface(response)
    print("Finished executing sg.")
    

# Requests user for AG Submenu commands, and tries to execute it.
def ag_submenu_interface(response):
    formatted_AG_response(response)
    while True:
        print("\n\n***  AG - Submenu ****")
        user_input = raw_input("\n>>")
        args = trim_to_arg_array(user_input)
        breakStatus = perform_action_ag_submenu(args)
        if(breakStatus):
            break

# Requests user for SG Submenu commands, and tries to execute it.
def sg_submenu_interface(response):
    formatted_SG_response(response)
    while True:
        print("\n\n***  SG - Submenu ****")
        user_input = raw_input("\n>>")
        args = trim_to_arg_array(user_input)
        breakStatus = perform_action_sg_submenu(args)
        if(breakStatus): break

# Requests user for RG Submenu commands, and tries to execute it.
def rg_submenu_interface(response,groupName):
    formatted_RG_response(response,groupName)
    while True:
        print("\n\n***  RG - Submenu : " + str(groupName)+"****")
        user_input = raw_input("\n>>")
        args = trim_to_arg_array(user_input)
        breakStatus = perform_action_rg_submenu(args)
        if(breakStatus): break


# Formatted response for an AG request
def formatted_AG_response(response):
    subscribed_groups = get_subscriptions()
    for i in range(len(response)):
        sub_flag = " "
        if(response[i] in subscribed_groups):
            sub_flag = "S"
        format_line = str(i+1)+ ". (" +sub_flag + ") " + str(response[i])
        print(format_line)


# Formatted response for an SG request
def formatted_SG_response(response):
    subscribed_groups = get_subscriptions()
    matched_subscribed_group = []
    #build a list of groups that are common to both the server response and this user's subscription preference.
    for i in response:
        if i in subscribed_groups:
            matched_subscribed_group.append(i)
    # print the subscribed groups formatted way
    for i in range(len(matched_subscribed_group)):
        num_unread = get_num_unread_posts(matched_subscribed_group[i],response[matched_subscribed_group[i]])
        format_line = str(i+1)+ ". " +str(num_unread) + " " + str(matched_subscribed_group[i])
        print(format_line)

# Formatted response for an RG request
def formatted_RG_response(response, groupName):
    read_posts = get_read_posts(groupName)
    numCount = 1
    for i in response:
        newStatus = " "
        if i not in read_posts:
            newStatus = "N"
        format_line = str(numCount) + ". " +str(newStatus) + " " + str(i)
        numCount = numCount + 1
        print(format_line)
        

#fulfills client requested functions in the AG submenu
# @param args : list of str , contains user processed input.
def perform_action_ag_submenu(args):
    if len(args) ==0 :
        print("Error : nothing entered")
    elif args[0] == "s" :
        print("executing AG_s ...")
    elif args[0] == "u" :
        print("executing AG_u ...")
    elif args[0] == "n" :
        print("executing AG_n ...")
    elif args[0] == "q" :
        print("executing AG_q ...")
        return True
    else:
        print("invalid AG subcommand")
        command_AG_helpmenu()


#fulfills client requested functions in the SG submenu
# @param args : list of str , contains user processed input.
def perform_action_sg_submenu(args):
    if len(args) ==0 :
        print("Error : nothing entered")
    elif args[0] == "u" :
        print("executing SG_u ...")
    elif args[0] == "n" :
        print("executing SG_n ...")
    elif args[0] == "q" :
        print("executing SG_q ...")
        return True
    else:
        print("invalid SG subcommand")
        command_SG_helpmenu()


#fulfills client requested functions in the RG submenu
# @param args : list of str , contains user processed input.
def perform_action_rg_submenu(args):
    if len(args) ==0 :
        print("Error : nothing entered")
    elif args[0] == "r" :
        print("executing AG_s ...")
    elif args[0] == "n" :
        print("executing AG_u ...")
    elif args[0] == "p" :
        print("executing AG_n ...")
    elif args[0] == "q" :
        print("executing AG_q ...")
        return True
    else:
        print("invalid AG subcommand")
        command_AG_helpmenu()

# AG help menu
def command_AG_helpmenu():
    print("\n AG Subcommands")
    print("s [m...n] : subscribe to group numbers")
    print("u [m...n] : unsuscribe from group numbers")
    print("n [n] : display next n groups")
    print("q : quit submenu")

# SG help menu
def command_SG_helpmenu():
    print("\n SG Subcommands")
    print("u [m...n] : unsuscribe from group numbers")
    print("n [n] : display next n groups")
    print("q : quit submenu")


    


#------------------------------#
#   USER INTERFACE PROCEDURES  #
#------------------------------#

#handles help menu
def print_help():
    print("\t-----------------------------------------------")
    print("\t|                  COMMANDS                   |")
    print("\t-----------------------------------------------")
    print("\t| ag [num results to display] : all groups")
    print("\t| sg [num results to display] : subscribed groups")
    print("\t| rg [Group Name][num results to display] : read group")
    print("\t| logout : end sesssion")
    print("\t| -----------------------------------------------|")


#format response string
def print_server_response(serverResp):
    print("-------------------")
    print(serverResp)
    print("-------------------")

def print_commandline_interface():
    print("\n\n*****************************")
    print(" AVAILABLE COMMAND OPTIONS ")
    print(" 1) login [YOUR ID] " )
    print(" 2) help  " )
    print("******************************")


#---------------------------------#
#   USER-INTERFACE CONTROL FLOW   #
#---------------------------------#

# trim user input into a list of strings, to be used for determining control flow
# @param args : string , from user command line input
def trim_to_arg_array(args):
    args = str(args)
    print(args)
    args = args.lstrip()
    args = args.rstrip()
    args = args.split()
    return args


#perform authenticated action (ag,sg,rg,logout)
# This happens only when a user is logged in
# @param args : [string] , parsed into a list of strings, with command at args[0]
# @param server , server socket. 
def authenticated_action(args,server):
    if(userData == None or len(userData) ==0 ):
        print("User is currently not logged in, please use login [user_id]")
    elif(args[0] == "ag"):
        print("executing command ag ...")
        #try if valid N argument (N = num to display), else use default value
        try:
            perform_ag(server, int(args[1]))
        except:
            perform_ag(server,DEFAULT_STEP)
    elif(args[0]=="sg"):
        print("executing command sg ...")
        #try if valid N argument (N = num to display), else use default value
        try:                            
            perform_sg(server, int(args[1]))
        except:
            perform_sg(server, DEFAULT_STEP)
    elif(args[0]=="rg"):
        print("executing command rg ...")
        if(verbose) : print("arguments : " + str(args))
        if(len(args)<2):
            print("Not enough arguments. Command rg has 1 mandatory arg and one optional arg")
        else:
            #try if valid N argument (N = num to display), else use default value
            try:                            
                perform_rg(server, str(args[1]),int(args[2]))
            except:
                perform_rg(server, str(args[1]), DEFAULT_STEP)
    elif(args[0]=="logout"):
        perform_logout(server)
        exit()
    else:
        print("Could not find command :"+ str(args[0]) + ", as recognized")
    if(verbose) : print("completed attempt for authenticated_action")

        

#fulfills client requested functions
# @param args : list of str , contains user processed input.
# @param server , server socket
def perform_action(args,server):
    if len(args) ==0 :
        print("Error : not valid option")
    elif args[0] == "login" :
        try:
            login_client_id(args[1])
        except:
            print("Unable to perform: login [user_id]")
    elif args[0] == "help":
        print_help()
    else:
        authenticated_action(args,server)
    


#display UI and perform user request
#@param server, server socket
def user_interface(server):
    #display options and get user choice
    print_commandline_interface()
    user_input = raw_input("Please choose an option\n>>")
    args = trim_to_arg_array(user_input)
    #perform the processed user arguments
    perform_action(args,server)


#------------------------------#
#       SOCKET                 #
#------------------------------#
# Set up a TCP/IP socket connection
def create_tcp_socket(server,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((server,port))
    return s

# Listening for data from server
def start_polling(s):
    serverResponseString = ""
    while True:
        resp = s.recv(1024)
        if(resp == ""):
            print("encountered nil, will stop polling")
            break
        elif(resp == "FIN"):
            print("Received FIN, will stop polling")
            break
        else:
            print_server_response(resp)
            serverResponseString = serverResponseString + resp
    try:
        responseJso = json.loads(serverResponseString)
        if(verbose): print("Assembled server response object")
        if(verbose): print(responseJso)
        return responseJso
    except:
        print("Error Assembling server jso, finished polling")

#--------------------------#
#   EXECUTE SCRIPT         #
#--------------------------#
# create socket
socket = create_tcp_socket(SERVER,PORT)
# try loading user data on local machine
startup_client_file_database(CLIENT_DATA_ADDR)
# perform user interaction
while True:
    user_interface(socket)

