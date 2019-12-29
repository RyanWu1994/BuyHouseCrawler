#!/usr/bin/env python
# coding: utf-8

# In[5]:


import requests
from bs4 import BeautifulSoup
from lxml import etree
from fake_useragent import UserAgent
from sqlalchemy import create_engine
import mysql.connector
import pandas as pd

ua = UserAgent()
headers = {"User-Agent":ua.random}
url = "https://buy.cthouse.com.tw/area/1-50-year/新北市-city/板橋區-town/0-5000-price/page1.html"
headers = {"User-Agent":ua.random}
res = requests.get(url,headers=headers)
# soup = BeautifulSoup(res.text)
sel = etree.HTML(res.content)

pageList = sel.xpath("//div[@class='pageBar']/a[6]//text()")
lastPage = int(pageList[0].strip("..."))+1


Name = []
Address = []
Price = []
Year = []
Area = []
Pattern = []


for j in range (1,lastPage):
    
    ua = UserAgent()
    url = "https://buy.cthouse.com.tw/area/1-50-year/新北市-city/板橋區-town/0-5000-price/page"+str(j)+".html"
    headers = {"User-Agent":ua.random}
    res = requests.get(url,headers=headers)
    soup = BeautifulSoup(res.text)
    sel = etree.HTML(res.content)

    #案名
    nameList = soup.find_all("a","intro__name")
    for item in nameList:
        Name.append(item.text)

    #地址
    addList = soup.select(".intro__add")
    for i in addList:
        Address.append(i.text)

    #價錢
    price = sel.xpath("//div[@class='item__price']/span[@class='price--real']/i//text()")
    for i in price:
        Price.append(i.replace(",",""))

    #年份
    year = sel.xpath("//div[@class='item__intro']/ul[@class='pcShow']/li[1]/i//text()")
    for i in year:
        Year.append(i)

    #坪數
    area = sel.xpath("//div[@class='mShow item__btmIntro']/ul/li[2]/i//text()")
    for i in area:
        Area.append(i)

    #規格
    nb = soup.find_all('div', {'class': 'item__intro'})
    for i in range(len(nb)):
        patternList = soup.find_all('ul', {'class': 'pcShow'})[i].find_all('li')[3].text
        Pattern.append(patternList)



#合併儲存格
Banqiao = []
for n in range(0,len(Name)):
    Banqiao.append({"Name":Name[n],"Address":Address[n],"Price":Price[n],"Year":Year[n],"Area":Area[n],"Pattern":Pattern[n],"Store":"中信"})


# In[26]:


# 在mysql的db中 建立好table,PRIMARY KEY=Name
# Taipei=table 名稱
'''
CREATE TABLE IF NOT EXISTS banqiao_data(
   Name VARCHAR(255) NOT NULL,
   Address VARCHAR(255) NOT NULL,
   Price Integer NOT NULL,
   Year Integer NOT NULL,
   Area decimal(5,2) NOT NULL,
   Pattern VARCHAR(255) NOT NULL,
   PRIMARY KEY (Name)

)ENGINE=InnoDB DEFAULT CHARSET=utf8; 
'''

#連結資料庫
#範本解釋:create_engine('mysql+mysql_driver://mysql帳號:mysql密碼@機器ip:mysql_port/DB名稱?其他參數', encoding='mysql編碼'
#charset=utf8 資料庫編碼
engine = create_engine('mysql+mysqlconnector://root:root@127.0.0.1:3306/Buyhouse?charset=utf8', encoding='utf-8')
con = engine.connect() #建立連結

for item in Banqiao:
    df = pd.DataFrame(item, index=[0]) # 為何加入index[0]:因為單次僅一個dict轉成df,詳情:https://reurl.cc/4gm4qD
    try:
        df.to_sql("banqiao_data",con=con,if_exists='append', index=False) #假設table已存在 就自動往下加入data
    except Exception as e:
        if 'PRIMARY' in str(e):
            pass
        
con.close() #關閉資料池連結
engine.dispose() #關閉資料庫連結
print("ctbc banqiao data updated")

