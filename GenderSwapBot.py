from twython import Twython, TwythonError
from threading import Timer
from secrets import *
from random import randint
import time

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

#dictionary of words to replace
replace = { 
            "actor": "actress",
            "actors": "actresses",
            "bachelor": "bachelorette",
            "boy": "girl",
            "boys": "girls",
            "boyfriend": "girlfriend",
            "boyfriends": "girlfriends",
            "brother": "sister",
            "brothers": "sisters",
            "dad": "mom",
            "Dad": "Mom",
            "dads": "moms",
            "Dads": "Moms",
            "dude": "dudette",
            "dudes": "dudettes",
            "he": "she",
            "him": "her",
            "his": "her",
            "husband": "wife",
            "father": "mother",
            "fathers": "mothers",
            "guy": "gal",
            "gentleman": "lady",
            "gentlemen": "ladies",
            "groom": "bride",
            "king": "queen",
            "kings": "queens",
            "male": "female",
            "man": "woman",
            "Man": "Woman",
            "manhood": "womanhood",
            "manly": "womanly",
            "masculine": "feminine",
            "masculinity": "femininity",
            "meninism": "feminism",
            "#Meninism": "#Feminism",
            "#meninism": "#feminism",
            "mister": "miss",
            "men": "women",
            "Men": "Women",
            "Mr.": "Ms.",
            "prince": "princess",
            "sir": "ma'am",
            "son": "daughter",
            "sons": "daughters",
            "Son": "Daughter",
            "actress": "actor",
            "actresses": "actors",
            "bachelorette": "bachelor",
            "bride": "groom",
            "daughter": "son",
            "daughters": "sons",
            "Daughter": "Son",
            "dudette": "dude",
            "dudettes": "dudes",
            "female": "male",
            "feminine": "masculine",
            "femininity": "masculinity",
            "feminism": "meninism",
            "#Feminism": "#Meninism",
            "#feminism": "#meninism",
            "gal": "guy",
            "girl": "boy",
            "girls": "boys",
            "girlfriend": "boyfriend",
            "girlfriends": "boyfriends",
            "her": "him",
            "her": "his",
            "lady": "gentleman",
            "ladies": "gentlemen",
            "ma'am": "sir",
            "mom": "dad",
            "Mom": "Dad",
            "moms": "dads",
            "Moms": "Dads",
            "mother": "father",
            "mothers": "fathers",
            "Ms.": "Mr.",
            "princess": "prince",
            "she": "he",
            "sister": "brother",
            "sisters": "brothers",
            "wife": "husband",
            "woman": "man",
            "Woman": "Man",
            "womanhood": "manhood",
            "womanly": "manly",
            "women": "men",
            "Women": "Men",
            "queen": "king",
            "queens": "kings"
            }



name = '@GenderSwapBot'


def getTweet():
    """
    Gets tweet containing a word from the replace dictionary
    """
    keyList = list(replace)
    # print(keyList)
    search = keyList[randint(0,len(keyList)-1)]
    print("Searching " + search)


    results = twitter.search(q=search, count = 1)
    for tweet in results["statuses"]:
        print("Getting tweet!")

        # try:
        #   print(tweet['text'].encode('utf8').decode('utf8'))
        # except:
        #   print("Cannot print")
        

        return tweet




def getMentions():
    """
    Gets the tweets that mentioned the bot
    """
    mentions = twitter.search(q=name, count = 5)    #search twitter for bot username
    mentionsList = []                               #make list to contain mention tweets
    for mention in mentions["statuses"]:            #add tweets to list
        # print("Got a mention!")
        mentionsList.append(mention)

    mentionsFile = open('mentions.txt', 'r')        #Get IDs mentions that have already been addressed in the past
    oldMentionsList = mentionsFile.readlines()      #Put each in a list
    mentionsFile.close()

    newMentionsList = []                            #Make a list of mentions that have not been addressed
    for mention in mentionsList:                    #by comparing the mentions that were harvested to the old mentions
        mentionText = mention['text'].encode('utf8').decode('utf8')
        if not mention['id_str'] + "\n" in oldMentionsList and mentionText[0:2] != "RT" and name in mentionText:
            newMentionsList.append(mention)

    mentionsFile = open('mentions.txt', 'a')        #append new mentions to the old mentions file
    for mention in newMentionsList:
        mentionsFile.write(mention['id_str'] + "\n")
    mentionsFile.close()
    return newMentionsList


def getOembed(id_str):
    """
    Gets Embed link of a tweet
    """
    oembed_dict = twitter.get_oembed_tweet(id=id_str)
    html_to_encode = oembed_dict['html']
    return html_to_encode.encode('utf-8').decode('utf8')



def makeNewTweet(t):
    """
    Takes a list of words t (the tweet)
    and swaps the gender of any gendered word
    """
    numEdits = 0            #counter of number of changes made to tweet
    newWords = []           #put new tweet in this list
    index = 0               #index of word being currently looked at

    tweetWords = t['text'].encode('utf8').decode('utf8').split()        #Get the text of a tweet
    for x in tweetWords:                                                #For each word in the tweet
        havePunc = False                                                #whether or not it has punctuation
        punc = ''

        #The current character count of the tweet
        currLen = len(' '.join(newWords[:index]) + ' '.join(tweetWords[index:]))

        #if there is punctuation with the word being checked
        if x[-1] == ',' or x[-1] == '.' or x[-1] == '?' or x[-1] == '!' or x[-1] == ':' or x[-1] == ';':
            havePunc = True                                             #It has punctuation
            punc = x[-1:]                                               #store the punctuation for later
            X = x[:-1]                                                  #save the word w/o punctuation
        elif x[-2:] == "'s":                                            #Do the same if it's possessive
            havePunc = True
            punc = "'s"
            X = x[:-2]
        else:                                                           #Else just get the word
            X = x


        # if name in tweetWords:
        #   maxCount = 140
        # else:
        #   maxCount = 116

        maxCount = 140                                                  #maximum char count

        if not name in X:                                               #disregard bot's username (the tweet is a mention)
            if X == '&amp':
                newWords.append('&')
            elif X in replace and len(replace[X] + punc) - len(X + punc) + currLen < maxCount:  #if it's a key word and adding it  doesn't put tweet over 140 char
                newWords.append(replace[X] + punc)                                              #replace it
                numEdits += 1                                                                   #add to the number of edits
            elif X.lower() in replace and len(replace[X.lower()] + punc) - len(X.lower()+ punc) + currLen < maxCount:
                if X == X.lower().capitalize():                                                 #check for capitalization
                    newWords.append(replace[X.lower()].capitalize() + punc)
                else:                                                                           #or all caps
                    newWords.append(replace[X.lower()].upper() + punc)
                numEdits += 1                                                                   #add to the number of edits
            else:                                                                               #else don't change it
                newWords.append(X + punc)
        else:                                                                                   #if word is bot's username
            newWords.append(t['user']['screen_name'].encode('utf8').decode('utf8'))             #replace it with the user the bot is replying to
        index += 1                                                                              #update current index


    currLen = len(' '.join(newWords))   #update current character count
    print("Character Count:",currLen)
    if(numEdits < 1):                   #if no edits, don't return tweet
        return None
    return newWords


    

def tweet(tweet):
    """
    Tweets a string
    """
    twitter.update_status(status = tweet);





lastTweet = None        #to store the last tweet that was edited by the bot


def mentionEdit():
    """
    Edits a tweet that mentioned the bot
    """
    mentionList = getMentions()             #get list of new mentions
    for mention in mentionList:             #Get the text of each mention
        tweetWords = mention['text'].encode('utf8').decode('utf8').split()
        print(' '.join(tweetWords))
        
        #Get the username of the person who mentioned you
        username = mention['user']['screen_name'].encode('utf8').decode('utf8')
        print(username)

        #Edit mention
        newTweetWords = makeNewTweet(mention)

        if newTweetWords == None:               #if no changes
            print("No changes to tweet!")
        else:
            newTweet = ' '.join(newTweetWords)  #Join words into one string
            try:
                print(newTweet)     
            except:
                print("Cannot print")

            if (not debug):                     #If not in debug mode
                try:
                    # tweet(newTweet + " " + origTweetURL)
                    tweet(newTweet)             #Tweet new tweet
                    print("I just tweeted!")
                except:
                    print("Ran into a problem tweeting!")


def runBot():
    print("Bot running!")

    trying = True

    # pulledTweet = getTweet()
    while(trying):                      #Keep trying to get a tweet til you find one that works
        try:
            pulledTweet = getTweet()
            origTweet = pulledTweet['text'].encode('utf8').decode('utf8')
            trying = False
        except:
            print("Couldn't pull tweet. Trying again.")
            trying = True
    
    #Get username of tweeter
    username =pulledTweet['user']['screen_name'].encode('utf8').decode('utf8')
    print(username)

    #Get the URL of the original tweet
    origTweetURL = "twitter.com/" + username + "/status/" + pulledTweet['id_str']
    print(origTweetURL)

    global lastTweet

    try:
        print(origTweet)
    except:
        print("Cannot print")

    if len(origTweet) > 140:                        #check length of tweet, if too long try again
        print("Tweet too long!")
        lastTweet = origTweet
        time.sleep(10)
        runBot()
    elif origTweet != lastTweet:                    #make sure the bot hasn't edited the tweet before

        newTweetWords = makeNewTweet(pulledTweet)   #edit tweet

        if newTweetWords == None:                   #if no changes
            print("No changes to tweet!")
            lastTweet = origTweet

            time.sleep(10)
            runBot()                                #try again
        else:
            newTweet = ' '.join(newTweetWords)      #combine tweet words into one string
            try:
                print(newTweet)             
            except:
                print("Cannot print")

            if (not debug):                         #if not in debug mode
                try:
                    # tweet(newTweet + " " + origTweetURL)
                    tweet(newTweet)                 #tweet new tweet
                    print("I just tweeted!")
                except:
                    print("Ran into a problem tweeting!")

            lastTweet = origTweet                   #set last tweet to this tweet
    else:                   
        print("No new Tweet!")                      #if no new tweet, try again
        time.sleep(10)
        runBot()

    mentionEdit()                                   #check mentions, and edit those




def setInterval(func, sec):
    def func_wrapper():
        setInterval(func, sec)
        func()
    t = Timer(sec, func_wrapper)
    t.start()
    return t


debug = False
runOnce = True

runBot()
if not runOnce:
    setInterval(runBot, 60*60*5)        #runs every 5 hours