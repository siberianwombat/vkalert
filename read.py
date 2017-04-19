import time
import ConfigParser
import vk_api
import datetime
import sys
import md5
import json
import requests
import os
import argparse

# @todo: check if storage path exists
def checkCache(md5hash, path, debug):
    if (debug):
        print "checkCache: %s/%s" % (path, md5hash)
    return os.path.exists(path + '/' + md5hash)

def storeCache(md5hash, text, path, debug):
    if (debug):
        print ('storeCache: %s/%s' % (path, md5hash))
    fname = path + '/' + md5hash
    fhandle = open(fname, 'a')
    try:
        os.utime(fname, None)
    finally:
        fhandle.close()
    return True;    

def slackNotify(text, config, debug):
    slack_data = {'text': text, 'channel': config.get('slack', 'channel'), 'username': config.get('slack', 'username'), 'icon_emoji': ':scream_cat:' }
    response = requests.post(
        config.get('slack', 'webhook_url'), data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
                'Request to slack returned an error %s, the response is:%s'
                % (response.status_code, response.text)
            )
    if (debug):
        print ('slack: sent')
    return True;

def checkUpdateCacheNotify(text, path, config, debug):
    md5hash = md5.new(text).hexdigest()
    if (not checkCache(md5hash, path, debug)):
        if slackNotify(text, config, debug  ):
            if (debug):
                print ('slack: notifying')
            storeCache(md5hash, text, path, debug)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.set_defaults(debug=False)
    args = parser.parse_args()

    if (args.debug):
        print ('start');
    
    reload(sys)
    sys.setdefaultencoding('utf8')
    config = ConfigParser.ConfigParser()

    # @todo add defaults
    config.read([os.path.dirname(__file__) + '/vkalert.cfg'])
    triggerWords = config.get('trigger', 'keywords').split(',')
    storagePath = config.get('cache', 'storage')
    
    vkLogin = config.get('vk', 'login')
    vkPassword = config.get('vk', 'password')
    
    vk_session = vk_api.VkApi(login = vkLogin, password = vkPassword)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print('vk error: %s' % error_msg)
        return

    if (args.debug):
        print ('vk: logged in');

    vk = vk_session.get_api()

    wall = vk.newsfeed.get(count = config.getint('vk', 'count'), filters = 'post')

    for wallItem in wall['items']:
        text = wallItem.get('text').lower()
        for triggerWord in triggerWords:
            if text.find(triggerWord)>-1:
                if (args.debug):
                    print ('date: %s' % datetime.datetime.fromtimestamp(int(wallItem.get('date'))).strftime('%Y-%m-%d %H:%M:%S'))
                    print ('post: %s \n' % wallItem.get('text').encode('utf-8'))
                checkUpdateCacheNotify(wallItem.get('text'), storagePath, config, args.debug)                
                break

    if (args.debug):
        print ('done');
        
if __name__ == '__main__':
    main()
