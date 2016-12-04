import socket
import json

#--------------------#
#   GLOBAL DATA      #
#--------------------#
server = "127.0.0.1"
port = 1200
CLIENT_DATA_ADDR = "ForumClientData.txt"
verbose = 0
userData ={}

#key commands
LOGIN_COMMAND = "login_command"
POST_COMMAND = "post_command"
HELP_COMMAND = "help_command"


#-----------------------#
#   DATA MANAGEMENT     #
#-----------------------#

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

#tries to load client data on local machine
def login_client_id(client_id):
    global userData
    try:
        usersList = load_json_data(CLIENT_DATA_ADDR)
        userData = usersList[client_id]
        print("CLIENT " + str(client_id) + " LOGGED IN SUCCESSFULLY")
        return True
    except:
        print("CLIENT LOGIN FAILED : " + str(client_id)
        return False



def print_server_response(serverResp):
    print("-------------------")
    print(serverResp)
    print("-------------------")

def client_login(server):
    server.send(LOGIN_COMMAND)

def client_help(server):
    server.send(HELP_COMMAND)

def client_post(server):
    server.send(POST_COMMAND)


def print_commandline_interface():
    print("-------------------")
    print("**  options **")
    print(" 1) login [YOUR ID] " )
    print(" 2) help  " )
    print(" 3) post " ) 
    print("-------------------")
              
def perform_client_action(userInput,server):
    userInput = str(userInput).split() #convert to string and strip whitespace
    if(userInput == "1"):
        client_login(server)
    elif(userInput == "2"):
        client_help(server)
    elif(userInput == "3"):
        client_post(server)
    else:
        print("not valid input")
        server.close()

#display UI and perform user request
def user_interface(server):
    print_commandline_interface()
    user_input = input("Please choose an option\n>>")
    perform_client_action(user_input,server)
       
# Set up a TCP/IP socket connection
def create_tcp_socket(server,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((server,port))
    return s

def start_polling(s):
    # Protocol exchange - sends and receives
    user_interface(s)
    while True:
        resp = s.recv(1024)
        if resp == "": break
        print_server_response(resp)
    # Close the connection when completed
    s.close()

socket = create_tcp_socket(server,port)
start_polling(socket)
print "\ndone"
