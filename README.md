# Lab4 CS61, Dartmouth 22F
## Team 27, Hank Patil and Ethan Thomas

### Included files
Provided files include:
 - Team27Lab4.ini
 - dbconfig.py
 - userinterface.py
 - testing.in
 - testing.out

### Using the program
To use the program, it is required to have pymongo installed. To run, use `python userinterface.py`.

Use `python userinterface.py < testing.in > grader.testing.out` to feed our test commands from `testing.in` to the program and redirect output into `testing.out`.

### Implementation
To connect to the atlas cluster, we use `dbconfig.py` to parse the username and password stored in `Team27Lab4.ini`. `dbconfig.py` returns a uri string used in `userinterface.py` to get a pymongo client to the cluster.

`userinterface.py` includes 4 methods:
 - run_interface()
 - parse_command()
 - to_string()
 - recursive_comments()

#### run_interface()
This method uses `dbconfig.py` to get the uri and connect to the atlas cluster. Then it takes in user input and passes it onto `parse_command()`. `main()` calls `run_interface()` to receive input while the user hasn't quit the program.

#### parse_command()
This method receives a command in the form of a string and parses it to complete the desired user command. Before executing a command, the length of the command is verified. If an unknown command is provided, the user is told to try again.

There are 4 commands that this method completes:
 - show
 - post
 - comment
 - delete

##### show
For the desired blog, print out every post and comment in the blog. Posts and comments are printed out using `to_string()` in a similar format to the printout in the problem description.

##### post
For the desired blog, insert a new document to the blog.

##### comment
For the desired blog, insert a new comment to the blog under the referenced post/comment. To do so, we query the desired blog for a post/comment with the provided permalink and append that post/comment's `comments` field with this comment's object id. This is useful for when we want to post comments with proper indendation (i.e. posting a comment indented under the post/comment it commented on).

If the referenced post/comment doesn't exist, we don't create this comment.

##### delete
For the desired blog, delete the body text of the referenced post/comment. To do so, we query the desireed blog for the post/comment with the provided permalink and update that post/comment's `body` field with `deleted by [username]`.

If the referenced post/comment doesn't exist, we don't update any post/comment's body text.

#### to_string()
This method recieves all of the posts in a given collection and prints them out in a format similar to the one provided in the printout in the problem description. It looks at each post in the collection and prints posts with a leftmost indentation. Then for each comment, we use a DFS style recursion in `recursive_comments()` to properly indent comments of posts/comments.

#### recursive_comments()
This method uses a DFS style recursion to build a string of all comments under a post and indent them such that comments are indented according to how deep under a post they are. For example, a post has depth 0, a comment on that post has depth 1, a comment on that comment has depth 2, and so on. Once all comments under a post have been added to the built-up string, we return the string and print it in `to_string()`.

### Testing
We provide a `testing.in` file to test the functionality of `userinterface.py`. Firstly, we populate a blog called `blog1` with:
 - a post with 2 comments, and one of these has a comment
 - a post with a comment

Then we show the blog to see all of its posts.

Then we delete one of the posts and one of the comments, and again show the blog to illustrate the deletions.

Secondly, we populate a second blog called `blog2` with a single post to illustrate creating a new collection in the cluster.

We show the blog and then comment on the post, and again show the blog to illustrate working `post` and `comment` commands.

Finally, we test error handling:
 - We try to show a non-existent blog
 - We try to add a comment on a non-existent post
 - We try to delete a non-existent post
 - We provide incomplete commands for each type of command
