import PySimpleGUI as sg
from sys import exit
from os import path, getcwd, chdir
import subprocess
from datetime import datetime


#Текущая дата
tdata = datetime.now()

# Проверка наличия ПО Крипто ПРО
if path.exists(r'C:\Program Files\Crypto Pro\CSP\csptest.exe'):
    cspp = r'C:\Program Files\Crypto Pro\CSP\csptest.exe'
    certp = 'C:\Program Files\Crypto Pro\CSP'
elif path.exists(r'C:\Program Files (x86)\Crypto Pro\CSP\csptest.exe'):
    cspp = r'C:\Program Files (x86)\Crypto Pro\CSP\csptest.exe'
    certp = 'C:\Program Files (x86)\Crypto Pro\CSP'
else:
    sg.Popup('Ошибка!\nПрограммное обеспечение Крипто ПРО не найдено.')
    exit()

# Запуск программы
layout = [
    [sg.Text('Вставьте ключ с ЭЦП')],
    [sg.Submit('Запустить'), sg.Cancel('Отмена')]
]

window = sg.Window('Запуск программы', layout)
while True:
    event, values = window.read()
    if event == 'Отмена' or event == sg.WIN_CLOSED:
        window.close()
        exit()
    else:
        break
window.close()

# Загрузка установленных сертификатов
cwd = getcwd()
try:
    chdir(certp)
    result = subprocess.run(['certmgr.exe', '-list'], shell=True, capture_output=True, text=True, encoding='866')
except:
    sg.Popup('Произошла ошибка запуска ПО Крипто ПРО.')
    exit()
chdir(cwd)

# Парсинг возвращенный данных
text = result.stdout
while "  " in text:
    text = text.replace("  ", " ")
while '""' in text:
    text = text.replace('""', '"')
if 'Subject : ' in text:
    sname = 'Subject : '
elif 'Субъект : ' in text:
    sname = 'Субъект : '
else:
    sg.Popup('Ошибка!\nВ системе не обнаружены ЭЦП.')
    exit()
if 'SHA1 Hash' in text:
    snameSHA = 'SHA1 Hash'
    sSHA = 12
    NVA = 'Not valid after'
    sNVA = 18
else:
    snameSHA = 'SHA1 отпечаток'
    sSHA = 17
    NVA = 'Истекает : '
    sNVA = 11

start = 0
g = []
org = []
s = 0
while start < (len(text)):
    cn1 = text.find(sname, start)
    if cn1 == -1:
        break
    cn2 = text.find('\n', cn1)
    organ = text[cn1 + 10:cn2]
    start = cn2
    cn1 = text.find(snameSHA, start)
    if cn1 == -1:
        break
    cn2 = text.find('\n', cn1)
    organ += ', KeyID=' + text[cn1 + sSHA:cn2]
    start = cn2
    cn1 = text.find(NVA, start)
    if cn1 == -1:
        break
    cn2 = text.find('\n', cn1)
    organ += ', NVA=' + text[cn1 + sNVA:cn1 + sNVA + 10]
    start = cn2
    g.append(organ)
for i in g:
    ii = i.split(', ')
    name = ['', '', '', '', '']
    for l in ii:
        if l[0:3] == "OID":
            oidinn = l.split('=')
            name[1] = str(int(oidinn[1]))
        if l[0:3] == "CN=":
            name[0] = l[3:].lstrip('"')
        if l[0:6] == "KeyID=":
            name[3] = l[6:]
        if l[0:4] == "NVA=":
            name[4] = l[4:]
        if l[0:2] == "G=":
            name[2] = l[2:] + ')'
        if l[0:3] == "SN=":
            name[2] = '(' + l[3:] + ' ' + name[2]
        if l[0:4] == "ИНН=" and name[1] == '':
            name[1] = l[4:].lstrip("0")
    if name[0] != '' and name[1] != '':
        deadline = datetime.strptime(name[4], "%d/%m/%Y")
        if deadline > tdata:
            org.append(name[0] + '; ' + name[4] + '; ' + name[2] + '; ' + name[1] + '; ' + name[3])
if len(org) == 0:
    sg.Popup('Ошибка!\nНе удалось обработать список ЭЦП.')
    exit()


# Обработка запроса
def ronga():
    ddd = values['kto'][0].split("; ")
    if values['fsig'] == True:
        forsig = [' -sfsign', '_sig', '.sig']
    else:
        forsig = [' -cmssfsign', '_p7s', '.p7s']
    filename = values[0]  # .replace("/", "\\")[:-1]
    if values['tosig'] == True:
        pusk = cspp + forsig[0] + ' -sign -add -in "' + filename + '" -out "' + path.splitext(filename)[0] + forsig[1] + \
               path.splitext(filename)[1] + '" -my ' + ddd[4]
    else:
        pusk = cspp + forsig[0] + ' -sign -detached -add -in "' + filename + '" -out "' + filename + forsig[2] + '" -my ' + ddd[4]
    if values['sigtime'] == True:
        pusk = pusk + ' -addsigtime'
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
    return


# Создание окна программы
layout = [
    [sg.Text('Выберите владельца ЭЦП')],
    [sg.Listbox(values=org, size=(88, len(org)), key='kto', enable_events=True)],
    [sg.Radio('В формате SIG', "format", key='fsig', default=True), sg.Radio('В формате PKCS#7', "format", key='fp7s')],
    [sg.Text('Введите ПИН закрытого ключа*'), sg.InputText(key='password', password_char='*', size=(15, 1))],
    [sg.Text('* Необязательный пункт. Запрашивается через ПО Крипто ПРО.')],
    [sg.Text('Выберите файл'), sg.InputText(), sg.FileBrowse('Выбрать', key='file')],
    [sg.Checkbox('Присоединенная подпись', key='tosig')],
    [sg.Checkbox('Со штампом времени', key='sigtime')],
    [sg.Button('Подписать'), sg.Button('Очистить форму'), sg.Button('Выход')],
    [sg.Output(key='vyxod', size=(88, 20))],
    [sg.Text('simpleSIG v1.5 (2024.10.29)'), sg.Button('О программе')]
]
window = sg.Window('Подписать файлы ЭЦП', layout)

# Ожидание команды
while True:
    event, values = window.read()
    if event in (None, 'Выход', sg.WIN_CLOSED):
        window.close()
        exit()
    if event == 'Очистить форму':
        window['password']('')
        window['file']('Выбрать')
        window['vyxod']('')
        window[0]('')
        window['tosig'](False)
    if event == 'О программе':
        sg.Popup(
            'simpleSIG - подписывать файлы ЭЦП легко!\nАвтор: Максим Ёдгоров\ngithub: https://github.com/myodgor/simpleSIG')
    if event == 'Подписать':
        if len(values['kto']) == 0:
            sg.Popup('Ошибка! Выберите ЭЦП.')
        elif values['file'] == '' or values['file'] == 'Выбрать':
            sg.Popup('Ошибка! Выберите файл.')
        else:
            ronga()
