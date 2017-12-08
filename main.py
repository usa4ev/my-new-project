# -*- coding: utf-8 -*-
"""
Good news telegram bot.
It takes rss fedd from http://rus.vrw.ru/feed, parse it and send to telegram channel
"""

from time import time, sleep, strptime
from sched import scheduler
from re import sub, findall, split
from configparser import ConfigParser
from logging import basicConfig, info, critical, error, getLogger
from requests import post
from feedparser import parse


def get_post():
    """ Request news feed """
    feed = parse("http://rus.vrw.ru/feed")
    if feed.status != 200:
        error(u'Error. HTTP is not 200. Quit.')
        quit()
    else:
        return feed


def check(last_date, new_date, conf):
    """ Check news date """
    if parse_date(last_date) >= parse_date(new_date):
        info(u'Post is old.')
        return False
    elif parse_date(last_date) <= parse_date(new_date):
        info(u'Post is new.')
        conf['BOT']['LastDate'] = str(new_date)
        with open('good_news.cfg', 'w') as configfile:
            conf.write(configfile)
        return True
    else:
        critical(u'Error. Quit')
        quit()
        return -1


def post_message(item, bot_name, bot_token, chat_id):
    """ Send message to channel """
    text = "[" + modifikator(item.title) + "](" + item.link + ")" + "\n\n"\
           + modifikator(item.description)
    if hasattr(item, 'category'):
        text = text + cat_to_hashtag(item.category)
    request = 'https://api.telegram.org/bot' + bot_name + ':' + bot_token + \
              '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + text
    post(request)
    return


def modifikator(text):
    """ To clean text and replace ascii-codes with ascii-symbols"""
    modified_text = sub(r'(<.?([a-z][a-z0-9]*)\b[^>]*>)|Читать полностью »|Обсудить|\s{2,}', '', text)
    modified_text = modified_text.replace('\n', '\n\n')
    match = findall(r'(?<=&#)[0-9]+(?=;)', modified_text)
    for each in match:
        modified_text = modified_text.replace(r'&#' + each + r';', chr(int(each)))
    return modified_text


def cat_to_hashtag(category):
    """ Makes list of hashtags from list of categories and return it. """
    series = split(', ', category)
    hashtag_list = ''
    for sub_str in series:
        if bool(hashtag_list):
            hashtag_list = hashtag_list + ', '
        hashtag_list = hashtag_list + "#" + str.replace(sub_str.title(), ' ', '')
    return hashtag_list


def parse_date(str_date):
    """ Type adduction. From string to date. """
    try:
        return strptime(str_date, '%a, %d %b %Y %H:%M:%S %z')
    except ValueError:
        critical(u'Wrong date format.')
        quit()


def listen():
    """ Listen to rss and send messages to channel """
    feed = get_post()
    for item in reversed(feed.entries):
        if check(bot_conf['BOT']['LastDate'], item.published, bot_conf):
            post_message(item, bot_conf['BOT']['Name'],
                         bot_conf['BOT']['Token'],
                         bot_conf['BOT']['ChatId'])
            info(u'Post sent')
            sleep(30)
    return

if __name__ == '__main__':
    bot_conf = ConfigParser()
    try:
        bot_conf.read('good_news.cfg')
    except FileNotFoundError:
        print(u'Configuration file (good_news.cfg) not found')
        quit()
    basicConfig(format=u'%(levelname)-3s [%(asctime)s] |%(module)s|  %(message)s',
                filename=bot_conf['LOG']['Path'],
                level=bot_conf['LOG']['Level'])
    log = getLogger(u'Good News Bot')
    info(u'Bot has been started.')

    loop = scheduler(time, sleep)
    loop.enter(180, 1, listen(), (*[loop, 0], ))
