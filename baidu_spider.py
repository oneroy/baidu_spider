#! /usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        baidu_spider
# Purpose:     搜索指定文件里面的多个baidu关键词并保存baidu的搜索结果
#更新：文件名带Host，文件包含指定关键词
# Author:      oneroy
# Created:     2016-07-19
# Copyright:   (c) roy 2016
#-------------------------------------------------------------------------------
import sys, gzip,StringIO
import httplib
import urllib
import urllib2
import urlparse
import os
import getopt
import traceback
from bs4 import BeautifulSoup
import threading

##sys.argv = ["detect.py","http://202.204.193.211/jiaowu/zpx/szwyadmin/admin_index.asp","G:\\Test\\Spider\\baidufile\\detect.txt"]

urllib2.socket.setdefaulttimeout(55)

inFile=open('baidu_key.txt','r')
outFile=open('baidu_key_url.txt','a+')

def data_tag(data,foretag,endtag):
##    print ('foretag,endtag',foretag,endtag)
    data = data + os.linesep
    start=data.find(foretag)
    if start == -1:
        return ""
    else:
        start+=len(foretag)
##    print ('start',start)
    end=data[start:].find(endtag)
##    print 'end',end
    if end == -1:
        end = data[start:].find(os.linesep)
    end += start
    return data[start:end]

def down_file(url):
##    filename = url.split('/')[-1]
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = os.path.basename(path)
    if not filename:
       filename = 'downloaded.file'
    print ('netloc,filename',netloc,filename)
    if filename.find('.pdf') == -1  and filename.find('.xls') == -1:
        print 'File is not pdf or xls!!!!!!'
        return
    u = urllib2.urlopen(url)
    writeFilename = "baiduFile\\" + netloc + "_." + filename
    f = open(writeFilename, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
    f.close()


#测试URL
def DownloadByUrl(Url,isHttps,isLocation,isCookie,Cookie,isPost,PostData,isPut,PutData):
    print ('Url========,isHttps',Url,isHttps)
    Port = 80
    Url0 = Url[7:]
    if isHttps == True:
         Url0 = Url[8:]
    HostAddress = Host = Url0.split('/')[0]
    Uri = Url0[len(Host):]
    Uri = Uri.replace(' ','%20')  #zimbra存在该问题
    if Host.find('wenku.baidu.com') != -1  or Host.find('docin.com') != -1: #去除baidu文库和豆丁网
        return 0
    if Host.find(':') !=  -1:
        Port = (int) (Host.split(':')[1])
        HostAddress = Host.split(':')[0]
    print('HostAddress,Port,Uri,Cookie',HostAddress,Port,Uri,Cookie)
    try:
        if isHttps == True:
            conn = httplib.HTTPSConnection(HostAddress,timeout=55)
        else:
            conn = httplib.HTTPConnection(HostAddress,Port,None,55)
        if isCookie == True:
            headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; .NET4.0E)",
            "Accept": "text/html, application/x-ms-application, image/jpeg, application/xaml+xml, image/gif, image/pjpeg, application/x-ms-xbap, */*",
            "Host": Host,
            "Connection": "Keep-Alive",
            "Accept-Language": "zh-CN",
            "Accept-Encoding": "gzip, deflate",
            'Cookie': Cookie
            }
            conn.request('GET', Uri, None,headers)
            res = conn.getresponse()
        elif isPost == True:
            headers = {
                "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)",
                "Accept": "*/*",
                "Accept-Language": "zh-CN",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept-Encoding": "gzip, deflate",
                "Host": Host,
                "Content-Length": len(PostData),
                "Connection": "Keep-Alive",
                "Cache-Control": "no-cache"
            }
            print('Url,PostData,headers',Url,PostData,headers)
            req = urllib2.Request(Url,PostData,headers)
            cj=cookielib.CookieJar()
            opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            res =opener.open(req)
##            the_page =res.read()
##            print the_page
        elif isPut == True:
            headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; .NET4.0E)",
            "Accept": "text/html, application/x-ms-application, image/jpeg, application/xaml+xml, image/gif, image/pjpeg, application/x-ms-xbap, */*",
            "Host": Host,
            "Connection": "Keep-Alive",
            "Accept-Language": "zh-CN",
            "Accept-Encoding": "gzip, deflate"
            }
            conn.request("PUT", Uri, PutData , headers)
            res = conn.getresponse()
        else:
            headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; .NET4.0E)",
            "Accept": "text/html, application/x-ms-application, image/jpeg, application/xaml+xml, image/gif, image/pjpeg, application/x-ms-xbap, */*",
            "Host": Host,
            "Connection": "Keep-Alive",
            "Accept-Language": "zh-CN",
            "Accept-Encoding": "gzip, deflate"
            }
            conn.request('GET', Uri, None,headers)
            res = conn.getresponse()
        data = ""
        if isPost == True:
            print ('res.info()',str(res.info()))
            if str(res.info()).find("gzip")!=-1:
                print 'ggggg--gzip'
                data0 = res.read()
                compressedstream = StringIO.StringIO(data0)
                gzipper = gzip.GzipFile(fileobj=compressedstream)
                data = gzipper.read()
            else:
                data = res.read()
            res.close()
            conn.close()
            print 'data is:-----------',data
        else:
            resStatus = res.status
            print 'res.status',resStatus
            if resStatus == 302 and isLocation == False:
                newUrl = ''
                for item in res.getheaders():
                    if item[0]=='location' or item[0]=='Location':
                        newUrl = item[1]
                        if 'http' not in newUrl:
                            Lurl = item[1]
                            newUrl = Url.replace(Url.rsplit('/')[-1],Lurl)
                        print ('newUrl',newUrl)
                        lock.acquire()
                        outFile.write(newUrl +'\n')
                        lock.release()
                        return DownloadByUrl(newUrl,isHttps,True, isCookie,Cookie,False,PostData,isPut,PutData)
            if 400 <= resStatus <500:
                print '4XX Fail-------'
                return 0
            resMsg = res.msg
            pageLength = resMsg["content-length"]
            print ('pageLength',pageLength)
            #r.headers.get('content-length')
            if int(pageLength)>8388608 or int(pageLength)<8192:
                print 'pageLength > 1MB or < 10KB',pageLength
                return 0
            resMsg = str(resMsg)
            print 'res.msg',resMsg
            if str(resMsg).find("gzip")!=-1:
    ##            print 'ggggg--gzip'
                data0 = res.read()
                compressedstream = StringIO.StringIO(data0)
                gzipper = gzip.GzipFile(fileobj=compressedstream)
                data = gzipper.read()
            else:
                data = res.read()
            conn.close()
    # 不需要下载的时候下面这行注释掉
##        down_file(Url)
        return 1

    except Exception, e:
        print 'Exception Fail-------'
        print(traceback.format_exc())
        return 0




lock=threading.Lock()

def test():
    while True:
        lock.acquire()
        line=inFile.readline().strip()
        lock.release()
        if len(line)==0:break
        print 'line',line,
        question_word = line.split('|')[0]
        pageNum  = int(line.split('|')[1])
        print 'question_word,pageNum',question_word,pageNum
        try:
            url_list = []
            i = 0
            while (i < pageNum):
                baiduPageNum = str(pageNum * i)
    ##            baiduUrl = "http://www.baidu.com/s?wd=" + urllib.quote(question_word.encode('gbk')) + "&pn=" + baiduPageNum
                baiduUrl = "http://www.baidu.com/s?wd=" + urllib.quote(question_word.encode('utf8')) + "&pn=" + baiduPageNum
                print 'baiduUrl',baiduUrl
                i = i + 1
                url_list.append(baiduUrl)

            for url in url_list:
    ##            url = "http://www.baidu.com/s?wd=" + urllib.quote(question_word.encode('gbk'))
                print url
                try:
                    htmlpage = urllib2.urlopen(url).read()
                    soup = BeautifulSoup(htmlpage)
                    ##print htmlpage
                    print len(soup.findAll("h3", class_="t"))
                    for result_table in soup.findAll("h3", class_="t"):
                    ##    print 'baidu_r',result_table
                    ##    print "-----标题----\n" + baiduResult.renderContents()#标题
                        baiduUrl = data_tag(str(result_table),"href=\"","\" target")
                        print u"链接-----\n"  + baiduUrl
                    ##    urllib.urlretrieve(baiduUrl, filename)
                        if DownloadByUrl(baiduUrl,False,False,False,'',False,'',False,'') == 1:
                            print 'ok,down ok'
                except Exception, e:
                    print 'Exception Fail-------'
                    print(traceback.format_exc())
                    continue
        except Exception,e:
            print e

all_thread=[]
for i in range(50):
    t = threading.Thread(target=test)
    all_thread.append(t)
    t.start()

for t in all_thread:
    t.join()

inFile.close()
outFile.close()
