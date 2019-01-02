import os
import subprocess
import json
import uuid
import PySimpleGUI as sg
import requests
from archive import extract
from shutil import rmtree

dir = os.path.dirname(os.path.realpath(__file__))+'/.TDeskMulti/'
if os.name == 'nt':
    telegram = dir+'bin/Telegram/Telegram.exe'
elif os.name == 'mac':
    print('MacOS is not supported.')
    quit()
else:
    telegram = dir+'bin/Telegram/Telegram'
strings = {'new_account': 'Nuovo account', 'update_tdesk': 'Aggiorna TDesktop', 'start': 'Avvia', 'edit_name': 'Cambia nome', 'delete_account': 'Elimina account', 'enter_acc_name': 'Inserisci il nome dell\'account', 'e_not_selected_account': 'Seleziona un account dal menu', 'error': 'Errore', 'sure': 'Sei sicuro?'}

def start_account(account):
    global telegram
    global accounts
    subprocess.Popen([telegram, '-workdir', dir+'accounts/'+accounts[account]])
    quit()
def download_tdesk():
    global dir
    layout = [  [sg.InputCombo(['Telegram Desktop', 'Telegram Desktop Alpha'])],
                [sg.OK()]                                                     ]
    window = sg.Window('Telegram Desktop version').Layout(layout)
    event, number = window.Read()
    version = number[0]
    window.Close()
    if version == 'Telegram Desktop':
        if os.name == 'nt':
            link = 'https://telegram.org/dl/desktop/win_portable'
            file_name = dir+'telegram.zip'
        else:
            link = 'https://telegram.org/dl/desktop/linux'
            file_name = dir+'telegram.tar.xz'
    if version == 'Telegram Desktop Alpha':
        if os.name == 'nt':
            link = 'https://telegram.org/dl/desktop/win_portable?beta=1'
            file_name = dir+'telegram.zip'
        else:
            link = 'https://telegram.org/dl/desktop/linux?beta=1'
            file_name = dir+'telegram.tar.xz'
    layout = [  [sg.Text('Downloading Telegram Desktop...')],
                [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progressbar')]  ]
    window = sg.Window('Downloading Telegram Desktop...').Layout(layout)
    progress_bar = window.FindElement('progressbar')
    event, values = window.Read(timeout=0)
    with open(file_name, 'wb') as f:
        response = requests.get(link, stream=True)
        total_length = response.headers.get('content-length')
        if total_length is None:
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                percentage = int(100 * dl / total_length)
                progress_bar.UpdateBar(percentage)
                event, values = window.Read(timeout=0)
    extract(file_name, dir+'bin/', method='insecure')
    os.remove(file_name)
    window.Close()

if not os.path.exists(dir):
    os.makedirs(dir)
if not os.path.exists(dir+'accounts'):
    os.makedirs(dir+'accounts')
if not os.path.exists(dir+'bin'):
    os.makedirs(dir+'bin')
if not os.path.exists(dir+'accounts.json'):
    file = open(dir+'accounts.json', 'w')
    file.write('{}')
    file.close()
file = open(dir+'accounts.json', 'r')
accounts = json.loads(file.read())
file.close()
if not os.path.exists(telegram):
    download_tdesk()
layout = [  [sg.Button(strings['new_account']), sg.Button(strings['update_tdesk'])],
            [sg.Listbox(values=list(accounts.keys()), size=(40, 10), bind_return_key=True, key='selected_account'), sg.Column([[sg.Button(strings['start'])], [sg.Button(strings['edit_name'])], [sg.Button(strings['delete_account'])]])]  ]
window = sg.Window('TDeskMulti').Layout(layout)
while True:
    event, values = window.Read()
    if event is None or event == 'Exit':
        break
    if event == strings['new_account']:
        name = sg.PopupGetText(strings['enter_acc_name'], strings['enter_acc_name'])
        account_id = str(uuid.uuid4())
        os.makedirs(dir+'accounts/'+account_id)
        accounts[name] = account_id
        file = open(dir+'accounts.json', 'w')
        file.write(json.dumps(accounts))
        file.close()
        window.FindElement('selected_account').Update(list(accounts.keys()))
    if event == strings['update_tdesk']:
        download_tdesk()
    if event == strings['start']:
        if values['selected_account'] == []:
            sg.Popup(strings['error'], strings['e_not_selected_account'])
        else:
            window.Close()
            start_account(values['selected_account'][0])
    if event == strings['edit_name']:
        if values['selected_account'] == []:
            sg.Popup(strings['error'], strings['e_not_selected_account'])
        else:
            name = sg.PopupGetText(strings['enter_acc_name'], strings['enter_acc_name'])
            accounts[name] = accounts[values['selected_account'][0]]
            del accounts[values['selected_account'][0]]
            window.FindElement('selected_account').Update(list(accounts.keys()))
            file = open(dir+'accounts.json', 'w')
            file.write(json.dumps(accounts))
            file.close()
    if event == strings['delete_account']:
        if values['selected_account'] == []:
            sg.Popup(strings['error'], strings['e_not_selected_account'])
        else:
            if sg.PopupYesNo(strings['sure']) == 'Yes':
                account_id = accounts[values['selected_account'][0]]
                del accounts[values['selected_account'][0]]
                window.FindElement('selected_account').Update(list(accounts.keys()))
                file = open(dir+'accounts.json', 'w')
                file.write(json.dumps(accounts))
                file.close()
                rmtree(dir+'accounts/'+account_id)

window.Close()
