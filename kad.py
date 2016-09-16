from bs4 import BeautifulSoup
from clint.textui import progress
import argparse
import base64
import cfscrape
import requests

parser = argparse.ArgumentParser(description='Given 1 episode URL, download all in the season')
parser.add_argument('--url', help='Specify an episode URL')
parser.add_argument('--path', default='./', help='Specify a download path (defaults to ./)')

args = parser.parse_args()

session = requests.session()
scraper = cfscrape.create_scraper(sess=session)

def getEpisodeSoup(url):
    episodeRequest = scraper.get(url)
    episodeSoup = BeautifulSoup(episodeRequest.content, 'html.parser')
    
    return episodeSoup

def getEpisodeList(episodeSoup):
    episodeList = []
    episodeOptions = episodeSoup.find(id='selectEpisode').findAll('option')

    for ep in episodeOptions:
        episodeList.append(ep['value'])

    return episodeList

def getURL(episodeSoup):
    return base64.b64decode(episodeSoup.find(id='selectQuality').findAll('option')[0]['value'])

def getFilename(episodeSoup):
    return episodeSoup.find(id='divFileName').contents[2].strip()

def downloadFile(episodeURL, filename):
    episodeDownload = requests.get(episodeURL, stream=True)
    path = '%s/%s.mp4' % (args.path, filename)

    print('Downloading %s ...' % filename)

    with open(path, 'wb') as f:
        total_length = int(episodeDownload.headers.get('content-length'))
        for chunk in progress.bar(episodeDownload.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
            if chunk:
                f.write(chunk)
                f.flush()

    print('Done.')

def main(url):
    rootURL = url.rsplit('/', 1)[0]

    episodeSoup = getEpisodeSoup(url)
    episodeList = getEpisodeList(episodeSoup)

    for episode in episodeList:
        epSoup = getEpisodeSoup('%s/%s' % (rootURL, episode))
        downloadFile(getURL(epSoup), getFilename(epSoup))

if __name__ == "__main__":
    if args.url is None:
        print('No --url provided. See --help for more information.')
        exit()
    else:
        main(args.url)