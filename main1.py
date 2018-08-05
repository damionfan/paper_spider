import time
import re
import urllib
import csv
from urllib import request
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver


#解决重定向问题
def secvector(baseurl):
    display = Display(visible=0, size=(800, 600))
    display.start()

    # 现在Chrome会运行在一个虚拟的屏幕之中.
    # 你看不到它.
    browser = webdriver.Chrome('/home/milk/Downloads/chromedriver')
    browser.implicitly_wait(30)
    browser.get(baseurl)
    redirected_url = browser.current_url
    browser.quit()
    display.stop()
    if redirected_url:
        return redirected_url
    return None

#寻找目的文章链接
def find_realtext(contents):
    icons = contents.find(name='div',attrs={'class':'icons portlet'})
    alink = icons.find_all('a')
    flag = 0
    for a in alink:
        if flag == 0:
            link = a.get('href')
            #print(link)
            rellink = secvector(link)
            print(rellink)
        flag+=1


def write_csv(dic,lable):
    with open('data.csv','a',encoding='utf-8') as csvfile:
        fieldnames=['lable','title','years','auth','abstract']
        dic['lable'] = lable
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writerow(dic)


#请求函数，请求网页获取网页内容
def respose(lable):
    baseurl = 'https://www.ncbi.nlm.nih.gov/pubmed/?term='
    host_web = 'https://www.ncbi.nlm.nih.gov'
    dict = {}
    for lab in lable:
        url = baseurl+lab
        content = request.urlopen(url)
        con = content.read()
        soup = BeautifulSoup(con,"lxml") #解析网页内容
        #print(soup)  #测试发现国内能够访问
        rprt= soup.find_all(name='div',attrs={'class':'rprt'})
        for rpr  in rprt:
            rslt = rpr.find(name='div',attrs={'class':'rslt'})
            a = rslt.find('a')
            link = a.get('href')
            #访问页面详细信息，以获取论文名 论文作者 论文发表时间 论文摘要 以及是否可以摘取论文的文本内容
            details = request.urlopen(host_web+link)
            detail = details.read()
            soup_detail  = BeautifulSoup(detail,'lxml')
            contents = soup_detail.find(name='div',attrs={'class':'rprt_all'})
            #提取论文题目
            h1 = contents.find('h1')
            #print(h1)
            titles = re.sub('<h1>|<i>|</i>|</h1>','',str(h1),re.S)
            #print(titles)
            dict['title'] = titles
            #提取作者名称
            auth = contents.find(name='div', attrs={'class': "auths"})
            auth = re.sub('<sup>|</sup>', '', str(auth))
            auth = re.sub('<div .*?>|<a .*?>|</div>|</a>|\d+', '', auth)
            dict['auth'] = auth
            #print(auth)
            #摘取摘要信息
            abstr = contents.find(name='div',attrs={'class':'abstr'})
            if abstr:
                #abstract = abstr.find('p')
                ab = re.sub('Abstract|</div>|<div .*?>|<h4>|<h3>|</h4>|</h3>|<p>|</p>|<i>|</i>|<sup>|</sup>|-/-|</p>', '', str(abstr))
                dict['abstract'] = ab
                #print(ab)
            else:
                dict['abstract'] = "Can't find  abstract!"
                #print("Can't find  abstract!\n",)
            #年份
            years = contents.find(name='div', attrs={'class': 'cit'})
            # print(years)
            years = re.sub('<div class="cit">.*?</a>|;.*?</div>|:.*?</div>', '', str(years))
            years = re.sub('\. pii|\. doi', '', years)
            dict['years'] = years
            #write_csv(dict,lab)
    #寻找论文文本
            rellink = find_realtext(soup_detail)

            print(rellink)



if __name__ == '__main__':
    lable=[]
    lable.append('ABCA4')
    #lable.append('c.123A>G (p.D41N)')
    respose(lable)