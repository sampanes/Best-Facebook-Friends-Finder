README for FB_selenium_headless_pickle.py
by John Sampanes (jsampthachamp)

WHAT YOU NEED BEFORE RUNNING:
this file
chromedriver (I downloaded mine 12/22/2019) in same directory
python 2.7 is best
packages:
	selenium
	time
	sys
	xlsxwriter
	pickle
Your facebook info:
	username/nickname (facebook.com/nickname takes you to your page)
	facebook email and password
	PRO TIP don't trust random internet people with your username and password
	LOOK OVER ANY CODE THAT ASKS YOU FOR SUCH THINGS, STAY SAFE OUT THERE :)

USAGE:
	Enter email, password, nickname, choose a mode
	(Ideally and a plan for future iterations: change data types so each post is
	an object with reactions as attributes, so we can check old posts for new likes
	up until no new reacts are found, rather than my current brute force methodology)

        Creates a dict of all facebook friends who react (like, love, haha...) to
        posts that the user has made. The dict is structured as follows:
            reacting_peeps[ key ] = value
            key     = FRIEND'S NAME
            value   = TIMES THAT FRIEND HAS REACTED TO POSTS
        Allow plenty of time to scrape user's posts. This is opening each page up and
        that can take some time. Added enough useful outputs and some counting to visually
        demonstrate that app is running correctly

        the pickling of reacts and links will be named
        after user, and excel output will be timestamped, in the unlikely event that
	multiple people use this on the same computer or someone runs this twice and
	doesn't want old data destroyed