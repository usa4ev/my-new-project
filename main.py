from feedparser import parse
from sched import scheduler
from time import time, sleep
from re import sub, findall, split
from datetime import datetime
import telegram as telega

def check(sc, i):
    state = datetime.strftime(datetime.today(), '%c') + ' Итерация: ' + str(i)
    feed = parse("http://rus.vrw.ru/feed")
    new_date = parse_date(feed['channel'].published)
    with open('my_file.txt','r+') as f:
        last_date = f.read()
        if bool(last_date):
            check_pub_date = True
            last_date = datetime.strptime(last_date, '%c %z')
            if new_date <= last_date:
                print(state, '- Нет обновлений...')
                wait(sc, i)
                return
        else:
            check_pub_date = False

        f.write(datetime.strftime(new_date, '%c %z'))

    token = ""
    bot = telega.Bot(token)

    for item in reversed(feed.entries):
        pub_date = parse_date(item.published)

        if check_pub_date:
            if pub_date <= last_date:
                continue

        text = "[" + modifikator(item.title) + "](" + item.link + ")" + "\n\n"\
               '' + modifikator(item.description)

        if hasattr(item, 'category'):
            text = text + '\n\n' + cat_to_hashtag(item.category)

        bot.sendMessage("@good_news_everybody", text, parse_mode="Markdown", disable_web_page_preview=False, timeout=5)
        sleep(1)

    print(state, ' - Публикация обновлена!\n', 'Дата публикации: ', datetime.strftime(new_date, '%c'))
    wait(sc, i)


def cat_to_hashtag(category):
    lst = split(', ', category)
    result = ''
    for sub_str in lst:
        if bool(result):
            result = result + ', '
        result = result + "#" + str.replace(sub_str.title(), ' ', '')

    return result


def modifikator(text):
    modified_text = sub(r'(<.?([a-z][a-z0-9]*)\b[^>]*>)|Читать полностью »|Обсудить|\s{2,}', '', text)
    modified_text = modified_text.replace('\n', '\n\n')
    match = findall(r'(?<=&#)[0-9]+(?=;)', modified_text)
    for each in match:
        modified_text = modified_text.replace(r'&#' + each + r';', chr(int(each)))

    return modified_text.rstrip()


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
