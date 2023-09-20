import pymongo
import shlex
import re
from dbconfig import read_db_config

def parse_command(command, db):
    command = shlex.split(command)

    if command[0] == "show":
        if len(command) != 2:
            print("Syntax error. Usage: <show> <blogname>\n")
            return
        
        try:
            collection_name = command[1]

            if collection_name not in db.list_collection_names():
                print("This collection does not exist")
                return

            collection = db[collection_name]
            
            posts = collection.find()

            print("\nItems in", collection_name)
            to_string(posts, collection)

        except Exception as e:
            print("Error showing collection:", type(e), e)

    elif command[0] == "post":
        if len(command) != 7:
            print("Syntax error. Usage: <post> <blogname> <username> <title> <postbody> <tags> <timestamp>\n")
            return

        # collection
        blogname = command[1]

        # document fields
        username = command[2]
        title = command[3]
        postbody = command[4]
        tags = command[5].split(', ')
        depth = 0
        comments = []
        timestamp = command[6]

        permalink  = blogname+'.'+re.sub('[^0-9a-zA-Z]+', '_', title)

        post = {
            'title': title,
            'userName': username,
            'tags': tags,
            'depth': depth,
            'permalink': permalink,
            'body': postbody,
            'comments': comments,
            'timestamp': timestamp
        }

        try:
            collection = db[blogname]

            inserted_id = collection.insert_one(post).inserted_id

            print("Successfully inserted {} to {}".format(inserted_id, blogname))
        except Exception as e:
            print("Error trying to write to collection:", type(e), e)

    elif command[0] == "comment":
        if len(command) != 6:
            print("Syntax error. Usage: <comment> <blogname> <permalink> <username> <commentbody> <timestamp>\n")
            return

        # collection
        blogname = command[1]

        # query collection on permalink reference
        permalink = command[2]

        # document fields
        username = command[3]
        commentbody = command[4]
        timestamp = command[5]     # a comment's permalink is its timestamp

        try:
            collection = db[blogname]

            # update the referenced post
            post = collection.find_one({'permalink': permalink})

            if post is not None:
                depth = post['depth'] + 1

                comment = {
                    'userName': username,
                    'body': commentbody,
                    'depth': depth,
                    'comments': [],
                    'permalink': timestamp,
                    'reference': permalink
                }

                inserted_id = collection.insert_one(comment).inserted_id

                print("Successfully inserted {} to {}".format(inserted_id, blogname))

                collection.update_one({'permalink': permalink}, {"$push": {"comments":inserted_id}})
            else:
                print("This post does not exist")
        except Exception as e:
            print("Error trying to write to collection:", type(e), e)
    
    elif command[0] == "delete":
        if len(command) != 5:
            print("Syntax error. Usage: <delete> <blogname> <permalink> <username> <timestamp>\n")
            return

        # collection
        blogname = command[1]

        permalink = command[2]
        username = command[3]
        timestamp = command[4]

        try:
            collection = db[blogname]

            post = collection.find_one({'permalink': permalink})

            if post is not None:
                deleted_string = "deleted by [{}]".format(username)

                collection.update_one({'permalink': permalink}, {"$set": {"body": deleted_string, "timestamp": timestamp}})
            else:
                print("This post does not exist")
        except Exception as e:
            print("Error trying to update in collection:", type(e), e)

    elif command[0].lower() == 'q' or command[0].lower() == "quit":
        print()
        return
    
    else:
        print("Unknown command\n")

    print()

def to_string(posts, collection):
    print()
    for post in posts:
        if 'tags' in post:
            print('- - - -')
            for key in post:
                if key == "title" or key == "userName" or key == "timestamp" or key == "permalink":
                    print("  " + str(key) + ": " + str(post[key]))
                elif key == "body":
                    print("  Body:\n    ", str(post[key]))
            
            for comment_id in post['comments']:
                print(recursive_comments(comment_id, collection))

def recursive_comments(comment_id, collection):
    comment = collection.find_one({"_id": comment_id})

    curr_comment = "\n" + comment['depth']*"  " + "- - - -\n"

    for key in comment:
        if key == "userName" or key == "permalink":
            curr_comment += 2 * comment['depth']*"  " + str(key) + ": " + str(comment[key]) + "\n"
        if key == "body":
            curr_comment += 2 * (comment['depth'])*"  " + "comment: " + "\n"
            curr_comment += 2 * (comment['depth'] + 1)*"  "+ str(comment[key]) + "\n"
    
    sub_comments = comment['comments']

    if len(sub_comments) != 0:
        for sub_comment_id in sub_comments:
            return curr_comment + recursive_comments(sub_comment_id, collection)
    else:
        return curr_comment

def run_interface():
    # get connection uri
    uri = read_db_config()

    # connect to atlas cluster
    try:
        client = pymongo.MongoClient(uri)
        print("Connection successful")

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print("Connection failure:")
        print(err)

    # get the database for this lab
    db = client.Team27db

    # welcome the user
    print("\nWelcome")

    # accept input from the user
    while True:
        try:
            print("Please enter your command:")
            command = input("> ")

            # print the command back; only used if feeding lines to stdin from .in file
            print(command)

            if len(command) == 0:
                print("Please try again\n")
                continue

            parse_command(command, db)

            if command.lower() == "quit" or command.lower() == 'q':
                print("Goodbye")
                return

        except EOFError:
            print("EOF. Goodbye")
            return

if __name__ == "__main__":
    run_interface()
