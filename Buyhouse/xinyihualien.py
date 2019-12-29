#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas
from sqlalchemy import create_engine
import mysql.connector
import re

from requests.packages import urllib3
urllib3.disable_warnings()

url = "https://www.sinyi.com.tw/buy/list/0-5000-price/Hualien-county/Taipei-R-mrtline/03-mrt/default-desc/"

#last page
res = requests.get(url + "1", verify = False)
sel = etree.HTML(res.text)
page = sel.xpath("//a[@class='pageLinkClassName']//text()")
lastpage = int(page[-1]) + 1

new_name = []
new_address = []
new_price = []
new_year = []
new_area = []
new_pattern = []

for i in range(1,lastpage):
    res = requests.get(url + str(i), verify = False)
    sel = etree.HTML(res.text)

# 房屋名稱
    name = sel.xpath("//div[@class='LongInfoCard_TypeMobile']/div[1]/div[@class='LongInfoCard_Type_Name']//text()")
    new_name.extend(name)

# 房屋地址
    address = sel.xpath("//div[2]/div[1]/div[@class='LongInfoCard_Type_Address']//text()")
    new_address.extend(address)
    
# 房屋售價
    price = sel.xpath("//div[@class='LongInfoCard_TypeMobile']/div[1]/div[2]/div/span[1]//text()")
    for np in price:
        if np != '萬':
            new_price.append(int(np.replace(',','')))
    
# 房屋屋齡
    year = sel.xpath("//div[2]/div[1]/div[@class='LongInfoCard_Type_HouseInfo']/span[3]//text()")
    year2 = []
    for ny in year:
        try:
            year2.append(float(ny.strip('年')))
        except:
            year2.append(0)
    new_year.extend(year2)

#房屋坪數    
    area = sel.xpath("//div[2]/div[1]/div[@class='LongInfoCard_Type_HouseInfo']/span[1]//text()")
    for na in area:
        if na != '建坪 ' and na != '地坪 ':
            new_area.append(float(na))

#房屋隔間
    pattern = sel.xpath("//div[2]/div[1]/div[@class='LongInfoCard_Type_HouseInfo']/span[2]//text()")
    new_pattern.extend(pattern)


#合併

hualien_data = []
for j in range (len(new_name)):
    hualien_data.append({"Store":"信義", "Name":new_name[j], "Address":new_address[j], "Price":new_price[j], "Year":new_year[j], 
                      "Area":new_area[j], "Pattern":new_pattern[j]})

# 在mysql的db中 建立好table,PRIMARY KEY=book_name
# book_data=table 名稱
'''
CREATE TABLE IF NOT EXISTS `hualien_data`(
   `Store` VARCHAR(255) NOT NULL,
   `Name` VARCHAR(255) NOT NULL,
   `Address` VARCHAR(255) NOT NULL,
   `Price` Integer NOT NULL,
   `Year` DECIMAL(5,2) NOT NULL,
   `Area` DECIMAL(5,2) NOT NULL,
   `Pattern` VARCHAR(255) NOT NULL,
    CONSTRAINT `house_id` PRIMARY KEY (`Name`,`Area`)
    
)ENGINE=InnoDB DEFAULT CHARSET=utf8; 
'''

#連結資料庫
#範本解釋:create_engine('mysql+mysql_driver://mysql帳號:mysql密碼@機器ip:mysql_port/DB名稱?其他參數', encoding='mysql編碼'
#charset=utf8 資料庫編碼
engine = create_engine('mysql+mysqlconnector://root:root@127.0.0.1:3306/Buyhouse?charset=utf8', encoding='utf-8')
con = engine.connect() #建立連結

for item in hualien_data:
    df = pandas.DataFrame(item, index=[0]) # 為何加入index[0]:因為單次僅一個dict轉成df,詳情:https://reurl.cc/4gm4qD
    try:
        df.to_sql("hualien_data",con=con,if_exists='append', index=False) #假設table已存在 就自動往下加入data
    except Exception as e:
        if 'PRIMARY' in str(e):
            pass

con.close() #關閉資料池連結
engine.dispose() #關閉資料庫連結

#con.close()與engine.dispose()差別可參考:https://reurl.cc/oDd0dg

print("XinYi Hualien data updated!!")

# In[ ]:




