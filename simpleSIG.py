import PySimpleGUI as sg
import os
import subprocess
import sys

#Проверка наличия ПО Крипто ПРО
if os.path.exists(r'C:\Program Files\Crypto Pro\CSP\csptest.exe'):
    cspp = r'C:\Program Files\Crypto Pro\CSP\csptest.exe'
    certp = 'C:\Program Files\Crypto Pro\CSP'
elif os.path.exists(r'C:\Program Files (x86)\Crypto Pro\CSP\csptest.exe'):
    cspp = r'C:\Program Files (x86)\Crypto Pro\CSP\csptest.exe'
    certp = 'C:\Program Files (x86)\Crypto Pro\CSP'
else:
    sg.Popup('Ошибка! Программное обеспечение Крипто ПРО не найдено.')
    sys.exit()

#Запуск программы
layout = [
    [sg.Text('Вставьте ключ с ЭЦП')],
    [sg.Submit('Запустить'), sg.Cancel('Отмена')]
]

window = sg.Window('Запуск программы', layout)
while True:
    event, values = window.read()
    if event == 'Отмена' or event == sg.WIN_CLOSED:
        window.close()
        sys.exit()
    else:
        break
window.close()

#Загрузка установленных сертификатов
cwd = os.getcwd()
try:
    os.chdir(certp)
    result = subprocess.run(['certmgr.exe', '-list'], shell=True, capture_output=True, text=True, encoding='866')
except:
    sg.Popup('Произошла ошибка запуска ПО Крипто ПРО.')
    sys.exit()
os.chdir(cwd)

#Парсинг возвращенный данных
text = result.stdout
while "  " in text:    
    text = text.replace("  ", " ")
while '""' in text:
    text = text.replace('""', '"')
start = 0
g = []
while start < (len(text)):
    cn1 = text.find('Subject : ', start)
    if cn1 == -1:
        break
    cn2 = text.find('\n', cn1)
    g.append(text[cn1+10:cn2])
    start = cn2
org = []
s = 0
for i in g:
    ii = i.split(', ')
    name = ['', '', '']
    for l in ii:
        if l[0:3] == "CN=":
            name[0] = l[3:].lstrip('"')
        if l[0:2] == "E=":
            name[2] = l[2:]
        if l[0:4] == "ИНН=":
            name[1] = l[4:].lstrip("0")
    if name[1] != '' and name[2] != '':
        org.append(name[0]+'; '+name[2]+'; '+name[1]) 
if len(org) == 0:
    sg.Popup('Ошибка! В системе не обнаружены ЭЦП.')
    sys.exit()

#Обработка запроса
def ronga():
    ddd = values['kto'][0].split("; ")
    filename = values[0] #.replace("/", "\\")[:-1]
    if values['tosig'] == True:
        pusk = cspp + ' -sfsign -sign -add -in "' + filename + '" -out "' + os.path.splitext(filename)[0] + '_sig' + os.path.splitext(filename)[1] + '" -my ' + ddd[1]
    else:
        pusk = cspp + ' -sfsign -sign -detached -add -in "' + filename + '" -out "' + filename + '.sig" -my ' + ddd[1]
    inin = ddd[2]
    if inin != "":
        pusk = pusk + ',' + inin
    par_ol = values['password']
    if par_ol != "":
        pusk = pusk + ' -password ' + par_ol
    CREATE_NO_WINDOW = 0x08000000
    zapusk = subprocess.Popen(pusk, creationflags=CREATE_NO_WINDOW, stdout=subprocess.PIPE, text=True, encoding='866')
    zapusk.wait()
    data = zapusk.communicate()
    if zapusk.returncode:
        print(data[1])
        sg.Popup('Прозошла ошибка, попробуйте еще раз!')
    print(data[0])
    sg.Popup('Файл подписан!')

#Создание окна программы
layout = [
    [sg.Text('Выберите владельца ЭЦП')],
    [sg.Listbox(values=org, size=(88, len(org)), key='kto', enable_events=True)],
    [sg.Text('Введите ПИН закрытого ключа*'), sg.InputText(key='password', password_char='*', size=(15, 1))],
    [sg.Text('* Необязательный пункт. Запрашивается через ПО Крипто ПРО.')],
    [sg.Text('Выберите файл'), sg.InputText(), sg.FileBrowse('Выбрать', key = 'file')],
    [sg.Checkbox('Присоединенная подпись', key='tosig')],
    [sg.Button('Подписать'), sg.Button('Очистить форму'), sg.Button('Выход')],
    [sg.Output(key='vyxod', size=(88, 20))],
    [sg.Text('simpleSIG v1.0 (2020.10.31)'), sg.Button('О программе')]
]
window = sg.Window('Подписать файлы ЭЦП', layout)

# Ожидание команды
while True:
    event, values = window.read()
    if event in (None, 'Выход', sg.WIN_CLOSED):
        window.close()
        sys.exit()
    if event == 'Очистить форму':
        window['password']('')
        window['file']('Выбрать')
        window['vyxod']('')
        window[0]('')
        window['tosig'](False)
    if event == 'О программе':
        sg.Popup('simpleSIG - подписывать файлы ЭЦП легко!\nАвтор: Максим Ёдгоров\ngithub: https://github.com/myodgor/simpleSIG')
    if event == 'Подписать':
        if len(values['kto']) == 0:
            sg.Popup('Ошибка! Выберите ЭЦП.')
        elif values['file'] == '' or values['file'] == 'Выбрать':
            sg.Popup('Ошибка! Выберите файл.')
        else:
            ronga()

