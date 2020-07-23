import threading
import requests
import send2tamtam

token = 'DA5juDSuRp_QgJjoKHzw-VEKO17oJ5C41vawrsu1ztU'
# proxies = {'http': 'url-proxy.megafon.ru:3128', 'https': 'url-proxy.megafon.ru:3128'}
f = open('tree.json', 'r')
tree_json = eval(f.read())
f.close()
url = 'https://botapi.tamtam.chat/updates?access_token=' + token
sessions = {}

def worker(json_id):
    if len(json_id["updates"]) > 0:
        update_type = None
        for row in json_id['updates']:
            if row.get('update_type') == 'message_construction_request':
                session_id = row['session_id']
                if row['input'].get('payload') is not None:
                    sessions[session_id] = {}
                    sessions[session_id]['payload'] = row['input'].get('payload')
                    sessions[session_id]['message'] = ''
                if row['input'].get('messages') is not None and row['input']['messages'] != [] and row['input']['messages'][0]['text'] != '':
                    sessions[session_id]['message'] = row['input']['messages'][0]['text']
                send2tamtam.construct_message(session_id=session_id,
                                              input=row['input'].get('input_type'),
                                              payload=sessions[session_id].get('payload') if sessions.get(session_id) is not None else '',
                                              message=sessions[session_id].get('message') if sessions.get(session_id) is not None else '')
                print(sessions)
marker = 0
while True:
    try:
        r = requests.get(url if marker == 0 else url+f"&marker={marker}", timeout=30, stream=True, proxies=proxies).json()
        marker = r['marker']
        t = threading.Thread(target=worker, args=(r, ))
        t.start()
    except Exception as ex:
        print(ex.__str__())
