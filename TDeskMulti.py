#   Copyright 2019 peppelg
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import os
import subprocess
import json
import uuid
import PySimpleGUI as sg
import requests
from archive import extract
from shutil import rmtree
import locale

dir = os.path.dirname(os.path.realpath(__file__))+'/.TDeskMulti/'
if os.name == 'nt':
    telegram = dir+'bin/Telegram/Telegram.exe'
elif os.name == 'mac':
    print('MacOS is not supported.')
    quit()
else:
    telegram = dir+'bin/Telegram/Telegram'
strings = {'new_account': 'Nuovo account', 'update_tdesk': 'Aggiorna TDesktop', 'start': 'Avvia', 'edit_name': 'Cambia nome', 'delete_account': 'Elimina account', 'enter_acc_name': 'Inserisci il nome dell\'account', 'e_not_selected_account': 'Seleziona un account dal menu', 'e_account_exists': 'Esiste già un account con questo nome.', 'error': 'Errore', 'sure': 'Sei sicuro?'}
strings_en = {'new_account': 'Add Account', 'update_tdesk': 'Update Telegram Desktop', 'start': 'Start', 'edit_name': 'Edit name', 'delete_account': 'Delete account', 'enter_acc_name': 'Enter the account name', 'e_not_selected_account': 'Pls select an account', 'e_account_exists': 'An account with this name already exists.', 'error': 'Error', 'sure': 'Are you sure?'}
if not locale.getdefaultlocale()[0] == 'it_IT':
    strings = strings_en

def start_account(account):
    global telegram
    global accounts
    subprocess.Popen([telegram, '-workdir', dir+'accounts/'+accounts[account]])
    sys.exit(0)
def download_tdesk():
    global dir
    global icon
    layout = [  [sg.InputCombo(['Telegram Desktop', 'Telegram Desktop Alpha'], readonly=True)],
                [sg.OK()]                                                     ]
    window = sg.Window('Telegram Desktop version', icon=icon).Layout(layout)
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
    window = sg.Window('Downloading Telegram Desktop...', icon=icon).Layout(layout)
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
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('')
    return os.path.join(base_path, relative_path)

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
icon = resource_path('icon.ico')
if not os.path.exists(icon):
    icon = 'https://raw.githubusercontent.com/peppelg/TDeskMulti/master/icon.ico'
if not os.path.exists(telegram):
    download_tdesk()
layout = [  [sg.Button(strings['new_account']), sg.Button(strings['update_tdesk'])],
            [sg.Listbox(values=list(accounts.keys()), size=(40, 10), bind_return_key=True, key='selected_account'), sg.Column([[sg.Button(strings['start'])], [sg.Button(strings['edit_name'])], [sg.Button(strings['delete_account'])]])]  ]
window = sg.Window('TDeskMulti', icon=icon).Layout(layout)
while True:
    event, values = window.Read()
    if event is None or event == 'Exit':
        break
    if event == strings['new_account']:
        name = sg.PopupGetText(strings['enter_acc_name'], strings['enter_acc_name'], icon=icon)
        if name:
            if not name in accounts:
                account_id = str(uuid.uuid4())
                os.makedirs(dir+'accounts/'+account_id)
                accounts[name] = account_id
                file = open(dir+'accounts.json', 'w')
                file.write(json.dumps(accounts))
                file.close()
                window.FindElement('selected_account').Update(list(accounts.keys()))
            else:
                sg.Popup(strings['error'], strings['e_account_exists'], icon=icon)
    if event == strings['update_tdesk']:
        download_tdesk()
    if event == strings['start']:
        if values['selected_account'] == []:
            sg.Popup(strings['error'], strings['e_not_selected_account'], icon=icon)
        else:
            window.Close()
            start_account(values['selected_account'][0])
    if event == strings['edit_name']:
        if values['selected_account'] == []:
            sg.Popup(strings['error'], strings['e_not_selected_account'], icon=icon)
        else:
            name = sg.PopupGetText(strings['enter_acc_name'], strings['enter_acc_name'], icon=icon)
            accounts[name] = accounts[values['selected_account'][0]]
            del accounts[values['selected_account'][0]]
            window.FindElement('selected_account').Update(list(accounts.keys()))
            file = open(dir+'accounts.json', 'w')
            file.write(json.dumps(accounts))
            file.close()
    if event == strings['delete_account']:
        if values['selected_account'] == []:
            sg.Popup(strings['error'], strings['e_not_selected_account'], icon=icon)
        else:
            if sg.PopupYesNo(strings['sure'], icon=icon) == 'Yes':
                account_id = accounts[values['selected_account'][0]]
                del accounts[values['selected_account'][0]]
                window.FindElement('selected_account').Update(list(accounts.keys()))
                file = open(dir+'accounts.json', 'w')
                file.write(json.dumps(accounts))
                file.close()
                rmtree(dir+'accounts/'+account_id)

window.Close()
