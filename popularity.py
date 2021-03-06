import urllib2
import json
import time
import os
from optparse import OptionParser
from collections import Counter

parser = OptionParser()
parser.add_option("-c", "--config", dest="config",
                  help="load configuration from FILE", metavar="FILE")
(options, args) = parser.parse_args()

if len(args) != 1:
    parser.error("Config file needed")

# Read in config info
configFile = open(args[0])
config = json.load(configFile)


# Simplified page loading function
def loadPage(url):
    print 'Scraping ' + url

    header = {'User-Agent': config['userAgent']}
    request = urllib2.Request(url, None, header)

    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        print "Encountered a HTTP Error: " + str(e.code)

        if (e.code >= 500 and e.code < 600):
            # 5xx server errors may still be recoverable, so we try again later
            time.sleep(config['errorTimeout'])
            return loadPage(url)

        else:
            # All other errors are assumed to be not recoverable,
            # so we return false and let the caller deal with it
            return False

    except urllib2.URLError as e:
        print "Failed to reach server ", e.reason
        return False
    else:
        return response.read()


# Initiate scrapping process - get subreddit post list
def scrapeItems(recurse, after=False):
    # This function will recurse to grab the next page
    url = (config['baseUrl'] + config['subreddit'] + config['urlPostfix']
            + '?limit=' + str(config['postLimit']))

    if after:
        url = url + '&after=' + after

    page = loadPage(url)

    if not page:
        # Something went terribly wrong there.
        # We still have to keep going through, since we can't miss a page
        time.sleep(config['errorTimeout'])
        scrapeItems(recurse, after)
    else:
        pageData = json.loads(page)
        items = pageData['data']['children']

        for item in items:
            # Sleep on each item to not trip reddit's rate limiting
            time.sleep(config['itemTimeout'])
            itemUrl = (config['baseUrl'] + item['data']['permalink']
                + config['urlPostfix'])

            try:
                scrapeItem(itemUrl)
            except Exception as e:
                print e
                time.sleep(config['errorTimeout'])

            with open(config['rawDataFile'], 'w+') as fp:
                fp.write(json.dumps(data))

        # Fetch the next page if there are more pages
        if recurse + 1 < config['pages']:
            scrapeItems(recurse + 1, pageData['data']['after'])


def scrapeItem(url):
    page = loadPage(url)

    if page:
        pageData = json.loads(page)

        for item in pageData:
            processListing(item['data']['children'])

    # If the post didn't load we'll just let it go, unlike in scrapeItems


def processListing(listing):
    for item in listing:
        pageData = item['data']

        if 'author' in pageData:
            addFlair(pageData['author'], pageData[config['flairProp']])

        if 'replies' in pageData and isinstance(pageData['replies'], dict):
            processListing(pageData['replies']['data']['children'])


def addFlair(username, flair):
    if not flair:
        flair = config['nonePlaceholder']

    data[username] = flair


def collateData(data):
    return Counter(data.itervalues())


# Start by importing existing data from the data file
if os.path.exists(config['rawDataFile']):
    with open(config['rawDataFile']) as fp:
        try:
            data = json.load(fp)
        except ValueError as e:
            # If the file is empty a ValueError will be raised
            data = {}
else:
    data = {}

print ('Script Begin ',
    time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))

try:
    scrapeItems(0)

    collated = collateData(data)
    with open(config['collatedDataFile'], 'w+') as fp:
        result = {
            'data': collated,
            'updated': time.time()
        }

        fp.write(json.dumps(result))

except Exception as e:
    print e

print ('Script End ',
    time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))
