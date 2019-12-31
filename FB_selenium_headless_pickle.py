# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 12:21:30 2019

@author: John

    USAGE:
        Creates a dict of all facebook friends who react (like, love, haha...) to
        posts that the user has made. The dict is structured as follows:
            reacting_peeps[ key ] = value
            key     = FRIEND'S NAME
            value   = TIMES THAT FRIEND HAS REACTED TO POSTS
        Usage: input email, password, and username (dubbed nickname hereafter)
        Acquire user's facebook username/nickname ahead of time, google it if needed
        Allow plenty of time to scrape user's posts. This is opening each page up and
        that can take some time. Added enough useful outputs and some counters to visually
        demonstrate that app is running correctly
"""
import selenium as sel
from selenium import webdriver
import time
import sys
import xlsxwriter
import pickle

# for python 2.x we use raw_input
try:
    input = raw_input
except NameError:
    pass

'''
        GET USER INFO
            Input user email, password, and nickname
            Nickname can be be found (or created on facebook
            though it is usually refered to as a username
            and is used to get to a user's page in the form:
            https://facebook.com/username
            the pickling of reacts and links will be named
            after user, in the unlikely event that multiple
            people use this on the same computer
'''
my_email = input("Facebook Email: ")
my_password = input("Facebook Password: ")
nickname = input("Facebook Nickname/Username, comes after www.facebook.com/_____: ")
#Pickling file names
reacting_pickled = "reacting_peeps_"+nickname+".pickle"
post_links_pickled = "links_visited_"+nickname+".pickle"

print("By default, posts that have been looked at won't be looked at again")
view_bool = input("View only recent? y or yes: ")
# Additional input option for faster debugging
SECRET_DEBUG_SCROLL_SKIPPER = False
if view_bool == 'y' or view_bool == 'yes':
    print("\tViewing only recent")
    VIEW_ONLY_RECENT_POSTS = True
    try:
        reacting_peeps = pickle.load(open(reacting_pickled, "rb"))
        links_visited = pickle.load(open(post_links_pickled, "rb"))
        print("\tpickled data found! Loaded "+str(len(reacting_peeps))+" good friends and "+str(len(links_visited))+" visited posts")
    except (OSError, IOError) as e:
        print("\tno pickle data found, creating good friends list and links visited list")
        reacting_peeps = {}
        links_visited = []
elif view_bool == 'debug':
    print("Secret debug mode activated. Scrolling will be skipped")
    SECRET_DEBUG_SCROLL_SKIPPER = True
    print("\tDebugging, creating new good friends list and links visited list")
    reacting_peeps = {}
    links_visited = []
else:
    print("\tViewing all posts, clearing any pickled data")
    VIEW_ONLY_RECENT_POSTS = False
    reacting_peeps = {}
    links_visited = []

'''
        START REACT-SCRAPER
'''
print("\n--------Starting React-Scraper--------")

'''
        OPEN A HEADLESS WEBDRIVER
            Add options to create the best experience
            then .get(website) to go to facebook
'''
# HERE ARE SOME OPTIONS FOR OUR DRIVER
options = webdriver.ChromeOptions()

# save some time and effort by not creating a gui
options.add_argument('headless')

# set the window size
options.add_argument('window-size=1920x1080')

# log-level: Sets the minimum log level. Values 0 (default) thru 3: 
#    INFO = 0, 
#    WARNING = 1, 
#    LOG_ERROR = 2, 
#    LOG_FATAL = 3.
# default is 0.
options.add_argument('log-level=3')

# remote debugging port below, added to option list
#-------------------------------
#   http://localhost:9222/
#-------------------------------
options.add_argument('--remote-debugging-port=9222') # Recommended is 9222

# INITIALIZE DRIVER
driver = webdriver.Chrome(chrome_options=options)
driver.get('https://facebook.com')

# wait up to 10 seconds for the elements to become available
driver.implicitly_wait(10)

'''
        LOG IN ON FACEBOOK
            Look for email, password, and login elements
            No such elements may be found especially after
            having logged in without logging out.
            Except NoSuchElement and assume that means we are logged in.
'''
# use css selectors to grab the login inputs, then click login
try:
    email = driver.find_element_by_css_selector('input[type=email]')
    password = driver.find_element_by_css_selector('input[type=password]')
    login = driver.find_element_by_css_selector('input[value="Log In"]')
    
    email.send_keys(my_email)
    password.send_keys(my_password)
    
    driver.get_screenshot_as_file('login_screenshot.png')
    
    # login
    print("Logging in :)")
    login.click()
except sel.common.exceptions.NoSuchElementException as e:
    driver.get_screenshot_as_file('noLogin_screenshot.png')
    print("No login necessary: ", e)
except:
    print("Some other exception during login... quitting")
    driver.quit()
    quit()

'''
        GO TO OWNER's PROFILE
            navigate to profile and scroll
            to the bottom of the page,
            or at least until a link appears
            that has been explored
'''
# navigate to owner's profile
profile_link = 'https://www.facebook.com/'+nickname
print("Navigating to: "+profile_link)
driver.get(profile_link)

# Selenium script to scroll to the bottom, wait 3 seconds for the next batch of data to load, then continue scrolling.
# It will continue to do this until the page stops loading new data, or if post has been visited already (optional, set VIEW_ONLY_RECENT_POSTS)
lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
match=False
while(match==False):
    lastCount = lenOfPage
    time.sleep(3)
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    if lastCount==lenOfPage:
        match=True
    biglist=driver.find_elements_by_xpath("//div[@class='_4vn1']/span[@class='_1whp _4vn2']/a[@class='_3hg- _42ft']")
    if biglist[-1].get_attribute("href") in links_visited and VIEW_ONLY_RECENT_POSTS:
        match=True
    if SECRET_DEBUG_SCROLL_SKIPPER:
        match=True

'''
        GATHER LINKS TO LOADED POSTS
            Hopefully all that scrolling means plenty of posts loaded
            Take all the elements with posts and grab links
            Save only links with username/nickname so that
            other people's posts on user's wall aren't explored
            save these all to who react after scroll list of links
'''
# Start gathering permanent links to user's posts
whoreact_afterscroll_links = []
whoreact_afterscroll=driver.find_elements_by_xpath("//div[@class='_4vn1']/span[@class='_1whp _4vn2']/a[@class='_3hg- _42ft']")
print("Loop thru posts and grab links with user nickname")
for h in whoreact_afterscroll:
    theLink = h.get_attribute("href")
    if nickname in theLink:
        whoreact_afterscroll_links.append(theLink)
        sys.stdout.write("\r\t%d links collected..." % len(whoreact_afterscroll_links))
        sys.stdout.flush()

'''
        LOOP THROUGH ALL POSTS
            Gather the reacts of each post
            TODO Determine if webpage_goto
            already has facebook prefix in the attribute
            or if it needs to be added... if it is good without,
            we can delete the line with 'http...k.com', else,
            change str(webpage_...) to +=
'''
print("\nGoing through all user's posts and compiling reactions\n")

for theLink in whoreact_afterscroll_links:
    try:
        if theLink not in links_visited:
            driver.get(theLink)
            webpage_goto = 'https://www.facebook.com'
            webpage_goto_elem = driver.find_element_by_xpath("//div[@data-testid='fbFeedStoryUFI/feedbackSummary']/div[@class='_3vum']/div[@class='_66lg']/span[@aria-label='See who reacted to this']/span[@class='_1n9k']/a[contains(@ajaxify,'/ufi/reaction/profile/dialog/?')]")
            webpage_goto = str(webpage_goto_elem.get_attribute("href"))
            driver.get(webpage_goto)
            myfriends_element=driver.find_elements_by_xpath("//li[@class='_5i_q']/div[@class='clearfix']/a[@class='_5i_s _8o _8r lfloat _ohe']")
            #                                                 <li class="_5i_q"><div class="clearfix"><a class="_5i_s _8o _8r lfloat _ohe" title="
            sys.stdout.write("\r\t%d links visited" % len(whoreact_afterscroll_links))
            sys.stdout.flush()
            for friend in myfriends_element:
                if friend.get_attribute('title') not in reacting_peeps:
                    reacting_peeps[friend.get_attribute('title')] = 1
                else:
                    reacting_peeps[friend.get_attribute('title')] += 1
            links_visited.append(theLink)
        else:
            print("\nDuplicate: link has already been visited "+str(theLink))
    except:
        print("\nissue with link: ",theLink)
        pass 

'''
        PICKLE THE DATA AND ADD TO EXCEL
            Print how many links visited,
            Then dump reactions and links into pickle for next time
            Also creates unique excel sheet. This is due to the long
            run time, any excess workbooks can be deleted, but overwriting
            one that was good could prove aggrivating
'''   
print("\nvisited "+str(len(links_visited))+"/"+str(len(whoreact_afterscroll_links))+" links")

pickle.dump( reacting_peeps, open( reacting_pickled, "wb" ) )
pickle.dump( links_visited, open( post_links_pickled, "wb" ) )

timestr = time.strftime("%Y%m%d-%H%M%S")
friends_workbook = nickname+timestr+".xlsx"
workbook = xlsxwriter.Workbook(friends_workbook)
worksheet = workbook.add_worksheet()

row = 0
col = 0
worksheet.write(0, 0, "Name")
worksheet.write(0, 1, "Reacts")

for key in reacting_peeps.keys():
    row += 1
    worksheet.write(row, col, key)
    worksheet.write(row, col + 1, reacting_peeps[key])

workbook.close()

##THE END
driver.quit()