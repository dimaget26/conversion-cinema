import pandas as pd
import numpy  as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


np.random.seed(42)

#Таблица с пользователями магазина
users = []
for user_id in range(1, 2001): #Создаем список 2000 пользователей
    reg_date = datetime(2026,2,1) + timedelta(days=np.random.randint(0,29)) #Создание переменной по дате регистрации пользователя на сайте (1-28 число месяца)
    device = np.random.choice(['iOS', 'Android', 'Web'], p=[0.3, 0.6, 0.1]) # random.choice выбирает рандомный элемент из списка, где p= это вероятность сколько чего в процентах (то есть WEB меньше вмего, чаще всего заходят через телефон)
    users.append([user_id, reg_date, device])

df_users = pd.DataFrame(users, columns=['user_id', 'reg_date', 'device']) #Создание датафрейма на основе колонок, которые были созданы
print(df_users.head()) #Первичный обзор нашей таблицы
#print(df_users.isnull().sum()) #Проверка на пропуски (пропусков нет)

#Создание событий пользователей
events = []
for user_id in range(1, 2001): #Проход по каждому пользователю
    device = df_users[df_users['user_id'] == user_id]['device'].values[0]
    steps = ['cinema_open', 'trailer_watch', 'price_page', 'to_payment'] #4 шага воронки, где начинается все с захода на страница, оканчивая оплатой фильма
    num_steps = 1 #Каждый пользователь сделал минимум 1 действие (открыл приложение)
    if np.random.random() > 0.2: # Отсеиваем кол-во людей до 2 стадии
        num_steps = 2 #80% пользователей дошло до 2 шага (просмотр трейлера)
    if np.random.random() > 0.5 and num_steps >= 2:
        num_steps = 3  #Здесь делаем так, что половина отсмотревших трейлер перешло дальше к 3 шагу (переход к ценам)
    if device == 'Web' and num_steps >= 3:
        if np.random.random() > 0.95:  # 5% успеха
            num_steps = 4
        else:
            num_steps = 3
        # Только 5% Web-пользователей доходят до оплаты (вместо обычных 20%)  # 5% конверсии
    elif num_steps >= 3:
        if np.random.random() > 0.8:
            num_steps = 4 #20% дошедших до цены начинают оплату
        else:
            num_steps = 3

    event_times = []
    for i in range(num_steps): #Добавляем время событий каждого шага по воронке
        if i == 0:
            time_offset = np.random.randint(1, 60)
        else:
            time_offset = event_times[-1] + np.random.randint(1, 60)

        event_time = reg_date + timedelta(minutes=time_offset)
        event_times.append(time_offset)
        events.append([user_id, steps[i], event_time])

df_events = pd.DataFrame(events, columns=['user_id', 'step', 'event_time'])

print(df_events.head()) #Просмотр таблицы с событиями
# print(df_events.isnull().sum()) #Проверка на генерацию, нет ли пропусков в таблице

funnel = df_events.groupby('step')['user_id'].nunique().sort_values(ascending=False)
#Делаем переменную с воронкой по каждому шагу события по каждому пользователю, где смотрим как все развивалось

print(f'Всего пользователей - {df_users["user_id"].nunique()}')

print('\nВоронка:')
for i in range(len(funnel)-1):
    step1 = funnel.iloc[i]
    step2 = funnel.iloc[i+1]
    conv = step2 / step1 * 100  if step1 > 0 else 0
    print(f'{funnel.index[i]} → {funnel.index[i+1]}: {conv:.1f}% ')


df_merge = df_users.merge(df_events, on='user_id')
funnel_by_device = df_merge.groupby(['device', 'step'])['user_id'].nunique()
print(funnel_by_device)

#Графики по конверсии каждого дейвайса
show_android = funnel_by_device['Android'].sort_values(ascending=False).plot(kind='bar')
plt.title('Воронка по пользователям Android')
plt.grid(True, alpha=0.3)
plt.show()

show_iOS = funnel_by_device['iOS'].sort_values(ascending=False).plot(kind='bar')
plt.title('Воронка по пользователям iOS')
plt.grid(True, alpha=0.3)
plt.show()

show_Web = funnel_by_device['Web'].sort_values(ascending=False).plot(kind='bar')
plt.title('Воронка по пользователям Web')
plt.grid(True, alpha=0.3)
plt.show()

print('=' * 100)
print(f'Конверсии по каждому устройству:')
#Считаем конверсию по iOS
users_open_iOS = funnel_by_device.loc[('iOS', 'cinema_open')]
users_payment_iOS = funnel_by_device.loc[('iOS', 'to_payment')]
conv_iOS = users_payment_iOS / users_open_iOS * 100 if users_open_iOS > 0 else 0
print(f'🎯Конверсия iOS : {conv_iOS:.2f}%')

#Считаем конверсию по Android
users_open_android = funnel_by_device.loc[('Android', 'cinema_open')]
users_payment_android = funnel_by_device.loc[('Android', 'to_payment')]
conv_android = users_payment_android / users_open_android * 100 if users_open_android > 0 else 0
print(f'🎯Конверсия Android : {conv_android:.2f}%')

#Считаем конверсию по Web
users_open_web = funnel_by_device.loc[('Web', 'cinema_open')]
users_payment_web = funnel_by_device.loc[('Web', 'to_payment')]
conv_web = users_payment_web / users_open_web * 100 if users_open_web > 0 else 0
print(f'🔴Конверсия Web : {conv_web:.2f}%')


#Соединяем все три конверсии для визуальной картины
steps = ['Открыли \nприложение', 'Посмотрели \nтрейлер', 'Увидели \nцены', 'Начали \nоплату']
#Берем значение по каждой воронке типов устройств
iOS_conv = [577, 471, 233, 46]
android_conv = [1234, 968, 482, 97]
web_conv = [189, 144, 62, 2]
#График для визуализации конверсий
plt.plot(steps, iOS_conv, label='iOS', color='blue', linewidth=2, marker='o')
plt.plot(steps, android_conv, label='Android', color='red', linewidth=2, marker='x')
plt.plot(steps, web_conv, label='Web', color='green', linewidth=2, marker='v')
plt.xlabel('Шаг воронки', fontsize=12)
plt.ylabel('Количество пользователей', fontsize=12)
plt.title('Воронка продаж по типам устройств', fontsize=16)
plt.legend()
plt.grid(True, alpha=0.3)
plt.annotate('Провал на Web!\nПроверить платежную форму', xy=(steps[-1], iOS_conv[-1]), xytext=(steps[-1], iOS_conv[-1]), color='red', fontsize=8)
plt.tight_layout()
plt.savefig('funnel_analysis.png', dpi=150)
plt.show()


#Добавим выводы и рекомендации по бизнесу

print('=' * 100)
print('✅Выводы по проекту:')
print('1. 👑Большее количество пользователей Кино-онлайн используют мобильную версию, чем веб-браузер')
print('2. 🔥На iOS и Android % конверсии практически одинаковый, что говорит от том, что вкладываться в продвижение можно в оба типа устройств')
print('3. 🚨Основная и критическая проблема в Web-пользователях, где конверсия чуть больше 1%, а также основное кол-во пользователей "отваливаются" на этапе перехода к покупке')
print('=' * 100)
print('💡Рекомендации по бизнесу')
print('🔧В первую очередь проверить способ оплаты в Web браузерах, где может возникать ошибка')
print('💳Добавить какие-то альтернативные способы оплаты на Web, например через СБП или по QR-коду')
print('🎯Провести скидку при оплате через мобильное приложение Android, iOS')


#Перенос общей таблицы в csv-файл для дашбордов
df_merge.to_csv('funnel_analysis.csv', index=False)