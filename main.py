from feedparser import parse
from sched import scheduler
from time import time, sleep
from re import sub, findall
from datetime.datetime import _strptime
from requests import post
import logging
import configparser


# Запрос ленты новостей
def get_post():
    feed = parse("http://rus.vrw.ru/feed")
    return feed


# Проверка даты новости
def check(last_date, new_date):
    if parse_date(last_date) >= parse_date(new_date):
        logging.info(u'Новость старая')
        return False
    elif parse_date(last_date) <= parse_date(new_date):
        logging.info(u'Новость новая')
        return new_date, True
    else:
        logging.critical(u'Какой-то пиздец в проверке. Лучше прилягу.')
        quit()
        return -1


# Отправка сообщения
def post_message(item, bot_name, bot_token):
    req_base = "https://api.telegram.org/bot"
    req_method = '/sendMessage?'
    req_params = 'chat_id='
    req_text = ''
    request = req_base + bot_name + bot_token + req_method + req_params + req_text
    response = post(request)
    return


# Очистка текста от html-тэгов и замена ascii-кодов на ascii-символы
def modifikator(text):
    modified_text = sub(r'(<.?([a-z][a-z0-9]*)\b[^>]*>)|Читать полностью »|Обсудить|\s{2,}', '', text)
    modified_text = modified_text.replace('\n', '\n\n')
    match = findall(r'(?<=&#)[0-9]+(?=;)', modified_text)
    for each in match:
        modified_text = modified_text.replace(r'&#' + each + r';', chr(int(each)))
    return modified_text


def wait(sc, i):
    i = i + 1
    s.enter(30 * 60, 1, check, (*[sc, i],))


# Превращение строки с датой в дату
def parse_date(str_date):
    return _strptime(str_date, '%a, %d %b %Y %H:%M:%S %z')


if __name__ == '__main__':
    # Запуск логгера
    logging.basicConfig(format=u'%(levelname)-3s [%(asctime)s]  %(message)s',
                        filename='good_news.log', level=logging.DEBUG)
    logging.info(u'Бот запущен')
    # Чтение конфигурации
    config = configparser.ConfigParser()
    config.read('good_news.cfg')


    s = scheduler(time, sleep)
    s.enter(1, 1, check, (*[s, 0], ))
    s.run()
