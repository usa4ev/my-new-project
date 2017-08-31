from feedparser import parse
from sched import scheduler
from time import time, sleep
from re import sub, findall
from datetime import datetime
from requests import post


def check(sc, i):
    bot_name = ''
    token = ''
    state = datetime.strftime(datetime.today(), '%c') + ' Итерация:' + str(i)
    feed = parse("http://rus.vrw.ru/feed")
    new_date = feed['channel'].published
    new_date = parse_date(new_date)
    with open('my_file.txt') as f:
        last_date = f.read()
        if bool(last_date):
            last_date = datetime.strptime(last_date, '%c %z')
            if new_date <= last_date:
                print(state, '- Нет обновлений...')
                wait(sc, i)
                return
        else:
            with open('my_file.txt', 'w') as f:
                f.write(datetime.strftime(new_date, '%c %z'))
    for item in feed.entries:
        text = "_" + item.category + "_\n\n" \
               "["+modifikator(item.title)+"]("+item.link+")" + "\n\n" \
               "" + modifikator(item.description)
        post("https://api.telegram.org/bot" + bot_name + ":" + token + '/sendMessage?chat_id=@good_news_everybody'
                                                                       '&parse_mode=Markdown&text=' + text)
        sleep(1)
    print(state, '- Публикация обновлена!\n', 'Дата публикации: ' + datetime.strftime(new_date, '%c'))
    wait(sc, i)


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


def parse_date(str_date):
    return datetime.strptime(str_date, '%a, %d %b %Y %H:%M:%S %z')


if __name__ == '__main__':
    print("running...")
    s = scheduler(time, sleep)
    s.enter(1, 1, check, (*[s, 0], ))
    s.run()
