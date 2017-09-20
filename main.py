from feedparser import parse, registerDateHandler
from sched import scheduler
from time import time, sleep
from re import sub, findall, split
from time import strptime, strftime
from urllib import request, parse as urlParser
from logging import basicConfig, info, critical, error, getLogger
from configparser import ConfigParser


# Запрос ленты новостей
def get_post():
    registerDateHandler(parse_date)
    feed = parse("http://rus.vrw.ru/feed")
    if feed.status != 200:
        error(u'Error. HTTP is not 200. Quit.')
        quit()
    else:
        return feed


# Проверка даты новости
def check(last_date, new_date, config):
    if parse_date(last_date) >= new_date:
        info(u'Новость старая')
        return False
    elif parse_date(last_date) <= new_date:
        info(u'Новость новая')
        config['BOT']['LastDate'] = strftime('%a, %d %b %Y %H:%M:%S %z', new_date)
        with open('good_news.cfg', 'w') as configfile:
            config.write(configfile)
        return True
    else:
        critical(u'Error. Quit')
        quit()
        return -1


# Отправка сообщения
def post_message(item, bot_token, chat_id):

    # Формирование текста сообщения
    text = "[" + modifikator(item.title) + "](" + item.link + ")" + "\n\n"\
           + modifikator(item.description)
    if hasattr(item, 'category'):
        text = text + '\n' + cat_to_hashtag(item.category)
    # Формирование url'a запроса
    url = 'https://api.telegram.org/bot' + bot_token + '%2FsendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' +\
            urlParser.quote_plus(text)

    newRequest = request.Request(url,method='POST')
    newRequest.host = 'api.telegram.org'
    response = request.urlopen(newRequest)

    if response.getcode() != 200:
        critical(u'Запрос не смог. Код ответа: ', response.status_code, '. Программа остановлена.')
        quit()
    return


# Очистка текста от html-тэгов и замена ascii-кодов на ascii-символы
def modifikator(text):
    modified_text = sub(r'(<.?([a-z][a-z0-9]*)\b[^>]*>)|Читать полностью »|Обсудить|\s{2,}', '', text)
    modified_text = modified_text.replace('\n', '\n\n')
    match = findall(r'(?<=&#)[0-9]+(?=;)', modified_text)
    for each in match:
        modified_text = modified_text.replace(r'&#' + each + r';', chr(int(each)))
    return modified_text.rstrip()


# Превращение списка категорий в список хэштэгов
def cat_to_hashtag(category):
    series = split(', ', category)
    hashtag_list = ''
    for sub_str in series:
        if bool(hashtag_list):
            hashtag_list = hashtag_list + ', '
        hashtag_list = hashtag_list + "#" + str.replace(sub_str.title(), ' ', '')
    return hashtag_list


# Превращение строки с датой в дату
def parse_date(str_date):
    try:
        return strptime(str_date, '%a, %d %b %Y %H:%M:%S %z')
    except ValueError:
        critical(u'Wrong date format.')
        quit()


# Прослушивание rss-фида и отправка новых новостей в канал
def listen():
    feed = get_post()
    for item in reversed(feed.entries):
        if check(config['BOT']['LastDate'], item.published_parsed, config):
            post_message(item, config['BOT']['Token'],
                               config['BOT']['ChatId'])
            info(u'Post sent')
            sleep(30*60)
    return

if __name__ == '__main__':
    # Чтение конфигурации
    config = ConfigParser()
    try:
        config.read('good_news.cfg')
    except FileNotFoundError:
        print(u'Configuration file (good_news.cfg) not found')
        quit()
    # Запуск логгера
    basicConfig(format=u'%(levelname)-3s [%(asctime)s] |%(module)s|  %(message)s',
                filename=config['LOG']['Path'],
                level=config['LOG']['Level'])
    log = getLogger(u'Good News Bot')
    info(u'Bot has been started.')

    loop = scheduler(time, sleep)
    loop.enter(1, 1, listen(), (*[loop, 0], ))
