import telebot
import os.path
import random
import datetime
from telebot import types
from config import *
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    database = DB('lections.db')
    userlist1 = database.get_users('users')
    userlist2 = database.get_users('users_video')
    if message.chat.id not in userlist1:
        database.new_user(int(message.chat.id), 'users')
    if message.chat.id not in userlist2:
        database.new_user(int(message.chat.id), 'users_video')
    database.close()
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text='➡', callback_data='0lesson')
    keyboard.add(btn)
    bot.send_message(message.chat .id, 'Привет, {0.first_name}! ✋\nЯ - <b>{1.first_name}</b>, бот для изучения ква'
                                      'нтовой физики!'.format(message.from_user, bot.get_me()), parse_mode='html')
    bot.send_message(message.chat.id, 'В моей базе есть множество лекций, как в видеоформате🎞, так и в текстовом📖.\n ')
    bot.send_message(message.chat.id, 'Любую лекцию можно скачать и изучать в удобное время!🕔', reply_markup=keyboard)

def zero_lesson(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text='Перейти к уроку', callback_data='lesson_start_0_0')
    keyboard.add(btn)
    bot.send_message(message.chat.id, 'Для начала давайте пройдем вводный урок!\nВ нём я расскажу что из себя представляет квантовая физика.')
    bot.send_message(message.chat.id, 'После его прохождения вы сможешь выбрать интересующую тему и изучать её.', reply_markup=keyboard)

def lesson_video(message, type, folder, num):
    keyboard = types.InlineKeyboardMarkup()
    path = '.\{0}\{1}'.format(type, current_theme)
    num_files = len([f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))])
    database = DB('lections.db')
    column = '_'.join(folder.split(' '))
    database.insert_value(column, num, message.chat.id, 'users_video')
    video = open('{0}\{1}\lesson_{2}.mp4'.format(type, folder, num), 'rb')
    markup = types.InlineKeyboardMarkup()
    if num != num_files:
        next = types.InlineKeyboardButton(text='Перейти к уроку {}'.format(num+1), callback_data='video_lesson_{}'.format(num+1))
        markup.add(next)
    bot.send_message(message.chat.id, 'Подождите немного! Видео загружается на сервера Telegram.')
    bot.send_video(message.chat.id, video, caption='Урок {}'.format(num), reply_markup=markup)
    if num == num_files:
        keyboard.add(types.InlineKeyboardButton(text='Меню', callback_data='menu'))
        bot.send_message(message.chat.id, 'Это был последний урок данной темы!', reply_markup=keyboard)
    database.close()

def lesson(message, ctype, folder, num, i):
    i = int(i)
    j = int(i) + 2
    doc = Doc('{0}\{1}\lesson_{2}\doc.docx'.format(ctype, folder, num))
    doc2 = open('{0}\{1}\lesson_{2}\doc2.docx'.format(ctype, folder, num), 'rb')
    keyboard = types.InlineKeyboardMarkup()
    if i == 0 and num != 0:
        bot.send_document(message.chat.id, doc2, caption='Скачать лекцию.')
    while int(i) < j:
        if i == doc.count_paragraphs():
            if num == 0:
                btn = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
                keyboard.add(btn)
                bot.send_message(message.chat.id, 'Теперь вы можете заниматься тем, что вам интересно!', reply_markup=keyboard)
                break
            else:
                database = DB('lections.db')
                column = '_'.join(folder.split(' '))
                database.insert_value(column, num, message.chat.id, 'users')
                database.close()
                if num == len(os.listdir('.\{0}\{1}'.format(ctype, folder))):
                    keyboard.add(types.InlineKeyboardButton(text='Меню', callback_data='menu'))
                    bot.send_message(message.chat.id, 'Это был последний урок данной темы!', reply_markup=keyboard)
                else:
                    btn = types.InlineKeyboardButton(text='Урок {}'.format(num+1), callback_data='lesson_start_{0}_0'.format(num+1))
                    keyboard.add(btn)
                    bot.send_message(message.chat.id, 'Перейти к следующему уроку?', reply_markup=keyboard)
                break
        elif 'Image_ID' in doc.get_paragraph_text(i):
            photo_id = doc.get_paragraph_text(i).split('_')[1]
            photo_text = doc.get_paragraph_text(i).split('_')[2]
            photo = open('{0}\{1}\lesson_{2}\{3}.jpg'.format(ctype, folder, num, photo_id), 'br')
            bot.send_photo(message.chat.id, photo, caption=photo_text)
            i += 1
            continue
        else:
            bot.send_message(message.chat.id, doc.get_paragraph_text(i))
            i += 1
            if i == doc.count_paragraphs():
                bot.send_message(message.chat.id, 'Поздравляем, вы прошли урок!')
                if num == 0:
                    btn = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
                    keyboard.add(btn)
                    bot.send_message(message.chat.id, 'Теперь вы можете заниматься тем, что вам интересно!',
                                     reply_markup=keyboard)
                    break

    if i < doc.count_paragraphs():
        btn = types.InlineKeyboardButton(text='➡', callback_data='lesson_start_{0}_{1}'.format(num, i+1))
        keyboard.add(btn)
        bot.send_message(message.chat.id, doc.get_paragraph_text(i), reply_markup=keyboard)

def pick_theme(message):
    keyb = telebot.types.ReplyKeyboardMarkup(True, False)
    keyb.row('Квантовая криптография', 'Квантовая механика')
    keyb.row('Квантовая теория поля', 'Квантовая оптика')
    choose_theme = bot.send_message(message.chat.id, 'Теперь выбери тему!', reply_markup=keyb)
    bot.register_next_step_handler(choose_theme, pick_type)

def pick(message):
    keyb = telebot.types.ReplyKeyboardMarkup(True, False)
    keyb.row('Текст', 'Видео')
    choose_type = bot.send_message(message.chat.id, 'Отлично! Теперь выбери выбери предпочтительный формат!',
                                   reply_markup=keyb)
    bot.register_next_step_handler(choose_type, pick_lection)

def pick_type(message):
    global current_theme
    themes = ['Квантовая механика', 'Квантовая теория поля', 'Квантовая криптография', 'Квантовая оптика']
    if message.text not in themes:
        do = funcs(message)
        if do == 2:
            words(message)
            pick_theme(message)
    else:
        current_theme = message.text
        pick(message)

def pick_lection(message):
    global lectlist
    alltypes = ['Текст', 'Видео']
    if message.text not in alltypes:
        do = funcs(message)
        if do == 2:
            words(message)
            pick(message)
    else:
        current_type = message.text
        markup = types.InlineKeyboardMarkup()
        database = DB('lections.db')
        column = '_'.join(current_theme.split(' '))
        if current_type == 'Текст':
            les = database.get_value(column, message.chat.id, 'users')
            for i in range(les[0]+1):
                if i != len(os.listdir('.\{0}\{1}'.format(current_type, current_theme))):
                    markup.add(types.InlineKeyboardButton(text='Урок {}'.format(i+1), callback_data='lesson_start_{0}_0'.format(i+1)))
            bot.send_message(message.chat.id, 'Количество пройденных уроков по теме: {}'.format(les[0]), reply_markup=markup)
        else:
            les = database.get_value(column, message.chat.id, 'users_video')
            keyboard = types.InlineKeyboardMarkup()
            path = '.\{0}\{1}'.format(current_type, current_theme)
            num_files = len([f for f in os.listdir(path)
                             if os.path.isfile(os.path.join(path, f))])
            for i in range(les[0] + 1):
                if i != num_files:
                    keyboard.add(types.InlineKeyboardButton(text='Урок {}'.format(i + 1), callback_data='video_lesson_{0}'.format(i + 1)))
            bot.send_message(message.chat.id, 'Количество пройденных уроков по теме: {}'.format(les[0]), reply_markup=keyboard)
        database.close()

@bot.message_handler(commands=['menu'])
def menu(message):
    menu_markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Учиться', callback_data='themes')
    btn2 = types.InlineKeyboardButton(text='Тест', callback_data='test')
    btn3 = types.InlineKeyboardButton(text='Статистика', callback_data='stat')
    menu_markup.add(btn1, btn2)
    menu_markup.add(btn3)
    bot.send_message(message.chat.id, 'Это меню. Отсюда можно перейти к любой интерусющей деятельности.', reply_markup=menu_markup)

@bot.message_handler(commands=['test'])
def test(message):
    keyb = telebot.types.ReplyKeyboardMarkup(True, False)
    keyb.row('Новичок', 'Знаток', 'Профессор')
    bot.send_message(message.chat.id, 'Давай проверим насколько хорошо ты усвоил материал!')
    step=bot.send_message(message.chat.id, 'Выбери свой текущий уровень знаний.',  reply_markup=keyb)
    bot.register_next_step_handler(step, level)

def values(message):
    database = DB('lections.db')
    themes = ['Квантовая_механика', 'Квантовая_теория_поля', 'Квантовая_криптография', 'Квантовая_оптика']
    kvm_value = max(database.get_value(themes[0], message.chat.id, 'users'),
                    database.get_value(themes[0], message.chat.id, 'users_video'))
    kvtp_value = max(database.get_value(themes[1], message.chat.id, 'users'),
                     database.get_value(themes[1], message.chat.id, 'users_video'))
    kvkp_value = max(database.get_value(themes[2], message.chat.id, 'users'),
                     database.get_value(themes[2], message.chat.id, 'users_video'))
    kvo_value = max(database.get_value(themes[3], message.chat.id, 'users'),
                    database.get_value(themes[3], message.chat.id, 'users_video'))
    database.close()
    return kvm_value, kvtp_value, kvkp_value, kvo_value

def level(message):
    global testlist
    global answer
    answer = ''
    database = DB('lections.db')
    kvm_value, kvtp_value, kvkp_value, kvo_value = values(message)
    themes = ['Квантовая_механика','Квантовая_теория_поля','Квантовая_криптография','Квантовая_оптика']
    testlist = database.get_tests(themes[0], kvm_value[0])
    testlist += database.get_tests(themes[1], kvtp_value[0])
    testlist += database.get_tests(themes[2], kvkp_value[0])
    testlist += database.get_tests(themes[3], kvo_value[0])
    indexlist = []
    lenl = len(testlist)
    if message.text == 'Новичок':
        for i in range(lenl):
            if testlist[i][4] > 3:
                indexlist.append(i)
        z = 0
        for i in indexlist:
            del testlist[int(i) - z]
            z += 1
        do_test(message)
    elif message.text == 'Знаток':
        for i in range(lenl):
            if testlist[i][4] > 6 or testlist[i][4] < 4:
                indexlist.append(i)
        z = 0
        for i in indexlist:
            del testlist[int(i) - z]
            z += 1
        do_test(message)
    elif message.text == 'Профессор':
        for i in range(lenl):
            if testlist[i][4] < 7:
                indexlist.append(i)
        z=0
        for i in indexlist:
            del testlist[int(i)-z]
            z+=1
        do_test(message)
    else:
        do = funcs(message)
        if do == 2:
            step = bot.send_message(message.chat.id, 'Я не понимаю о чем вы. \nВыберите, пожалуйста, уровень.')
            bot.register_next_step_handler(step, level)

def do_test(message):
    global testlist
    global answer
    master = ['Новичок', 'Знаток', 'Профессор']
    do = funcs(message)
    if do == 2:
        if message.text == answer:
            bot.send_message(message.chat.id, 'Верно!')
        elif message.text in master:
            pass
        else:
            bot.send_message(message.chat.id, 'Неправильно!')
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Меню', callback_data='menu')
        btn2 = types.InlineKeyboardButton(text='Выбрать тему', callback_data='themes')
        markup.add(btn2, btn1)
        if testlist == [] and message.text in master:
            bot.send_message(message.chat.id, 'Вы выучили недостаточно материала для этого уровня.',
                             reply_markup=markup)
        elif testlist == [] and message.text not in master:
            bot.send_message(message.chat.id, 'Вы прошли все тесты данной сложности!',
                             reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(message.chat.id, 'Изучайте новый материал для появления новых вопросов.',
                             reply_markup=markup)
        else:
            keyboard = types.ReplyKeyboardMarkup(True, False)
            random.shuffle(testlist)
            answer = testlist[0][2].split('_')[0]
            answers = testlist[0][2].split('_')
            random.shuffle(answers)
            for i in range(2):
                keyboard.row(answers[i], answers[i + 2])
            step = bot.send_message(message.chat.id, testlist[0][1], reply_markup=keyboard)
            bot.register_next_step_handler(step, do_test)
            del testlist[0]


@bot.message_handler(commands=['statistics'])
def statistics(message):
    kvm, kvtp, kvkp, kvo = values(message)
    bot.send_message(message.chat.id, '<b>Статистика</b>\n'
                                      'Изучено уроков:\n'
                                      '•Квантовая механика: {0}\n'
                                      '•Квантовая оптика: {1}\n'
                                      '•Квантовая теория поля: {2}\n'
                                      '•Квантовая криптография: {3}'.format(kvm[0], kvo[0], kvtp[0], kvkp[0]), parse_mode='html')

@bot.callback_query_handler(func=lambda call:True)
def ans(call):
    global current_theme
    if call.data == 'menu':
        menu(call.message)
    if call.data == 'stat':
        statistics(call.message)
    if call.data == '0lesson':
        zero_lesson(call.message)
    if call.data == 'themes':
        pick_theme(call.message)
    if call.data == 'test':
        test(call.message)
    if 'lesson_start' in call.data:
        if 'lesson_start_0' in call.data:
            current_theme = 'zero'
        current_lesson = int(call.data.split('_')[2])
        current_par = int(call.data.split('_')[3])
        lesson(call.message, 'Текст', current_theme, current_lesson, current_par)
    if 'video_lesson' in call.data:
        current_lesson = int(call.data.split('_')[2])
        lesson_video(call.message, 'Видео', current_theme, current_lesson)

def funcs(message):
    if message.text == '/start':
        start_message(message)
    elif message.text == '/words':
        words(message)
    elif message.text == '/statistics':
        statistics(message)
    elif message.text == '/help':
        start_message(message)
    elif message.text == '/menu':
        menu(message)
    elif message.text == '/test':
        test(message)
    else:
        return 2
@bot.message_handler(content_types=['text'])
def words(message):
    bot.send_message(message.chat.id, 'Извините, но я не понимаю вас.')
    # if message.text == 'admin':
    #   bot.send_message(message.chat.id, message.chat.id)

if __name__ == '__main__':
    bot.polling(none_stop=True)