#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 永慶房屋-花蓮縣-花蓮市-5000萬以下

import requests
from bs4 import BeautifulSoup
from lxml import etree
from time import sleep
from fake_useragent import UserAgent
from sqlalchemy import create_engine
import mysql.connector
import pandas as pd

# 模擬瀏覽器
ua = UserAgent()
headers = {"User-Agent":ua.random}

# 用來接資料的空list
project_name = []
Address = []
prices = []
Year = []
Area = []
Pattern = []
Hualien = []

# city_list = ["台北市-大安區","新北市-板橋區","花蓮縣-花蓮市"]

url_2 = "https://buy.yungching.com.tw/region/花蓮縣-花蓮市_c/-5000_price/?pg=100000"
res_2 = requests.get(url_2)
sel = etree.HTML(res_2.text)
item = sel.xpath("//a[@class='ga_click_trace']//text()")
page = int(item[-3])+1
    

# 爬蟲程式
for k in range(1,page):
    url = "https://buy.yungching.com.tw/region/花蓮縣-花蓮市_c/-5000_price/pg=3?pg="+str(k)
    res = requests.get(url,headers=headers)
    soup = BeautifulSoup(res.text)

    name = soup.select("h3")
    price = soup.select(".price-num")
    age = soup.select(".item-info-detail li:nth-child(2)")
    genre = soup.select(".item-info-detail li:nth-child(1)")
    number = soup.select(".item-info-detail li:nth-child(6)")
    compartment = soup.select(".item-info-detail li:nth-child(7)")

# 案名與地址==============================================================
    for i in range(len(name)): 
        x = name[i].text.split()
        project_name.append(x[0])
        Address.append(x[1])

#總價=====================================================================
    for i in price:
        prices.append(int(i.text.replace(",","")))

#屋齡=====================================================================
    for i in age:
        if i.text.strip("\r\n年 ") == "":
            i = 0
            Year.append(float(i))
        else:
            Year.append(float(i.text.strip("\r\n年 ")))

#坪數=====================================================================
    for i in number:
        if i.text.strip("建物  坪") == "":
            i = None
            Area.append(i)
        else:
            Area.append(float(i.text.strip("建物  坪")))

#房屋隔間==================================================================
    for i in compartment:
        if i.text.strip("\r\n ") == "":
            i = None
            Pattern.append(i)
        else:
            Pattern.append(i.text.strip("\r\n "))

#組合=====================================================================
for i in range(len(project_name)):
    Hualien.append({"Name":project_name[i],"Address":Address[i],"Price":prices[i],"Year":Year[i],"Area":Area[i],"Pattern":Pattern[i],"Store":"永慶"})

    

# 在mysql的db中 建立好table,PRIMARY KEY=Name
# Taipei=table 名稱
'''
CREATE TABLE IF NOT EXISTS hualien_data(
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

for item in Hualien:
    df = pd.DataFrame(item, index=[0]) # 為何加入index[0]:因為單次僅一個dict轉成df,詳情:https://reurl.cc/4gm4qD
    try:
        df.to_sql("hualien_data",con=con,if_exists='append', index=False) #假設table已存在 就自動往下加入data
    except Exception as e:
        if 'PRIMARY' in str(e):
            pass
        
con.close() #關閉資料池連結
engine.dispose() #關閉資料庫連結

#con.close()與engine.dispose()差別可參考:https://reurl.cc/oDd0dg

print("yungching hualien data updated")


# In[ ]:




