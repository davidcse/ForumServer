Group 21
Robert Trujillo
David Lin
Vincent Tereso

FORUM SERVER

There are two files: ForumServer.py - the server program that accepts clients
                     ForumClient.py - the client program that can read and make posts in groups
                     
1. To run these first unzip the package
2. Run the server: python ForumServer.py - take note of the host machine and the port number specified in the server code (60000)
3. Run the client: python ForumClient.py SERVER_MACHINE PORT_NUMBER - specify where to connect to the server
4. After that you are free to use the client

/*****************************************************/
/*			SERVER Documentation                    */
/***************************************************/

The server has a main thread that loads the server data from a predefined relative directory. 
It is called ServerDataFile.txt in the current file path. This file contains a json-formatted object, 
which contains the server data for all groups, discussions, and posts. 

--------------------
Data Management:
--------------------
If the server does not see that this relative path exists, it will instead use sample data that is predefined in the program. 
This sample data is also used to create a new file in the current relative path, for current session use and persistent data storage. 


--------------------
Accepting 
--------------------
The main thread of the server is in a while loop, that continually accepts incoming client connections. 
When a new client is accepted, a child thread is spawned in order to handle the client's socket. 
The side threads continue listening for the child's requests for server data, and fulfills those requests. 
There is a thread spawned for each new client, in order to handle concurrency. 
The main thread continues listening for any new connections. 


---------------------
Handling Requests
--------------------
After connection, the clients have the capability to ask the server for the most up to date data. 
The type of data requested is managed by protocols. If a client does not send a valid protocol that the server recognizes, 
the requests will not be fulfilled. 

------------------------
Protocol Documentation 
------------------------

/* Requests the range of group names between range's start and end on the server data stores. */
GETGROUPRANGE:{
	START: (NUMBER)
	END: (NUMBER)
}

/* Requests the range of posts under the parent group. */
GETPOSTRANGE:{
	GROUPID:(STRING)
	START: (NUMBER)
	END: (NUMBER)
}

/* Requests the posts contents for all the following groups in the array*/
GETGROUPITEMS:{
	GROUPS: (ARRAY OF STRINGS)
}

/* Requests the contents for the specific post under the group*/
GETPOSTID:{
	GROUPID: (STRING)
	POSTID: (STRING)
}

/* Request to add a new post under the specific group*/
SETPOSTID:{
	GROUP: (STRING)
	SUBJECT: (STRING)
	AUTHOR: (STRING)
	BODY: (STRING)	
}

Fin protocol is the corresponding sequence ".\n."
Resource Not found is the corresponding string "NOGRP"



/*********************************************/
/*		CLIENT DOCUMENTATION 				*/
/********************************************/

-------------------------
Server Communication
------------------------
On startup, the client tries to connect to the IP address and port number, passed via 2 arguments in order from the command line. 


-------------------------
Loading Data
-------------------------
If successfully connected to the server, the client proceeds to load the data file containing user accounts and settings.
This data is from a .txt file at a relative path to the current working directory, and is called './ForumClientData.txt'
If the directory doesn't exist, then a sample data is used with two prebuilt users, "Vinny" and "Joe."
The sample data is written to the predefined directory, and used for subsequent sessions. 


-------------------------
Program Structure
-------------------------
Once logged in, the user can perform operations such as AG, SG, and RG. 
A main loop performs the main menu operations, and subsequent loops are used to perform subcommand operations 
within the different modes such as AG,SG, and RG. When finished with these modes, the program returns back to the
main loop where the user can re-enter another command mode (AG,SG,RG), ask for "help", or "logout" of the current user's session. 

-----------------------
Protocol Communication
-----------------------
In each of the modes, the client will ask the server for data to display, by using predefined protocol functions. 
These functions wrap the requests in the specified protocol format documented above, and sends the formatted requests to the server.
Upon receipt of the requested data, the client will parse the response from the server and display it within the application. 

---------------------
Persistence
---------------------
If there is a change in the user's settings at any point during runtime, the client will write the reflected changes into the persistent text file 
at the relative base address. 
