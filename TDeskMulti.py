#   Copyright 2019-2020 peppelg
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
import sys
import subprocess
import json
import uuid
import locale
import base64
import requests
import PySimpleGUI as sg
# import PySimpleGUIQt as sg
from archive import extract
from shutil import rmtree
import argparse

parser = argparse.ArgumentParser(description='Telegram Desktop multi-account.')
parser.add_argument('--dir', dest='directory',
                    help='Directory where TDeskmulti will store your Telegram accounts')
args = parser.parse_args()

if args.directory and os.path.isdir(args.directory):
    dir = os.path.realpath(args.directory) + '/.TDeskMulti/'
else:
    if (os.name == 'nt' and getattr(sys, 'frozen', False)):
        dir = os.getenv('APPDATA')+'/.TDeskMulti/'
    else:
        dir = os.path.dirname(os.path.realpath(__file__)) + '/.TDeskMulti/'


if os.name == 'nt':
    telegram = dir+'bin/Telegram/Telegram.exe'
elif os.name == 'mac':
    print('MacOS is not supported.')
    quit()
else:
    telegram = dir+'bin/Telegram/Telegram'
strings = {'new_account': 'Nuovo account', 'update_tdesk': 'Aggiorna TDesktop', 'start': 'Avvia', 'edit_name': 'Cambia nome', 'delete_account': 'Elimina account', 'enter_acc_name': 'Inserisci il nome dell\'account',
           'e_not_selected_account': 'Seleziona un account dal menu', 'e_account_exists': 'Esiste già un account con questo nome.', 'error': 'Errore', 'sure': 'Sei sicuro?'}
strings_en = {'new_account': 'Add Account', 'update_tdesk': 'Update Telegram Desktop', 'start': 'Start', 'edit_name': 'Edit name', 'delete_account': 'Delete account',
              'enter_acc_name': 'Enter the account name', 'e_not_selected_account': 'Pls select an account', 'e_account_exists': 'An account with this name already exists.', 'error': 'Error', 'sure': 'Are you sure?'}
if not locale.getdefaultlocale()[0] == 'it_IT':
    strings = strings_en

sg.theme('SystemDefault')
# sg.theme('SystemDefaultForReal')


def start_account(account):
    global telegram
    global accounts
    subprocess.Popen([telegram, '-workdir', dir+'accounts/'+accounts[account]])
    sys.exit(0)


def download_tdesk():
    global dir
    global icon
    layout = [[sg.Combo(['Telegram Desktop', 'Telegram Desktop Alpha'], readonly=True, default_value='Telegram Desktop')],
              [sg.OK()]]
    window = sg.Window('Telegram Desktop version', icon=icon).Layout(layout)
    event, number = window.Read()
    version = number[0]
    window.Close()
    if version == None:
        return 'exit'
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
    layout = [[sg.Text('Downloading Telegram Desktop...')],
              [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progressbar')]]
    window = sg.Window('Downloading Telegram Desktop...',
                       icon=icon).Layout(layout)
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
if not os.path.exists(icon) or os.name == 'posix':
    icon = b'R0lGODlhIAAgAOfFAB6WyB6WyR+XyR+XyiCYyiCYyyGYyyGZyyGZzCKZzCKazCKazSOazSObzSObziSbzimayyScziSczyWczyWdzyWd0Cad0Cae0Cae0See0Sef0Sef0iif0iig0iig0ymg0zOezimh0ymh1Cqh1Cqi1Tmezzaf0Cui1Tmfzzmf0Cuj1iyj1jqg0Syk1zih0i2k1y2k2DSj1Duh0i2l2C6l2C6l2S6m2S+m2S+m2i+n2jCn2jCn202gzDCo20ei0DGo2zGo3DGp3DKp3DKp3TKq3TOq3TOq3lOizTSr3jSr30im1TSs3zWs4DWt4Dat4Teu4mGo0U6u3Waq01uu2mir0V+x3XGu1G2x2XWv1XOw1nWx1Ha23XS75Iq52YS/4ou+34u+4I6+3ZO93ITB5pbB35LC4pnB3pzB3ZPF5Z/H4qjI3azL36PN6qzL46zM5K3M5LDM4K3N5a3N5rHN4K3O56/O5a7R6rfR4rLS6bjR5rjV6r7U57bX7cja6sXb68rb68vc68Xe8Mje7szd7Mze7Mze7czf7szf787f7s/f7c/g783i8c/j8tTj79bk8NLm9Njm8dnm8dbn89jq9t3p8+Ds9eHs9eLt9uDu+OXu9eHv+eXv9+bw+Obx+ejx+Orx+Ofy+ery+Onz+enz+uvz+Ov0+uv1++31++32++72++72/O73/O/3/PD3/PH3/PD4/PH4/PL4/fL5/fP5/fT5/fT6/fX6/fb6/fj6/Pb7/ff7/fj7/vj8/vn8/vr8/vr9/vv9/vz+/v3+//7+//7//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH5BAEKAP8ALAAAAAAgACAAAAj+AP8JHEhQ4JODCA8WXMhwIBMnCSMibNjQSJIlTJo4gSgxIUWCQ4gYsZiEyUOOHZ98/LcDCJAhQ0YmKXkypcqGN3Do2PEDiJAhRYwguZhxY0eGMGjUsIEjx44eQIKElEnTaMSCKla0eDGDho0bTqG+jEnSpNWJA0mcyLq161edPH0CFUpUI8eBH0SMUMv2RdKlTZ9GDcllzEyzEAVy6PAhhF6+Wrl6BbsjCptJrDRRNSsQg4YNHDzk3bs2clcvgUyxWv3oZ9ChS/5RqGABQwbQoh+vnWIH02pRlVbzgSpVpMUHESZQsHAhg4bFH2KUWbRqtSpKjlKtRhPWJcwiDBr+IJcw+wKGK3o6rV7NKVGk9a+qvN3ZUwgCBQsaOIhgIo2k9audAkkflLDSyiuwgOKXUkyFRcABByigQANhoAIgK5cM0oclrcASyyy0MNKXW2AJQAABBhyQgAI+kCHIKKU00scfm8Aiyyy12JILHpC1pRQAAQgwAAEFHHDfAiDk0QcgntyYYy679PKFXmBs0RcMAGQJgAAmPhihGH0Q4oott+gSpS+/KMHYIXSQltU/WmbJ5YkGQNHHHHeQwksvvwATTCiebWCIHKORIFCcWgY55B5wqKGFH8AIMwwxitCGgSFxhJbXoYjGKcAZa1ABoRm4FFPMG6amauonHQzUaZxTPBzRpQFSZFJMFiWgkAIidbAggwsEvdqpogRAYMWRDRTiBnkVFCTsq3N6qQAhbYjH0LPQztoFFgpQhO2rxBaw0rfCCrASp+TGeW6w6a7bkLDnBgQAOw=='

if not os.path.exists(telegram):
    if download_tdesk() == 'exit':
        sys.exit(0)
layout = [[sg.Button(strings['new_account']), sg.Button(strings['update_tdesk'])],
          [sg.Listbox(values=list(accounts.keys()), size=(40, 10), bind_return_key=True, key='selected_account'), sg.Column([[sg.Button(strings['start'])], [sg.Button(strings['edit_name'])], [sg.Button(strings['delete_account'])]])]]
window = sg.Window('TDeskMulti', icon=icon).Layout(layout)
while True:
    event, values = window.Read()
    if event is None or event == 'Exit':
        break
    if event == strings['new_account']:
        name = sg.PopupGetText(
            strings['enter_acc_name'], strings['enter_acc_name'], icon=icon)
        if name:
            if not name in accounts:
                account_id = str(uuid.uuid4())
                os.makedirs(dir+'accounts/'+account_id)
                accounts[name] = account_id
                file = open(dir+'accounts.json', 'w')
                file.write(json.dumps(accounts))
                file.close()
                window.FindElement('selected_account').Update(
                    list(accounts.keys()))
            else:
                sg.Popup(strings['error'],
                         strings['e_account_exists'], icon=icon)
    if event == strings['update_tdesk']:
        download_tdesk()
    if event == strings['start']:
        if values['selected_account'] == []:
            sg.Popup(strings['error'],
                     strings['e_not_selected_account'], icon=icon)
        else:
            window.Close()
            start_account(values['selected_account'][0])
    if event == strings['edit_name']:
        if values['selected_account'] == []:
            sg.Popup(strings['error'],
                     strings['e_not_selected_account'], icon=icon)
        else:
            name = sg.PopupGetText(
                strings['enter_acc_name'], strings['enter_acc_name'], icon=icon)
            accounts[name] = accounts[values['selected_account'][0]]
            del accounts[values['selected_account'][0]]
            window.FindElement('selected_account').Update(
                list(accounts.keys()))
            file = open(dir+'accounts.json', 'w')
            file.write(json.dumps(accounts))
            file.close()
    if event == strings['delete_account']:
        if values['selected_account'] == []:
            sg.Popup(strings['error'],
                     strings['e_not_selected_account'], icon=icon)
        else:
            if sg.PopupYesNo(strings['sure'], icon=icon) == 'Yes':
                account_id = accounts[values['selected_account'][0]]
                del accounts[values['selected_account'][0]]
                window.FindElement('selected_account').Update(
                    list(accounts.keys()))
                file = open(dir+'accounts.json', 'w')
                file.write(json.dumps(accounts))
                file.close()
                rmtree(dir+'accounts/'+account_id)

window.Close()
