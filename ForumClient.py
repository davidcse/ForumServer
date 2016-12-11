import socket
import json
from StringIO import StringIO
from os import path 
import traceback
#--------------------#
#   GLOBAL DATA      #
#--------------------#
SERVER = "127.0.0.1"
PORT = 1200
CLIENT_DATA_ADDR = "./Data/ForumClientData.txt"
DEFAULT_STEP = 5
verbose = 0

global fin
fin = ""

# dictionary storing user settings for the current client.
userData ={}
currentUserId = ""

# sample data file content if none previously exists.
sampleUserData = {
    'Joe':{
             'subscribed':['comp.programming','comp.os.threads'],
              'read':{
                        'comp.programming':['programming post 1','programming post 3'],
                        'comp.os.threads':['threads post 2']
                     }
          },
    'Vinny':{
                'subscribed':['comp.lang.python','comp.lang.java'],
                'read':{
                    }
            }
    }

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

# saves the current user's preferences to file. 
def save_file():
    global userData
    try:
        #update user preferences and store back into file
        database = load_json_data(CLIENT_DATA_ADDR)
        database[currentUserId] = userData
        store_json_data(CLIENT_DATA_ADDR,database)
    except:
        print("FAILED TO SAVE USER DATA AT ADDRESS: " + str(CLIENT_DATA_ADDR))

# Attempts to load a json txt file for client data, else creates one with sample data
# @filePath : string , where to load and store from the data file. 
def load_file(filePath):
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
        print("Client " + str(client_id) + " logged in successfully")
        currentUserId = client_id
        return True
    except:
        print("Login Failed : " + str(client_id))
    return False

#------------------------------#
#       USER PREFERENCES       #
#------------------------------#
def get_subscriptions():
    return userData["subscribed"]

def get_read_posts(groupName):
    return userData["read"][groupName]

def mark_as_read(groupName,post):
    try:
        parentGroup = userData["read"][groupName]
    except KeyError :
        userData["read"][groupName] = []
        parentGroup = userData["read"][groupName]
    if(post not in parentGroup):
        parentGroup.append(post)

def mark_as_subscribed(groupName):
    if(groupName not in userData["subscribed"]):
        userData["subscribed"].append(groupName)
    else:
        print("User is already subscribed to the group: " + str(groupName))
        
def mark_as_unsubscribed(groupName):
    if(groupName in userData["subscribed"]):
        userData["subscribed"].remove(groupName)
    else:
        print("User is already unsubscribed to the group: " + str(groupName))
    
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



#--------------------------#
#   BUILD PROTOCOL HELPERS #
#--------------------------#

# protocol to ask server to retrieve names of groups between the range numbers, in the server's database index. 
def protocol_grouprange(start,end):
    build_string = 'GETGROUPRANGE:{'+'"START":'+ str(start) + ',"END":'+str(end)+'}'
    if(verbose):print("protocol : " + build_string)
    return build_string


# asks server for an array of posts, within range start to end, for the specified group. 
def protocol_postrange(groupName,start,end):
    build_string = 'GETPOSTRANGE:{"GROUPID":"'+ str(groupName) + '","START":'+ str(start) + ',"END":'+str(end)+'}'
    if(verbose):print("protocol : " + build_string)
    return build_string


# protocol to ask server to send all the requested groups in the array, and all of the posts belonging to each group. 
def protocol_group_items(groupNameArray):
    if(not isinstance(groupNameArray,list)):
        print("Can not form a group array protocol, input must be a list of strings of groupnames")
        return
    build_string = 'GETGROUPITEMS:{"GROUPS":['
    for i in range(len(groupNameArray)):
        build_string = build_string +'"' +str(groupNameArray[i]) + '"'
        if(i < (len(groupNameArray)-1)):
            build_string = build_string +  ","
    build_string = build_string + ']}'
    if(verbose):print("protocol : " + build_string)
    return build_string


# protocol to ask server to add a post to the discussion group. 
def protocol_setpost_id(group,post_id,post_content):
    build_string = 'SETPOSTID:{'+'"START":'+ str(start) + ',"END":'+str(end)+'}'
    if(verbose):print("protocol : " + build_string)
    return build_string


# protocol to ask server to retrieve a post under the given group id. 
def protocol_get_postid(group_id,post_id):
    build_string = 'GETPOSTID:{"GROUPID":"'+str(group_id)+'","POSTID":"'+ str(post_id)+'"}'
    if(verbose):print("protocol : " + build_string)
    return build_string


#---------------------------------#
#    MAIN CLIENT PROCEDURES       #
#---------------------------------#

# Attempts to store user preference data, and closes server socket before exiting.
# @param : server , server's socket
def perform_logout(server):
    print("Performing logging out user")
    save_file()
    print("Closing connection with the server ")
    server.close()
    print("Session Terminated Successfully")


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
    print("**\tMAIN MENU\t **")
    print("login [YOUR ID] " )
    print("******************************")

def print_commandline_interface2():
    print("\n\n*****************************")
    print("**\tMAIN MENU\t **")
    print("ag [num results to display] : all groups")
    print("sg [num results to display] : subscribed groups")
    print("rg [Group Name][num results to display] : read group")
    print("logout : end sesssion")
    print("******************************")


#display UI and perform user request
#@param server, server socket
def user_interface(server):
    #display options and get user choice
    if(currentUserId == ""):print_commandline_interface()
    else:print_commandline_interface2()
    user_input = raw_input("\n\n>>")
    args = trim_to_arg_array(user_input)
    #perform the processed user arguments
    perform_action(args,server)


# trim user input into a list of strings, to be used for determining control flow
# @param args : string , from user command line input
def trim_to_arg_array(args):
    args = str(args)
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
        #try if valid N argument (N = num to display), else use default value
        try:
            perform_ag_mainloop(server, int(args[1]))
        except:
            perform_ag_mainloop(server,DEFAULT_STEP)
    elif(args[0]=="sg"):
        #try if valid N argument (N = num to display), else use default value
        try:                            
            perform_sg_mainloop(server, int(args[1]))
        except:
            perform_sg_mainloop(server, DEFAULT_STEP)
    elif(args[0]=="rg"):
        if(verbose) : print("arguments : " + str(args))
        if(len(args)<2):
            print("Not enough arguments. Command rg has 1 mandatory arg and one optional arg")
        else:
            #try if valid N argument (N = num to display), else use default value
            try:                            
                perform_rg_mainloop(server, str(args[1]),int(args[2]))
            except:
                perform_rg_mainloop(server, str(args[1]), DEFAULT_STEP)
    elif(args[0]=="logout"):
        perform_logout(server)
        exit()
    else:
        print("Could not find command :"+ str(args[0]) + ", as recognized")
    if(verbose) : print("completed attempt for authenticated_action")

        

#********************#
#   AG = ALL GROUPS  #
#********************#

# Asks server to display all groups available.
# @param : server , socket of server
# @param : numStep , number of groups to display at a time. 
def perform_ag_mainloop(server,numStep):
    # get groups [n,m] from server , where (m - n) = results display number.
    rangeStart = 1
    rangeEnd = rangeStart + numStep - 1
    server.send(protocol_grouprange(rangeStart,rangeEnd))
    server_response  = start_polling(server)
    if(server_response == None):
        if(verbose): print("Could not evaluate response from server.")
    else:
        # print most recent server response and ask for submenu input
        while True:
            formatted_AG_response(server_response, rangeStart)
            command_AG_helpmenu()
            user_input = raw_input("\nAG >>")
            args = trim_to_arg_array(user_input)
            # resume evaluation of further user input. 
            if len(args) ==0 :
                print("Error : nothing entered")
            elif args[0] == "s" :
                execute_AG_subscribe(args[1:],rangeStart,rangeEnd,server_response)
            elif args[0] == "u" :
                execute_AG_unsubscribe(args[1:],rangeStart,rangeEnd,server_response)           
            elif args[0] == "n" :
                print("Displaying next " + str(numStep) + "results")
                # recalculate range variables and query server for groups within those range
                rangeStart = rangeStart + numStep
                rangeEnd = rangeStart + numStep - 1
                server.send(protocol_grouprange(rangeStart,rangeEnd))
                server_response  = start_polling(server)
                # recontinue submenu control flow evaluation or else exit command.
                if(server_response == None or server_response == [] or server_response == ""):
                    print("server did not send any more group information ... ")
                    break
            elif args[0] == "q" :
                print("quitting AG Mode")
                break
            else:
                print("invalid AG subcommand")
                command_AG_helpmenu()
    #completed the ag submenu            
    if(verbose) : print("Finished executing AG menu.")



# print formatted response for an AG request
def formatted_AG_response(response, start_num):
    print("\n\n**************************")
    print("**    ALL GROUPS    ***")
    print("**************************")
    subscribed_groups = get_subscriptions()
    numCount = start_num
    for groupName in response:
        sub_flag = " "
        if(groupName in subscribed_groups):
            sub_flag = "S"
        format_line = str(numCount) + ". (" +sub_flag + ") " + str(groupName)
        numCount = numCount + 1
        print(format_line)


# subscribes the group for this user and saves the preference.
def execute_AG_subscribe(arglist, start, end, response):
    for i in arglist:
        try:
            optionNum = int(i)
        except:
            print("arguments contained something that was not an integer")
            break
        if(optionNum>=start and optionNum<= end):
            try:
                mark_as_subscribed(response[optionNum-start])
                save_file()
                print("subscribe to no. " + str(optionNum) + " was successful")
            except IndexError :
                print("Argument : " + str(i) + " is not within range")
                break
            except:
                print("Error subscribing to group no. " + str(i))
                traceback.print_exc()
                break


# unsubscribes the group for this user and saves the preference. 
def execute_AG_unsubscribe(arglist, start, end, response):
    unsubscribed_groups = []
    for i in arglist:
        try:
            print("unsubscribing from number " + str(i))
            optionNum = int(i)
        except:
            print("arguments contained something that was not an integer")
            break
        if(optionNum>=start and optionNum<= end):
            try:
                # get the group to unsubscribe, remove from program data, then persist to stored file. 
                unsub_group = response[optionNum-start]
                mark_as_unsubscribed(unsub_group)
                save_file()
                unsubscribed_groups.append(unsub_group)
                print("unsubscribe to no. " + str(optionNum) + " was successful")
            except IndexError :
                print("Argument : " + str(i) + " is not within range")
                break
            except Exception as error:
                print("Error unsubscribing to group no. " + str(i))
                traceback.print_exc()
                break
    return unsubscribed_groups

    

# Prints the usage statement in the AG submenu
def command_AG_helpmenu():
    print("\n AG Subcommands")
    print("s [m...n] : subscribe to group numbers")
    print("u [m...n] : unsuscribe from group numbers")
    print("n [n] : display next n groups")
    print("q : quit submenu\n\n")




#**************************#
#   SG = SUBSCRIBED GROUPS #
#**************************#

# Asks server to display N-number of subscribed groups available.
# @param : server , socket of server
# @param : numStep , number of groups to display at a time. 
def perform_sg_mainloop(server,numStep):
    # get groups [n,m] from server , where (m - n) = results display number.
    subscribed_array = get_subscriptions()
    rangeStart = 1
    rangeEnd = rangeStart + numStep - 1
    server.send(protocol_group_items(subscribed_array[(rangeStart-1):(rangeEnd)]))
    server_response = start_polling(server)
    # handle and display the server's response
    if(server_response == None or server_response ==[] or server_response == "" or server_response == {}):
        if(verbose): print("Could not evaluate response from server.")
    else:
        # print most recent server response and ask for submenu input
        while True:
            formatted_SG_response(server_response, rangeStart)
            command_SG_helpmenu()
            user_input = raw_input("\nSG >>")
            args = trim_to_arg_array(user_input)
            # resume evaluation of further user input. 
            if len(args) ==0 :
                print("Error : nothing entered")
            elif args[0] == "u" :
                unsubscribed_groups = execute_SG_unsubscribe(args[1:],rangeStart,rangeEnd,server_response)
                if(unsubscribed_groups != None and unsubscribed_groups != []):
                    # remove the recently unsubscribed group from the server response to be redisplayed in the next SG-Format.
                    server_response = {key: value for key, value in server_response.items() if key not in  unsubscribed_groups}
            elif args[0] == "n" :
                print("Displaying next " + str(numStep) + "results")
                # recalculate range variables and query server for groups within those range
                subscribed_array = get_subscriptions()
                rangeStart = rangeStart + numStep
                rangeEnd = rangeStart + numStep - 1
                server.send(protocol_group_items(subscribed_array[(rangeStart-1):(rangeEnd)]))
                server_response = start_polling(server)
                # recontinue submenu control flow evaluation or else exit command.
                if(server_response == None or server_response == [] or server_response == "" or server_response =={}):
                    print("server did not send any more group information ... ")
                    break
            elif args[0] == "q" :
                print("quitting SG Mode")
                break
            else:
                print("invalid SG subcommand")
                command_SG_helpmenu()
    #completed the ag submenu            
    if(verbose) : print("Finished executing SG menu.")





# Formatted response for an SG request
def formatted_SG_response(response, start_num):
    print("\n\n**************************")
    print("**  SUBSCRIBED GROUPS  ***")
    print("**************************")
    # print the subscribed groups formatted way
    numCount = start_num
    for i in response:
        num_unread = get_num_unread_posts(i,response[i])
        format_line = str(numCount) + ". " +str(num_unread) + " " + str(i)
        numCount = numCount + 1
        print(format_line)



# unsubscribes the group for this user and saves the preference.
# @arglist : list of user input arguments.
# @start : starting num
# @end : ending num
# @response : json response object from the server.
# @returns : string name of the unsubscribed group. 
def execute_SG_unsubscribe(arglist, start, end, response):
    unsubscribed_groups = []
    for i in arglist:
        try:
            print("unsubscribing from number " + str(i))
            optionNum = int(i)
        except:
            print("arguments contained something that was not an integer")
            break
        if(optionNum>=start and optionNum<= end):
            try:
                group_to_unsubscribe = list(response)[optionNum-start]
                mark_as_unsubscribed(group_to_unsubscribe) #convert dict to list on the fly, then access the Nth key element. 
                save_file()
                print("unsubscribe to no. " + str(optionNum) + " was successful")
                unsubscribed_groups.append(group_to_unsubscribe)
            except IndexError :
                print("Argument : " + str(i) + " is not within range")
                break
            except Exception as error :
                print("Error unsubscribing to group no. " + str(i))
                traceback.print_exc()
                break
    return unsubscribed_groups

# SG help menu
def command_SG_helpmenu():
    print("\n SG Subcommands")
    print("u [m...n] : unsuscribe from group numbers")
    print("n [n] : display next n groups")
    print("q : quit submenu\n\n")


#**************************#
#   RG = READ GROUP        #
#**************************#

def find_read_range(num_str):
    start_end_arr = []
    rangeNums = num_str.split("-")
    if len(rangeNums) == 1:
        start_end_arr.append(int(rangeNums[0].strip()))
        start_end_arr.append(int(rangeNums[0].strip()))
    elif len(rangeNums) == 2:
        start_end_arr.append(int(rangeNums[0].strip()))
        start_end_arr.append(int(rangeNums[1].strip()))
    else:
        print("Entered an invalid range of numbers")
    return start_end_arr
    

# Asks server to display N-number of posts available for a specified group.
# @param : server , socket of server
# @groupName : str, name of the target group. 
# @param : numStep , number of groups to display at a time. 
def perform_rg_mainloop(server, groupName, numStep):
    # get posts [n,m] from server for the specified group, where (m - n) = results display number.
    rangeStart = 1
    rangeEnd = rangeStart + numStep - 1
    server.send(protocol_postrange(groupName,rangeStart,rangeEnd))
    server_response = start_polling(server)
    # handle and display the server's response
    if(server_response == None or server_response ==[] or server_response == "" or server_response == {}):
        if(verbose): print("Could not evaluate response from server.")
    else:
        # print most recent server response and ask for submenu input
        while True:
            formatted_RG_response(server_response, groupName, rangeStart)
            command_RG_helpmenu()
            user_input = raw_input("\nRG >>")
            args = trim_to_arg_array(user_input)
            # resume evaluation of further user input. 
            if len(args) ==0 :
                print("Error : nothing entered")
            elif args[0] == "r" :
                read_ranges = find_read_range(args[1])
                start_range = read_ranges[0]
                end_range = (read_ranges[1]) + 1
                for i in range(start_range,end_range, 1):
                    index = i - rangeStart
                    post_keystring = list(server_response)[index]
                    mark_as_read(groupName, post_keystring)
                # persist the read status change into data file
                save_file()
            elif args[0] == "n" :
                print("Displaying next " + str(numStep) + "results")
                # recalculate range variables and query server for groups within those range
                rangeStart = rangeStart + numStep
                rangeEnd = rangeStart + numStep - 1
                server.send(protocol_postrange(groupName,rangeStart,rangeEnd))
                server_response = start_polling(server)
                # recontinue submenu control flow evaluation or else exit command.
                if(server_response == None or server_response == [] or server_response == "" or server_response =={}):
                    print("server did not send any more group information ... ")
                    break
            elif args[0] == "p" : 
                print("execute RG_P")                
            elif args[0] == "q" :
                print("quitting RG Mode")
                break
            # must be an id request, as user enters a number for the option. 
            else:
                try:
                    idNum = int(args[0])
                    relativeNum = idNum - rangeStart
                    if(relativeNum > (len(server_response) -1)):
                        print("The post id you have entered is larger than the available range")
                    else:
                        post_id = list(server_response)[relativeNum]
                        # stay at submenu until completed submenu mode.
                        interface_postid_submenu(server, groupName,post_id,numStep)
                        # exited submenu for the post, so continue
                except Exception as error :
                    print("invalid RG subcommand " + str(error))
                    command_RG_helpmenu()
    #completed the rg submenu            
    if(verbose) : print("Finished executing RG menu.")


# submenu interface for examining the contents of a post.
def interface_postid_submenu(server, groupName, post_id, numStep):
    start = 1
    server.send(protocol_get_postid(groupName ,post_id))
    serv_resp = start_polling(server)
    if(serv_resp == None or serv_resp == "" or serv_resp =={}):
        print("server did not send a response for this post id")
    else:
        if verbose : print("Received from server " + str(serv_resp))
        while True:
            formatted_postid_response(serv_resp[post_id],start, numStep)
            user_input = raw_input("\n[id] >>")
            args = trim_to_arg_array(user_input)
            if(len(args) == 0):
                print("No command was found, please submit command")
            elif args[0] == "n" :
                start = start + numStep
                lines_in_post_body = serv_resp[post_id]["Body"].split("\n")
                if(start > len(lines_in_post_body)):
                    print("The post has no more content to show.\n Exiting post view mode")
                    break
            elif args[0] ==  "q" :
                print("quitting post [id] submenu\n\n")
                break
    

# prints the formatted response for a post content
def formatted_postid_response(response, start_num, num_step):
    content = response["Body"]
    content = content.split("\n")
    end_num = start_num + num_step - 1
    contStatus = "\t[CONTINUED]..."
    if(start_num ==1):
        contStatus = ""
    
    print("\n******* Post Content *************")
    print("Group : " + str(response["Group"]))
    print("Subject : " + str(response["Subject"]))
    print("Author : " + str(response["Author"]))
    print("Date : " + str(response["Date"]))
    print("Body : " + str(contStatus) + "\n")
    for i in content[start_num-1:end_num]:
        print(i)
        
        

# Formatted response for an RG request
# @response : the string parsed to json obj. from server. 
def formatted_RG_response(response, groupName, start_num):
    print("\n\n************************************")
    print("**    READ GROUP: " + str(groupName) + "    ***")
    print("*****************************************")
    read_posts = get_read_posts(groupName)
    numCount = start_num
    post_list = list(response)
    for i in post_list:
        newStatus = " "
        if i not in read_posts:
            newStatus = "N"
        format_line = str(numCount) + ". " +str(newStatus) + " " + str(response[i])  + " " + str(i)
        numCount = numCount + 1
        print(format_line)
        
# RG help menu
def command_RG_helpmenu():
    print("\n RG Subcommands")
    print("[id] : read post number [id]'s contents")
    print("r [m] | [m-n] : mark post or posts within range as read")
    print("n : display next set of posts")
    print("p : make new post on server")
    print("q : quit submenu\n\n")


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
    if verbose : print("waiting for server response")
    serverResponseString = ""
    while True:
        resp = s.recv(1)
        if(checkFin(resp)):
            print("Received FIN, will stop polling")
            break
        else:
            serverResponseString = serverResponseString + resp
    try:

        # TRIM END PROTOCOL OFF SERVER RESPONSE
        print("Server Response:" + serverResponseString)
        serverResponseString = serverResponseString[0:-2]
        responseJso = json.loads(serverResponseString)
        if(verbose): print("Assembled server response object")
        if(verbose): print(responseJso)
        return responseJso
    except:
        print("Error Assembling server jso, finished polling")


def checkFin(new):
    global fin
    if(fin == "" and new == "\n"):
        fin = fin + new
        return False
    elif fin == "\n" and new == ".":
        fin = fin + new
        return False;
    elif fin == "\n." and new == "\n":
        fin = ""
        return True
    else:
        fin = ""
        return False

#--------------------------#
#   EXECUTE SCRIPT         #
#--------------------------#
# create socket
socket = create_tcp_socket(SERVER,PORT)
# try loading user data on local machine
load_file(CLIENT_DATA_ADDR)
# perform user interaction
while True:
    user_interface(socket)

