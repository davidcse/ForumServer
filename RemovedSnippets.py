###############
# REMOVED SERVER CODE
###############

#---------------------#
#   CLASS DEFINITIONS #
#---------------------#

class Discussion:
    def __init__(self,name,groupArray):
        self.name = name
        if(groupArray !=None):
            self.groups = groupArray
        else:
            self.groups = []
            
    
class Group:
    def __init__(self,name,posts=None):
        self.name = name
        if(posts != None):
            self.posts = posts
        else:
            self.posts = []

    def serialize(self):
        json.dumps
    
    def stringify(self):
        print("GROUP NAME : " + str(self.name))
        for i in self.posts:
            i.stringify()

        
class Post:
    def __init__(self,author, subject,body):
        self.author = author
        self.subject = subject
        self.body = body

    def stringify(self):
        print("author: " + str(self.author))
        print("subject: " + str(self.subject))
        print("body: "  + str(self.body))
    
#-----------------#
#   DATA(BASE)    #
#-----------------#
#adds group object into the map
def storeGroup(groupName,groupObj):
    global discussions
    discussions[groupName] = groupObj

#adds a post into the parent group, from the map
def storePost(groupName,postObj):
    global discussions
    parentGroup = discussions[groupName]
    parentGroup.posts.append(postObj)

#parses a string into group object, stores into the discussion map
def parseGroupLine(line):
    line = line.split("group:")
    groupName = line[1]
    print(groupName)
    groupObj = Group(groupName)
    storeGroup(groupName,groupObj)
    if verbose :
        print("created Group")
        groupObj.stringify()

#parses a string into post object, stores it in the discussion map
def parsePostLine(line):
    line = line.split("-")
    groupName = line[0].strip("post:")
    postContent = line[1]

    storePost(groupName,Post("postAuthor","postSubj","postBody"))
    if(verbose):
        print("------ parsed object-------")
        print("key: " + str(groupName) + "\npost object: " + str(postContent))
    
def load_post_data(filePath):
    file = open(filePath, 'r')
    data = file.read()
    if(verbose):
        print(data)
    return data.split("\n")

def parse_objects(data):
    for i in data:
        if i.startswith("group:"):
            parseGroupLine(i)
        elif i.startswith("post:"):
            parsePostLine(i)
        else:
            if(verbose):
                print("not parsed: " + str(i))

#-----------------#
#   LOAD          #
#-----------------#
#data = load_post_data("./Desktop/ForumServerData.txt")
#parse_objects(data)
