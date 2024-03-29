import json
import requests
from PIL import Image, ImageDraw, ImageFont

token = 'DA5juDSuRp_QgJjoKHzw-VEKO17oJ5C41vawrsu1ztU'
f = open('tree.json', 'r')
tree_json = eval(f.read())
f.close()
def simple_message(chat_id, msg, token):
    json_init = {"text": f"{msg}"}
    url_init = 'https://botapi.tamtam.chat/messages?chat_id=' + str(chat_id) + '&access_token=' + token
    # ret = requests.post(url_init, data=json.dumps(json_init), proxies=proxies)
    ret = requests.post(url_init, data=json.dumps(json_init))
    return ret.json()

def load_image(img_name):
    # url_load = (requests.post(url='https://botapi.tamtam.chat/uploads?type=image&access_token='+token, verify=False, proxies=proxies).json())['url']
    url_load = (requests.post(url='https://botapi.tamtam.chat/uploads?type=image&access_token='+token, verify=False).json())['url']
    files = {'request_file': open(img_name, 'rb')}
    # ret = requests.post(url=url_load,files=files, verify=False, proxies=proxies).json()
    ret = requests.post(url=url_load,files=files, verify=False).json()
    url_token = None
    for key in (ret['photos'].keys()):
        url_token = ret['photos'][key]['token']
        # json_init = {"text": f"{msg}", "attachments": [{"type": "image", "payload": {"token": f"{url_token}"}}, {"type": "inline_keyboard", "payload": {"buttons": [[{"type":"link", "text": f"{link_name}", "url": f"{link}", "intent":"default"}]]}}]}
    return url_token

def construct_message(session_id, input, payload, message):
    keyboard = {"buttons": []}
    url_init = f"https://botapi.tamtam.chat/answers/constructor?session_id={session_id}&access_token={token}"
    # print(input)
    caption = "Конструктор открыток поможет Вам подписать и отправить открытку"
    id = None
    if input == 'callback':
        id = payload
    if id is None and message == '' or payload.find("root:") == 0:
        for key in tree_json.keys():
            kb = [{"type": "callback", "text": key, "payload": key}]
            keyboard['buttons'].append(kb)
            jsn = {"messages": [{"text": caption}], "allow_user_input": False, "hint": "Выбери категорию", "keyboard": keyboard}
            # json_ret = requests.post(url=url_init, data=json.dumps((jsn)), proxies=proxies).json()
            json_ret = requests.post(url=url_init, data=json.dumps((jsn))).json()
    elif id is None and message != '':
        # print('payload', payload)
        file_index = payload.replace("select:", "")
        file_index = file_index[0:file_index.find("|")]
        postcard_key = payload[payload.find("|") + 1:]
        img_name = tree_json[postcard_key][int(file_index)]
        make_postcard(template=img_name, text=message, session_id=session_id)
        url_token = load_image(img_name="out/"+session_id+".jpg")
        keyboard['buttons'].append([{"type": "callback", "text": "Назад", "intent": "negative",
                                     "payload": f"go:{file_index}|{postcard_key}"}])
        jsn = {"messages":
                   [{
                     "attachments":
                         [{"type": "image", "payload": {"token": url_token}}]
                     }],
               "allow_user_input": True, "hint": "Готово!", "keyboard": keyboard}
        # json_ret = requests.post(url=url_init, data=json.dumps((jsn)), proxies=proxies).json()
        json_ret = requests.post(url=url_init, data=json.dumps((jsn))).json()
    elif id.find("select:") == 0:
        file_index = id.replace("select:", "")
        file_index = file_index[0:file_index.find("|")]
        postcard_key = id[id.find("|") + 1:]
        img_name = "templates/"+tree_json[postcard_key][int(file_index)]+"_mini.jpg"
        url_token = load_image(img_name=img_name)
        jsn = {"messages":
                   [{"text": "Добавь подпись",
                     "attachments":
                         [{"type": "image", "payload": {"token": url_token}}]
                     }],
               "allow_user_input": True, "keyboard": keyboard}
        # json_ret = requests.post(url=url_init, data=json.dumps((jsn)), proxies=proxies).json()
        json_ret = requests.post(url=url_init, data=json.dumps((jsn))).json()
    elif id.find("go:") == 0:
        file_index = id.replace("go:","")
        file_index = file_index[0:file_index.find("|")]
        postcard_key = id[id.find("|")+1:]
        go(session_id=session_id, postcard_key=postcard_key, file_index=int(file_index))
    else:
        go(session_id=session_id, postcard_key=id, file_index=0)
def go(session_id, postcard_key, file_index=0):
    if file_index == -999:
        return
    url_init = f"https://botapi.tamtam.chat/answers/constructor?session_id={session_id}&access_token={token}"
    keyboard = {"buttons": []}
    keyboards = []
    files = tree_json[postcard_key]
    file_count = len(files)
    img_prev = 0 if file_index == 0 else file_index-1
    img_cur = file_index
    img_next = file_index if file_index == file_count-1 else file_index+1
    url_token = load_image(img_name="templates/" + tree_json[postcard_key][file_index] + "_mini.jpg")
    keyboards.append({"type": "callback", "text": "⬅️", "intent": f"{'positive' if img_prev!=img_cur else 'default'}", "payload": f"go:{img_prev}|{postcard_key}"})
    keyboards.append({"type": "callback", "text": "➡️", "intent": f"{'positive' if img_next!=img_cur else 'default'}", "payload": f"go:{img_next}|{postcard_key}"})
    keyboard['buttons'].append(keyboards)
    keyboard['buttons'].append([{"type": "callback", "text": "✅", "intent": "negative", "payload": f"select:{img_cur}|{postcard_key}"}])
    keyboard['buttons'].append([{"type": "callback", "text": "❌", "intent": "default", "payload": f"root:"}])
    jsn = {"messages":
               [{
                 "attachments":
                     [{"type": "image", "payload": {"token": url_token}}]
                 }],
           "allow_user_input": False, "hint": "Выбери шаблон и добавь подпись", "keyboard": keyboard}
    json_ret = requests.post(url=url_init, data=json.dumps((jsn))).json()

def transorm_text(text, symbols, rows, text_align=''):
    new_text = ''
    new_text1 = ''
    rows_ =0
    for t in text.splitlines():
        cur_symbols = 0
        for i in t.split(' '):
            if rows_ < rows:
                if cur_symbols + len(i) <= symbols:
                    new_text = new_text + i + " "
                    cur_symbols += len(i) + 1
                else:
                    if rows_ + 1 < rows:
                        new_text = new_text.rstrip() + "\n" + i + " "
                        rows_ += 1
                        cur_symbols = len(i) + 1
        new_text = new_text + "\n"
        rows_ += 1
    if text_align == 'fill':
        new_text1 = ''
        for text in new_text.splitlines():
            add_symb = symbols - len(text)
            cur_spaces = len(text) - len(text.replace(" ", ""))
            space = 0 if cur_spaces == 0 else add_symb // cur_spaces
            # print(space)
            tail = 0 if cur_spaces == 0 else add_symb % cur_spaces
            text = text.replace(' ', ''.join([' ' for s in range(space + 1)]))
            text1 = ""
            for nn in range(len(text)):
                if text[nn] == ' ' and text[nn - 1] != ' ' and tail > 0:
                    text1 = text1 + '  '
                    tail = tail - 1
                else:
                    text1 = text1 + text[nn]
            new_text1 = new_text1 + text1 + '\n'
        new_text = new_text1
    return new_text
def make_postcard(template, text, session_id):
    f = open(f"json/{template}.json", "r")
    params = eval(f.read())
    f.close()
    columns = 1 if params.get("columns") is None else params["columns"]
    text = transorm_text(text=text,
                         symbols=params["row_symbols"],
                         rows=params["rows"] if columns == 1 else int(params["rows"])*2+1,
                         text_align='left' if params.get('align') is None else params['align'])
    if text.find("#error") == 0:
        pass
    else:
        img = Image.open(f"templates/{template}.jpg", "r")
        width, height = img.size
        img = img.rotate(0 if params.get("rotation") is None else params["rotation"], expand=1)
        # print(img.size)
        fnt = ImageFont.truetype(f"fonts/{params['font']}", params["fontsize"])
        d = ImageDraw.Draw(img)
        d.text(xy=(0 if params.get("text_x") is None else params["text_x"], 0 if params.get("text_y") is None else params["text_y"]),
               text=text if columns == 1 else "\n".join(text.splitlines()[0:params["rows"]]),
               align='left' if params.get('align') is None or str(params.get('align')) == 'fill' else params['align'],
               font=fnt,
               width=width,
               height=0 if str(params.get('align_y')) == "top" else height,
               fill=(params['fill_color'][0], params['fill_color'][1], params['fill_color'][2]))
        if columns == 2:
            d.text(xy=(width/2 if params.get("text_x") is None else width/2 + params["text_x"],
                       0 if params.get("text_y") is None else params["text_y"]),
                   text="\n".join(text.splitlines()[params["rows"]:params["rows"]*2]),
                   align='left' if params.get('align') is None or str(params.get('align')) == 'fill' else params['align'],
                   font=fnt,
                   width=width,
                   height=0 if str(params.get('align_y')) == "top" else height,
                   fill=(params['fill_color'][0], params['fill_color'][1], params['fill_color'][2]))
        img = img.rotate(0 if params.get("rotation") is None else -params["rotation"], expand=1)
        img.save(f"out/{session_id}.jpg")


if (__name__ == '__main__'):
    print(transorm_text(text="С днем рождения поздравляю\nСчастья радости желаю\nНе пей, не бей, не матерись\nне отравляй нам с мамой жись",
                  symbols=23, rows=6))
