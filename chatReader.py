import re
import datetime
import json
def stringify(messageText, pureText = False):
    if(not isinstance(messageText, list)):
        return messageText
    ret = ''
    for element in messageText:
        if(isinstance(element, str)):
            ret = ret + element
        elif(type(element) is dict and 'text' in element and pureText == False):
            ret = ret + element['text']
    return ret
def readChat(path):
    if(path.endswith('.json')):
        f = open(path, encoding="utf-8")
        data = json.load(f)
        f.close()

        rawMessages = data['messages']
        messages = []
        for rawMessage in rawMessages:
            msg = {}
            msg['id'] = 't'+str(rawMessage['id'])
            msg['type'] = rawMessage['type']
            msg['dateTime'] = datetime.datetime.strptime(rawMessage['date'], '%Y-%m-%dT%H:%M:%S')
            if('from' in rawMessage):
                msg['from'] = rawMessage['from']
            else:
                msg['from'] = None
            if('media_type' in rawMessage and rawMessage['media_type']=='sticker'):
                msg['type'] = 'sticker'
            elif ('photo' in rawMessage):
                msg['type'] = 'photo'
            elif ('file' in rawMessage and 'mime_type' in rawMessage):
                msg['type'] = rawMessage['mime_type']
            if('text' in rawMessage):
                if(type(rawMessage['text']) is list):
                    msg['text'] = stringify(rawMessage['text'], True)
                else:
                    msg['text'] = rawMessage['text']
            messages.append(msg)
        return messages
    elif(path.endswith('.txt')):
        #https://www.imrankhan.dev/pages/Exploring%20WhatsApp%20chats%20with%20Python.html
        # some regex to account for messages taking up multiple lines
        pat = re.compile(r'^(\d(\d)?\/\d(\d)?\/\d\d\d\d.*?)(?=^^\d(\d)?\/\d(\d)?\/\d\d\d\d|\Z)', re.S | re.M)
        with open(path, encoding="utf-8") as f:
            rawMessages = [m.group(1).strip().replace('\n', ' ') for m in pat.finditer(f.read())]
        messages = []
        counter = 0
        for rawMessage in rawMessages:
            #print(rawMessage)
            msg = {}
            # timestamp is before the first dash
            msg['id'] = 'w'+str(counter)
            tryFormats = ['%d/%m/%Y, %H:%M', '%d/%m/%Y, %I:%M %p','%d/%m/%Y, %I:%M:%S %p']
            for tryFormat in tryFormats:
                try:
                    msg['dateTime'] = datetime.datetime.strptime(rawMessage.split(' - ')[0], tryFormat)
                    #print(msg)
                    break
                except ValueError as e:
                    #print(e)
                    continue
            # sender is between 24hr or am/pm, dash and colon
            #print(msg)
            try:
                msg['from'] = re.search('([0-9]|M) - (.*?):', rawMessage).group(2)
            except:
                msg['from'] = None
                continue
            try:
                msg['text'] = rawMessage.split(': ', 1)[1]
            except:
                msg['text'] = None
                continue

            if(msg['text']=='<Media omitted>'):
                msg['type'] = 'media'
            else:
                msg['type'] = 'text'
            messages.append(msg)
            counter = counter + 1
            #print(msg)
        return messages