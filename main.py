import feedparser as rssparser
import sched, time, re
import telegram as telega
from datetime import datetime


def check(sc, i):

    state = datetime.strftime(datetime.today(), '%c') + ' Итерация:' + str(i)

    feed = rssparser.parse("http://rus.vrw.ru/feed")
    newdate = feed['channel'].published
    newdate = parsedate(newdate)

    with open('my_file.txt') as f:
        lastdate = f.read()
        dateisfilled = bool(lastdate)

        if dateisfilled:
            lastdate = datetime.strptime(lastdate, '%c %z')

            if newdate <= lastdate:
                print(state, '- Нет обновлений...')
                wait(sc, i)
                return
        else:
            with open('my_file.txt', 'w') as f:
                f.write(datetime.strftime(newdate, '%c %z'))

    bot = telega.Bot("306948333:AAFDFNVKV0psTSR497_9sHhpJY3dZz9dcyA")

    for item in feed.entries:
        text = "_" + item.category + "_\n\n" \
               "["+modifikator(item.title)+"]("+item.link+")" + "\n\n" \
               "" + modifikator(item.description)
        # +"["+item.title+"]("+item.link+")"

        bot.sendMessage("@good_news_everybody", text, parse_mode="Markdown", disable_web_page_preview=False, timeout=5)
        time.sleep(1)

    print(state, '- Публикация обновлена!\r\n', 'Дата публикации: ' + datetime.strftime(newdate, '%c'))
    wait(sc, i)


def modifikator(text):
    modified_text = re.sub(r'(<.?([a-z][a-z0-9]*)\b[^>]*>)|Читать полностью »|Обсудить|\s{2,}', '', text)
    modified_text = modified_text.replace('\n', '\n\n')
    match = re.findall(r'(?<=&#)[0-9]+(?=;)', modified_text)
    for each in match:
        modified_text = modified_text.replace(r'&#' + each + r';', chr(int(each)))
    return modified_text


def wait(sc, i):
    i = i + 1
    s.enter(30 * 60, 1, check, (*[sc, i],))


def parsedate(strdate):
    return datetime.strptime(strdate, '%a, %d %b %Y %H:%M:%S %z')


if __name__ == '__main__':
    print("running...")

    s = sched.scheduler(time.time, time.sleep)
    s.enter(1, 1, check, (*[s, 0], ))
    s.run()

