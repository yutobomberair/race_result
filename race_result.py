# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 11:37:13 2021

@author: yutob
"""

##library
# スクレイピング
from selenium import webdriver
from time import sleep
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
# テーブル操作
import pandas as pd
import numpy as np
# 画像出力
#from IPython.display import Image, display
import cv2
import platform
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
#%matplotlib inline
import argparse

# 関数
def get_unique_list(seq):
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]

def get_df(area):
    df = pd.DataFrame()
    if area == '中山':
        df = df_nakayama
    if area == '中京':
        df = df_tyukyo
    if area == '東京':
        df = df_tokyo
    if area == '阪神':
        df = df_hanshin
    if area == '小倉':
        df = df_kokura
    if area == '新潟':
        df = df_nigata
    if area == '函館':
        df = df_hakodate
    if area == '札幌':
        df = df_sapporo
    if area == '福島':
        df = df_hukusima
    
    return df

def get_url(date):
    url = 'https://race.netkeiba.com/top/race_list_sub.html?kaisai_date='+date+'&current_group='+date+'#racelist_top_a'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    race_info = []
    for d in soup.find_all(class_='RaceList_DataList'):
        area = d.find(class_='RaceList_DataTitle').text.split(' ')[1]
        all_race = d.find_all('li', class_='RaceList_DataItem')
        for i in all_race:
            race_info.append([area, i.find(class_="RaceList_Itemtime").text, 'https://race.netkeiba.com'+i.find('a').get('href')[2:]])
    race_info_sort = sorted(race_info, key=lambda x: x[1])
        
    return race_info_sort

def corner_plot(corner):
    li = []
    for i in corner.find_all('td'):
        li.append(i.text)
    corner = []
    for r in li:
        if r != '':
            exch = []
            cp = 0
            ap_i = 0
            for n, i in enumerate(r):
                if i == ',':
                    continue
                elif cp == 1:
                    exch[-1] = exch[-1] + i
                    cp = 0
                elif i == '1' and n != len(r)-1:
                    if r[n+1] != ',' and r[n+1] !=  '(' and r[n+1] != ')' and r[n+1] != '-' and r[n+1]  != '=' and r[n+1] != '*':
                        exch.append(i)
                        cp = 1
                    else:
                        exch.append(i)
                elif i == '-':
                    exch.append('h')
                elif i == '=':
                    exch.append('i')
                elif i == '*':
                    exch.append('s')
                else:
                    exch.append(i)

            c_rank = [] 
            sp = 0
            for i in exch:
                if i == ')':
                    c_rank.append(ap)
                    ap_i = 0
                elif ap_i == 1:
                    if sp == 1:
                        i = '*' + i
                        sp = 0
                        ap.append(i)
                    elif i == 's':
                        sp = 1
                    else:
                        ap.append(i)
                elif i == '(':
                    ap = []
                    ap_i = 1
                elif sp == 1:
                    i = '*' + i
                    sp = 0
                    c_rank.append(i)
                elif i == 's':
                    sp = 1
                else:
                    c_rank.append(i)

            corner.append(c_rank)
        else:
            corner.append('')
    
    return corner

def get_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    #レース数, レース名
    race_num = soup.find(class_="RaceNum").text
    race_name = soup.find(class_="RaceName").text.replace('\n', '')
    race_course = soup.find(class_="RaceData01").text.replace('\n', '').split('/')[1]
    a = soup.find(class_="RaceData01")
    race_weather = a.find_all('span')[2].text.replace('/ ', '')
    corner = 0
    rap = 0
    pace = 0
    h_num = 0
    h_name = 0
    jok = 0
    h_tuka = 0
    h_agari = 0
    h_agari_sort = 0
    
    if race_course.split(' ')[1][0] != '障':
        #分析対象
        corner = soup.find('table', class_="RaceCommon_Table Corner_Num")
        corner = corner_plot(corner)
        rap = [i.text for i in soup.find_all(class_='HaronTime')[1].find_all('td')]
        pace = soup.find(class_='RapPace_Title').span.text
        h_num = [i.find(class_="Num Txt_C").text.replace('\n', '') for i in soup.find_all('tr', class_="HorseList")]
        h_name = [i.find(class_="Horse_Info").a.text for i in soup.find_all('tr', class_="HorseList")]
        jok = [i.find(class_="Jockey").text.replace('\n', '') for i in soup.find_all('tr', class_="HorseList")]
        h_agari = [i.find_all('td')[11].text.replace('\n', '') for i in soup.find_all('tr', class_="HorseList")]
        h_tuka = [i.find_all('td')[12].text.replace('\n', '') for i in soup.find_all('tr', class_="HorseList")]
        h_agari_sort = sorted(get_unique_list(h_agari))
    
    return race_num, race_name, race_course, race_weather, corner, rap, pace, h_num, h_name, jok, h_tuka, h_agari, h_agari_sort

def draw_img(race_info, race_num, race_name, race_course, race_weather, corner, rap, pace, h_num, h_name, jok, h_tuka, h_agari, h_agari_sort, df):
    img_info = race_course.split(' ')
    path, gr, df_path = img_path(race_info, img_info)
    
    if gr != '_障':
        x, y, step = df.at[df_path, 'X'], df.at[df_path, 'Y'], df.at[df_path, 'step']
        img = cv2.imread('./course/'+path+'.png')
        print(path)
        pil_image = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_image)
        font_path = get_fontpath()
        draw = draw_raceinfo(draw, font_path, race_num, race_name)
        draw = draw_raptime(draw, font_path, pace, race_weather, rap, x, y, step)
        syutuba = [[h_num[i], h_name[i], jok[i], h_agari[i], h_tuka[i]] for i in range(len(jok))]
        draw = draw_result(draw, font_path, syutuba, h_agari, h_agari_sort)
        draw = draw_rank(draw, font_path, corner)
        result_image = np.array(pil_image)
        h, w, _ = result_image.shape
        result_image = cv2.resize(result_image, dsize=(int(w/3), int(h/3)))

        cv2.imwrite('./course/output/result'+'_'+race_info[0]+str(race_num.replace("\n",  ""))+gr+'.png', result_image)
#         cv2.imwrite('コース/output/result.png', result_image)
    
    return

def img_path(race_info, img_info):
    gr = '_'+img_info[1][0]
    dis = '_'+img_info[1][1:-1]
    dr = '_'+img_info[2][1]
    route = ''
    if len(img_info) == 4:
        route = '_'+img_info[3][0]
        
    path = race_info[0]+'/'+race_info[0]+gr+dis+dr+route
    df_path = gr[1:]+dis[1:]+route
    
    return path, gr, df_path

def get_fontpath():
    # OSごとにパスが異なる
    font_path_dict = {
      "Windows": "C:/Windows/Fonts/meiryo.ttc",
      "Darwin": "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",  
      "Linux": "/usr/share/fonts/OTF/TakaoPMincho.ttf"
    }

    font_path = font_path_dict.get(platform.system())
    if font_path is None:
      assert False, "想定してないOS"
    
    return font_path

def draw_raceinfo(draw, font_path, race_num, race_name):
    draw.font = ImageFont.truetype(font_path, 250)  # font設定
    draw.text((500, 650), race_num.replace("\n",  ""), (255, 255, 255))  # pil_imageに直接書き込み
    draw.text((1350, 650), race_name, (255, 255, 255)) 
    
    return draw

def draw_raptime(draw, font_path, pace, race_weather, rap, x, y, step):
    draw.font = ImageFont.truetype(font_path, 250)
    draw.text((5000, 150), 'ペース:'+pace, (0, 0, 0))
    draw.text((6300, 150), '('+race_weather+')', (0, 0, 0))
    draw.font = ImageFont.truetype(font_path, 100)  # font設定
    for t in rap:
        draw.text((x, y), t, (0, 0, 255))
        x -= step
    
    return draw

def draw_result(draw, font_path, syutuba, h_agari, h_agari_sort):
    draw.font = ImageFont.truetype(font_path, 150)  # font設定
    color = (0, 0, 0)
    draw.text((6600, 2000), '順位', color)
    draw.text((7000, 2000), '馬番', color)
    draw.text((7400, 2000), '馬名', color)
    draw.text((8900, 2000), '騎手', color)
    draw.text((9450, 2000), '上がり3F', color)
    draw.text((10100, 2000), '通過順位', color)

    y= 2250
    for i in range(len(syutuba)):
        if str(syutuba[i][3]) == str(h_agari_sort[0]):
            color_ch = (0, 200, 255)
        elif str(syutuba[i][3]) == str(h_agari_sort[1]):
            color_ch = (255, 0, 0)
        elif str(syutuba[i][3]) == str(h_agari_sort[2]):
            color_ch = (0, 0, 255)
        else:
            color_ch = (0, 0, 0)
        draw.text((6600, y), str(i+1), color)
        draw.text((7000, y), syutuba[i][0], color)
        draw.text((7400, y), syutuba[i][1], color)
        draw.text((8900, y), syutuba[i][2], color)
        draw.text((9600, y), syutuba[i][3], color_ch)
        draw.text((10100, y), syutuba[i][4], color)
        y += 350
        
    return draw

def draw_rank(draw, font_path, corner):
    color = (0, 0, 0)
    draw.font = ImageFont.truetype(font_path, 150)  # font設定
    coor = [[800, 4900], [800, 5830], [800, 6760], [800, 7690]]
    width = 210
    for c, i in enumerate(corner):
        if len(i) != 0:
            x, y = coor[c][0], coor[c][1]
            for i in corner[c]:
                y = coor[c][1]
                if isinstance(i, list) is True:
                    for j in i:
                        draw.text((x, y), str(j), color)
                        y += 180
                    x += width
                else:
                    if i == 'h':
                        x += 1.5 * width
                        continue
                    elif i == 'i':
                        x += 3.5 * width
                        continue

                    draw.text((x, y), str(i), color)
                    x += width
    return draw

# 座標データの入力
# 中山
ind = ['芝1200_外', '芝1600_外', '芝1800', '芝2000', '芝2200_外', '芝2500', '芝2600_外', '芝3200', '芝3200_外', '芝3600_内', 'ダ1000', 'ダ1200', 'ダ1700', 'ダ1800', 'ダ2400', 'ダ2500']
col = ['X', 'Y', 'step']
df_nakayama = pd.DataFrame(index=ind, columns=col)
zahyou = [[10200, 10200, 10200, 10200, 10200, 10450, 10200, 10200, 10200, 10200, 10200, 10200, 10200, 10000, 10200, 10450], 
         [1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1450, 1400, 1400, 1400, 1450],
         [470, 470, 500, 485, 500, 470, 470, 470, 500, 500, 520, 600, 600, 640, 640, 640]]
df_nakayama['X'] = zahyou[0]
df_nakayama['Y'] = zahyou[1]
df_nakayama['step'] = zahyou[2]

# 中京
ind = ['芝1200', '芝1300', '芝1400', '芝1600', '芝2000', '芝2200', '芝3000', 'ダ1200', 'ダ1400', 'ダ1800', 'ダ1900', 'ダ2500']
col = ['X', 'Y', 'step']
df_tyukyo = pd.DataFrame(index=ind, columns=col)
zahyou = [[7400, 7100, 6800, 6100, 4800, 4200, 1600, 7400, 6800, 5600, 5000, 3200], 
         [1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1350, 1400, 1400],
         [-650, -650, -650, -650, -640, -640, -640, -650, -650, -620, -620, -620]]
df_tyukyo['X'] = zahyou[0]
df_tyukyo['Y'] = zahyou[1]
df_tyukyo['step'] = zahyou[2]

# 東京
ind = ['芝1400', '芝1600', '芝1800', '芝2000', '芝2300', '芝2400', '芝2500', '芝2600', '芝3400', 'ダ1200', 'ダ1300', 'ダ1400', 'ダ1600', 'ダ2100', 'ダ2400']
col = ['X', 'Y', 'step']
df_tokyo = pd.DataFrame(index=ind, columns=col)
zahyou = [[8250, 7900, 7500, 7100, 6700, 6300, 5900, 5500, 4300, 8400, 8150, 8100, 7600, 6300, 3200], 
         [1410, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1350, 1400, 1400, 1400, 1400, 1400],
         [-410, -400, -400, -400, -400, -405, -405, -400, -400, -440, -440, -440, -450, -440, -450]]
df_tokyo['X'] = zahyou[0]
df_tokyo['Y'] = zahyou[1]
df_tokyo['step'] = zahyou[2]

# 阪神
ind = ['芝1200', '芝1400', '芝2000', '芝2200', '芝3000', '芝3200', '芝1400_外', '芝1600_外', '芝1800_外', '芝2400_外', '芝2600_外', '芝3200_外', 'ダ1200', 'ダ1400', 'ダ1800', 'ダ2000', 'ダ2600']
col = ['X', 'Y', 'step']
df_hanshin = pd.DataFrame(index=ind, columns=col)
zahyou = [[10650, 10650, 10650, 10620, 10650, 10650, 10600, 10600, 10600, 10600, 10600, 10600, 10500, 10500, 10500, 10500, 10500], 
         [1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350],
         [460, 460, 480, 460, 460, 460, 370, 370, 370, 370, 370, 370, 520, 520, 530, 530, 530]]
df_hanshin['X'] = zahyou[0]
df_hanshin['Y'] = zahyou[1]
df_hanshin['step'] = zahyou[2]

# 小倉
ind = ['芝1000', '芝1200', '芝1700', '芝1800', '芝2000', '芝2600', 'ダ1000', 'ダ1700', 'ダ2400']
col = ['X', 'Y', 'step']
df_kokura = pd.DataFrame(index=ind, columns=col)
zahyou = [[10600, 10600, 10600, 10600, 10600, 10600, 10600, 10800, 10600], 
         [1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350],
         [530, 530, 530, 530, 530, 530, 600, 600, 600]]
df_kokura['X'] = zahyou[0]
df_kokura['Y'] = zahyou[1]
df_kokura['step'] = zahyou[2]

#新潟
ind = ['芝1200', '芝1400', '芝2000', '芝2200', '芝2400', '芝1400_外', '芝1600_外', '芝1800_外', '芝2000_外', '芝3000_外', '芝3200_外', 'ダ1200', 'ダ1700', 'ダ1800', 'ダ2500']
col = ['X', 'Y', 'step']
df_nigata = pd.DataFrame(index=ind, columns=col)
zahyou = [[7850, 7250, 5550, 4970, 4400, 8250, 7600, 7150, 6750, 8250, 8250, 7850, 7300, 6150, 6300], 
         [1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1350, 1400, 1400, 1400, 1400],
         [-550, -555, -560, -560, -560, -530, -450, -450, -447, 600, 600, -550, -550, -570, -550]]
df_nigata['X'] = zahyou[0]
df_nigata['Y'] = zahyou[1]
df_nigata['step'] = zahyou[2]

#函館
ind = ['芝1000', '芝1200', '芝1700', '芝1800', '芝2000', '芝2600', 'ダ1000', 'ダ1700', 'ダ2400']
col = ['X', 'Y', 'step']
df_hakodate = pd.DataFrame(index=ind, columns=col)
zahyou = [[10000, 10100, 10000, 10200, 10100, 10150, 10100, 10450, 10200], 
         [1400, 1350, 1350, 1350, 1380, 1380, 1350, 1470, 1470],
         [555, 555, 555, 555, 555, 555, 600, 600, 600]]
df_hakodate['X'] = zahyou[0]
df_hakodate['Y'] = zahyou[1]
df_hakodate['step'] = zahyou[2]

#札幌
ind = ['芝1000', '芝1200', '芝1500', '芝1800', '芝2000', '芝2600', 'ダ1000', 'ダ1700', 'ダ2400']
col = ['X', 'Y', 'step']
df_sapporo = pd.DataFrame(index=ind, columns=col)
zahyou = [[10100, 10100, 10400, 10200, 10100, 10150, 10000, 10400, 10000], 
         [1350, 1350, 1350, 1350, 1320, 1320, 1470, 1470, 1470],
         [680, 670, 665, 680, 680, 680, 750, 750, 750]]
df_sapporo['X'] = zahyou[0]
df_sapporo['Y'] = zahyou[1]
df_sapporo['step'] = zahyou[2]

#福島
ind = ['芝1200', '芝1800', '芝2000', '芝2600', 'ダ1150', 'ダ1700', 'ダ2400']
col = ['X', 'Y', 'step']
df_hukusima = pd.DataFrame(index=ind, columns=col)
zahyou = [[10000, 10250, 10000, 10000, 10300, 10330, 10050], 
         [1370, 1350, 1350, 1350, 1320, 1320, 1320],
         [550, 550, 560, 550, 580, 600, 610]]
        
df_hukusima['X'] = zahyou[0]
df_hukusima['Y'] = zahyou[1]
df_hukusima['step'] = zahyou[2]



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('date', help='input date, (ex 20220723)')
    args = parser.parse_args()

    # 競馬場の座標確認
    date = args.date # 取得日
    os.mkdir("./course/output/"+date)
    race_info = get_url(date)

    key = list(set([i[0] for i in race_info]))

    for i in race_info:
        df = get_df(i[0])
        
        try:
            race_num, race_name, race_course, race_weather, corner, rap, pace, h_num, h_name, jok, h_tuka, h_agari, h_agari_sort = get_info(i[2])
        except AttributeError:
            continue
        try:
            result_image = draw_img(i, race_num, race_name, race_course, race_weather, corner, rap, pace, h_num, h_name, jok, h_tuka, h_agari, h_agari_sort, df)
        except NameError:
            continue


    # title画像作成
    DATE = str(date[0:4]) + "/" + str(date[4:6]) + "/" + str(date[6:])

    for course in key:
        qua = "ダート"

        img = cv2.imread("./blank.jpeg")
        img = cv2.resize(img, dsize=(3946, 2898))
        pil_image = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_image)
        font_path = get_fontpath()


        draw.font = ImageFont.truetype(font_path, 400)  # font設定
        draw.text((750, 1000), DATE, (255, 255, 255))  # pil_imageに直接書き込み
        draw.text((750, 1500), course, (255, 255, 255)) 
        draw.text((1800, 1500), qua, (255, 255, 255)) 

        result_image = np.array(pil_image)
        h, w, _ = result_image.shape

        cv2.imwrite('./course/output/'+course+'_'+qua+'_'+str(DATE.replace('/', ''))+'.png', result_image)

        qua = "芝"

        img = cv2.imread("./blank.jpeg")
        img = cv2.resize(img, dsize=(3946, 2898))
        pil_image = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_image)
        font_path = get_fontpath()


        draw.font = ImageFont.truetype(font_path, 400)  # font設定
        draw.text((750, 1000), DATE, (255, 255, 255))  # pil_imageに直接書き込み
        draw.text((750, 1500), course, (255, 255, 255)) 
        draw.text((1800, 1500), qua, (255, 255, 255)) 

        result_image = np.array(pil_image)
        h, w, _ = result_image.shape

        cv2.imwrite('./course/output/'+course+'_'+qua+'_'+str(DATE.replace('/', ''))+'.png', result_image)
