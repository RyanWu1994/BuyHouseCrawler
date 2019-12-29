#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from lxml import etree
from sqlalchemy import create_engine
import mysql.connector
import pandas as pd

ua = UserAgent()
headers = {"User-Agent":ua.random}

page_url = "https://www.rakuya.com.tw/sell/result?city=2&zipcode=220&price=~5000&room=1%2C2%2C3%2C4%2C5~&age=1~50&page=1"
page_res = requests.get(page_url,headers=headers)
sel = etree.HTML(page_res.text)

last_page = sel.xpath("//div[@class='block__pagination']/nav/p[@class='pages']//text()")
head = last_page[0].strip("第  /  頁").split(" /")
lastpage66 = int(head[1])+1


#新北市板橋

house_name = []  # 案名
house_address = []  # 地址
house_price = []  # 房價
house_year = []  # 屋齡
house_area = []  # 坪數
house_Pattern = []  # 房間規格

for j in range(1,lastpage66):
    url = "https://www.rakuya.com.tw/sell/result?city=2&zipcode=220&price=~5000&room=1%2C2%2C3%2C4%2C5~&age=1~50&page="+str(j)
    res = requests.get(url,headers = headers)
    soup = BeautifulSoup(res.text)
    sel = etree.HTML(res.text)

#price
    price = soup.select(".text__price")

    for i in price:
        house_price.append(i.text.strip("萬"))


    #Name

    nameList = soup.find_all("div","h2 title-2")

    for item in nameList:
        house_name.append(item.text.strip("新上架"))

    #Address
    nameList = soup.find_all("span","map")

    for item in nameList:
        house_address.append(item.text.strip("\n"))


    # year
    year = soup.select(".list__info li:nth-child(4)")

    for i in year:
        house_year.append(i.text.strip("年"))

    #area 坪

    area = sel.xpath("//div[@class='grid-column rightside']/ul[@class='list__info']/li[2]//text()")

    for i in area:
        house_area.append(i.strip("坪"))

    #Pattern 規格
#     house_Pattern = sel.xpath("//div[@class='grid-column rightside']/ul[@class='list__info']/li[3]//text()")
    Pattern = soup.select(".list__info li:nth-child(3)")

    for i in Pattern:
        house_Pattern.append(i.text)

new = []
for n in range(len(house_name)):
    new.append({"Name":house_name[n],"Address":house_address[n],"price":house_price[n],"Year":house_year[n],"Area":house_area[n],"Pattern":house_Pattern[n],"Store":"樂屋網"})
new


# In[ ]:


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

for item in new:
    df = pd.DataFrame(item, index=[0]) # 為何加入index[0]:因為單次僅一個dict轉成df,詳情:https://reurl.cc/4gm4qD
    try:
        df.to_sql("banqiao_data",con=con,if_exists='append', index=False) #假設table已存在 就自動往下加入data
    except Exception as e:
        if 'PRIMARY' in str(e):
            pass
        
con.close() #關閉資料池連結
engine.dispose() #關閉資料庫連結
print("rakuya banqiao data updated")

