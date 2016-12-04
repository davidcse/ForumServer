import socket
import json
from StringIO import StringIO 

#----------------------#
#   GLOBAL DATA        #
#----------------------#

# Filepath to the json-formatted text file
DATABASE_FILE_ADDR = "ServerDataFile.txt"

#sample Data
sampleData1 = {
        'group1': {
                "post1":{
                        "author1":"paul",
                        "subject":"firstpost",
                        "body":"The very first sentence"
                    }
            },
        'group2': {
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
#   SERVER PROCEDURES    #
#------------------------#
def execute_help(client):
    client.send("help menu : 1) 2) 3)")

def execute_post(client):
    client.send("post successful")
    print("client posted to server")

def execute_default(client):
    client.send("procedure not found")
    print("client requested a non-existent procedure")

def execute_login(client):
    client.send("login successful: welcome")
    print("Logged in client ")
    

#Dictionary of procedure functions, which must be defined above. 
procedures={
        'post_command' : execute_post,
        'help_command' : execute_help,
        'login_command' : execute_login
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

init_database_object()

#-----------------#
#   TCP/IP        #
#-----------------#
server = ""
port = 1200

# Establish a TCP/IP socket
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('Initialized Socket')
# Bind to TCP port 
s.bind((server,port))
print('Server binded at : ' + str(port))
# ... and listen for anyone to contact you
# queueing up to five requests if you get a backlog
s.listen(5)
print('server is listening')

while True:
        # Wait for a connection
        connect, address = s.accept()
        # Typically fork at this point

        # Receive up to 1024 bytes
        resp = (connect.recv(1024)).strip()
        print("received message : " + str(resp) + " from : " + str(address))
        # And if the user has sent a "SHUTDOWN"
        # instruction, do so (ouch! just a demo)
        if(resp=="SHUTDOWN"):
            break
        else:
            requested_procedure = getProcedure(resp)
            requested_procedure(connect)

        # Send an answer
        connect.send("Server finished performing: '" + resp + "' \n")

        # And there could be a lot more here!

        # When done with a connection close it
        connect.close()
        print("\ndone " + str(address))
        # And loop for / wait for another client

#close the server
s.close()
