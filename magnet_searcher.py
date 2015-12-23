#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import time
import threading
import random
import urllib
import urllib2
from lxml.html import soupparser
import bs4
import webbrowser
import chardet


filecoding="utf-8"
syscoding=sys.getfilesystemencoding()


d_switchflag={
        'btdb':         1,
        'btbook':       1,
        'torrentkitty': 1
        }
d_parsefunc={
        'btdb':         "parse_btdb",
        'btbook':       "parse_btbook",
        'torrentkitty': "parse_torrentkitty"
        }
d_recordname={
        'btdb':         "l_record_btdb",
        'btbook':       "l_record_btbook",
        'torrentkitty': "l_record_torrentkitty"
        }


header1 = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6','Accept':'text/html;q=0.9,*/*;q=0.8','Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3'}
header2 = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5'}
header3 = {'User-Agent':'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}
header4 = {'User-Agent:':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'}
l_header = [header1, header2, header3, header4]


class Record():
        ''' search result recode '''
        def __init__(self, resite, title, magnet, size, nfile, ndownload):
                self.resite=resite
                self.title=title
                self.magnet=magnet
                self.size=size
                self.nfile=nfile
                self.ndownload=ndownload

        def showinfo(self):
                print "%s: %s" % (self.title,self.magnet)
                print "resource site: %s\tsize: %s\tfile number:%s\tdownload count: %s" % (self.resite, self.size, self.nfile, self.ndownload)

def parse_btdb(keyword, request_header):
        ''' function search from btdb '''
        global l_record_btdb
        l_record_btdb=[]

        request_url="http://btdb.in/q/%s/"%urllib.quote(keyword.decode(filecoding).encode('utf-8'))       #编码方式安个站点的编码定
        print request_url

        request=urllib2.Request(request_url, headers=request_header)
        try:
                conn=urllib2.urlopen(request, timeout=30)
        except Exception:
                print "Error: connect %s failed!" % request_url
                return
        html=conn.read().decode('utf-8').encode(filecoding)
        conn.close()

        fd=open("result_btdb.html", "w")
        fd.write(html)

        dom=soupparser.BeautifulSoup(html)
        l_soupitem=dom.findAll("li", attrs={"class":"search-ret-item"})
        if l_soupitem == None:
               return
        for i in l_soupitem:
                title=i.find("h2", attrs={"class":"item-title"}).find("a").get("title")
                magnet=i.find("div").find("a", attrs={"class":"magnet"}).get("href")
                l_info=i.findAll("span", attrs={"class":"item-meta-info-value"})
                size=l_info[0].text             #大小 文件数 (创建时间) 下载热度
                nfile=l_info[1].text
                ndownload=l_info[-1].text
                record=Record("BTDB", title, magnet, size, nfile, ndownload)
                l_record_btdb.append(record)

def parse_btbook(keyword, request_header):
        ''' function search from btbook '''
        global l_record_btdb
        global l_record_btbook
        l_record_btbook=[]

        request_url="http://www.btbook.net/search/%s.html"%urllib.quote(keyword.decode(filecoding).encode('utf-8'))       #编码方式安个站点的编码定
        print request_url

        request=urllib2.Request(request_url, headers=request_header)
        try:
                conn=urllib2.urlopen(request, timeout=30)
        except Exception:
                print "Error: connect %s failed!" % request_url
                return
        html=conn.read().decode('utf-8').encode(filecoding)
        conn.close()

        fd=open("result_btbook.html", "w")
        fd.write(html)

        dom=soupparser.BeautifulSoup(html)
        l_soupitem=dom.findAll("div", attrs={"class":"search-item"})
        if l_soupitem == None:
               return
        for i in l_soupitem[1:]:                #l_soupitem[0] : advertisement
                title=i.find("h3").find("a").text
                l_info=i.find("div", attrs={"class":"item-bar"}).findAll("span")
                size=l_info[2].b.text           #文件格式 创建时间 大小 下载热度 最近下载时间
                nfile="--"
                ndownload=l_info[3].b.text
                magnet=i.find("div", attrs={"class":"item-bar"}).findAll("a", attrs={"class":"download"})[0].get("href")    #磁力链接 迅雷链接
                record=Record("BTBOOK", title, magnet, size, nfile, ndownload)
                l_record_btbook.append(record)

def parse_torrentkitty(keyword, request_header):
        ''' function search from torrentkitty '''
        global l_record_torrentkitty
        l_record_torrentkitty=[]

        request_url="http://www.torrentkitty.net/search/%s"%urllib.quote(keyword.decode(filecoding).encode('utf-8'))       #编码方式安个站点的编码定
        print request_url

        request=urllib2.Request(request_url, headers=request_header)
        try:
                conn=urllib2.urlopen(request, timeout=30)
        except Exception:
                print "Error: connect %s failed!" % request_url
                return
        html=conn.read().decode('utf-8').encode(filecoding)
        conn.close()

        fd=open("result_torrentkitty.html", "w")
        fd.write(html)

        dom=soupparser.BeautifulSoup(html)
        l_soupitem=dom.find("div", attrs={"id":"main"}).find("div", attrs={"class":"wrapper"}).find("table", attrs={"id":"archiveResult"}).findAll("tr")
        if l_soupitem == None:
               return
        for i in l_soupitem[1:]:
                l_info=i.findAll("td")
                title=l_info[0].text            #名称 torrent大小 创建时间 链接
                size="--"
                nfile="--"
                ndownload="--"
                magnet=l_info[-1].findAll("a")[1].get("href")
                record=Record("TorrentKitty", title, magnet, size, nfile, ndownload)
                l_record_torrentkitty.append(record)

def create_html(l_record):
        ''' create a results html page '''
        fd_htmlbase=open("base.html", "r")
        fd_htmlresult=open("magnet_search_result.html", "w")
        dom=bs4.BeautifulSoup(fd_htmlbase, "lxml")
        fd_htmlbase.close()

        count=len(l_record)

        dom_tbody=dom.find("tbody")            #到达第一行新增处
        for (key, value) in enumerate(l_record):
                tag_tr=dom.new_tag("tr")       #新增行
                dom_tbody.insert(0, tag_tr)

                dom_tbody_tr=dom_tbody.find("tr")

                tag_th=dom.new_tag("th")       #索引列
                tag_th.string=str(count-key)
                dom_tbody_tr.insert(0, tag_th)

                tag_title=dom.new_tag("td")    #标题列
                tag_title.string=value.title
                dom_tbody_tr.insert(1, tag_title)

                tag_size=dom.new_tag("td")    #文件大小
                tag_size.string=value.size
                dom_tbody_tr.insert(2, tag_size)

                tag_nfile=dom.new_tag("td")    #文件数
                tag_nfile.string=value.nfile
                dom_tbody_tr.insert(3, tag_nfile)

                tag_ndownload=dom.new_tag("td")    #热度
                tag_ndownload.string=value.ndownload
                dom_tbody_tr.insert(4, tag_ndownload)

                tag_resite=dom.new_tag("td")    #来源
                tag_resite.string=value.resite
                dom_tbody_tr.insert(5, tag_resite)

                tag_magnet=dom.new_tag("td")    #磁力链接
                tag_magnet["class"]="magnet"    #加入class属性 方便下一层插入
                dom_tbody_tr.insert(6, tag_magnet)

                dom_tbody_tr_tdmagnet=dom_tbody_tr.find("td", attrs={"class":"magnet"}) #找到magent列标签
                tag_magnet_a=dom.new_tag("a", href=value.magnet)
                tag_magnet_a.string="下载".decode(filecoding).encode(syscoding)
                dom_tbody_tr_tdmagnet.insert(0, tag_magnet_a)

        fd_htmlresult.write(str(dom))
        fd_htmlresult.close()
        #webbrowser.open("file://"+os.getcwd()+"/magnet_search_result.html")
        #webbrowser.open("magnet_search_result.html", new=2)

def main():
        print 'Filecoding: ', filecoding
        print 'Syscoding: ', syscoding
        sys.stdout.write("Keywords: ")
        keyword=sys.stdin.readline()[:-1].decode(syscoding).encode(filecoding)
        #print chardet.detect(keyword)
        print keyword

        time_begin=time.time()

        l_thread=[]
        for k in d_switchflag:
                #print k, d_switchflag[k]
                if d_switchflag[k]==0:
                        print "!run %s" % d_parsefunc[k]
                        continue
                print "run %s" % d_parsefunc[k]
                request_header=random.choice(l_header)
                #print request_header
                t=threading.Thread(target=eval(d_parsefunc[k]), args=(keyword, request_header))
                l_thread.append(t)

        for i in l_thread:
                i.start()
        for i in l_thread:
                i.join()

        time_end=time.time()

        l_record=[]
        for k in d_switchflag:
                if d_switchflag[k]==0:
                        continue
                l_record+=eval(d_recordname[k])
                print "result record add: %s" % d_recordname[k]

        time_takes=time_end-time_begin
        #for i in l_record:
        #        i.showinfo()
        print ("result: %s" % len(l_record)).decode(filecoding).encode(syscoding)
        print ("time: %sS" % time_takes)

        create_html(l_record)
        exit()

if __name__=='__main__':
        main()
