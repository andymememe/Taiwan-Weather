import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os.path
import pandas as pd
import sys

def updateWeatherData():
    file = open('data/time.txt', 'w')
    url = 'http://opendata.cwb.gov.tw/opendataapi?dataid=F-C0032-001&authorizationkey=<API-KEY-REPLACE>'
    res = requests.get(url)
    root = ET.fromstring(res.text)
    
    # Get update info
    time = root.find(addMark('sent')).text
    updateTime = time.split('+')[0]
    file.write(updateTime)
    file.close()
    
    # Get data
    dataset = root.find(addMark('dataset'))
    result = pd.DataFrame(columns=['name', 'time', 'Wx', 'MaxT', 'MinT', 'CI',
                                   'PoP']);
    count = 0
    for loc in dataset.findall(addMark('location')):
        for i in range(3):
            row = [loc.find(addMark('locationName')).text]
            time = loc.findall(addMark('weatherElement'))[0].findall(addMark('time'))[i].find(addMark('startTime')).text
            row.append(time)
            for we in loc.findall(addMark('weatherElement')):
                weType = we.find(addMark('elementName')).text
                timedata = we.findall(addMark('time'))[i]
                row.append(timedata.find(addMark('parameter')).find(addMark('parameterName')).text)
            result.loc[count] = row
            count = count + 1
    result.to_csv('data/data.csv', encoding='utf-8')
    return result

def addMark(tag):
    return '{urn:cwb:gov:tw:cwbcommon:0.1}' + tag

if(os.path.isfile('data/time.txt')):    
    timeFile = open('data/time.txt', 'r')
    lastUpdateTime = datetime.strptime(timeFile.readlines()[0].strip(), '%Y-%m-%dT%H:%M:%S')
    timeFile.close()
    now = datetime.now()
    timeDelta = now - lastUpdateTime
    if timeDelta.seconds > 6 * 60 * 60:
        data = updateWeatherData()
    else:
        data = pd.DataFrame.from_csv('data/data.csv')
else:
    data = updateWeatherData()

locationName = sys.argv[1].replace('台', '臺')
locData = data.loc[data['name'] == locationName]
print(locationName + '的天氣概況')
for _, row in locData.iterrows():
    print(row['time'] + ' 天氣為' + row['Wx'] + '，氣溫為' + str(row['MinT']) + '~' + str(row['MaxT']))

