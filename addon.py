import re
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import urllib2
import urlparse
import requests
import html5lib
from bs4 import BeautifulSoup


addon = xbmcaddon.Addon()
language = addon.getLocalizedString
handle = int(sys.argv[1])
url_rivedi="http://www.la7.it/rivedila7/0/la7"
url_rivedila7d="http://www.la7.it/rivedila7/0/la7d"
url_tutti_programmi="http://www.la7.it/programmi"
url_live="http://www.la7.it/dirette-tv"
url_base="http://www.la7.it"    
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'}
pagenum=0


def parameters_string_to_dict(parameters):
    paramDict = dict(urlparse.parse_qsl(parameters[1:]))
    return paramDict


def show_root_menu():
    ''' Show the plugin root menu '''
    liStyle = xbmcgui.ListItem(language(32002))
    addDirectoryItem({"mode": "diretta_live"},liStyle)
    liStyle = xbmcgui.ListItem(language(32001))
    addDirectoryItem({"mode": "rivedi_la7"},liStyle)
    liStyle = xbmcgui.ListItem(language(32004))
    addDirectoryItem({"mode": "rivedi_la7d"},liStyle)
    liStyle = xbmcgui.ListItem(language(32006))
    addDirectoryItem({"mode": "tutti_programmi"},liStyle)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def addDirectoryItem(parameters, li):
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=handle, url=url, 
        listitem=li, isFolder=True)


def rivedi_la7():
    req = urllib2.Request(url_rivedi,headers=headers) 
    page=urllib2.urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    giorno=html.find(id="giorni").find_all('div' ,class_='giorno')
    if giorno is not None:
        for div in giorno[0:]:
            dateDay=div.find('div',class_='dateDay')
            dateMonth=div.find('div',class_='dateMonth')
            dateRowWeek=div.find('div',class_='dateRowWeek')
            a=div.a.get('href')
            liStyle = xbmcgui.ListItem(dateRowWeek.contents[0]+" "+dateDay.contents[0]+" "+dateMonth.contents[0])
            addDirectoryItem({"mode": "rivedi_la7","giorno": a}, liStyle)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def rivedi_la7d():
    req = urllib2.Request(url_rivedila7d,headers=headers) 
    page=urllib2.urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    giorno=html.find(id="giorni").find_all('div' ,class_='giorno')
    
    if giorno is not None:
        for div in giorno[0:]:
            dateDay=div.find('div',class_='dateDay')
            dateMonth=div.find('div',class_='dateMonth')
            dateRowWeek=div.find('div',class_='dateRowWeek')
            a=div.a.get('href')
            liStyle = xbmcgui.ListItem(dateRowWeek.contents[0]+" "+dateDay.contents[0]+" "+dateMonth.contents[0])
            addDirectoryItem({"mode": "rivedi_la7d","giorno": a}, liStyle)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def get_video_link(url):
    req = urllib2.Request(url,headers=headers) 
    page=urllib2.urlopen(req)
    html=page.read();
    res=re.findall('m3u8" : "(.*?)"', html)
    if res:
        return res[0]
    else:
        res=re.findall('m3u8: "(.*?)"', html)
        if res:
            return res[0]


def play_video(video,live):

    if live:
        s = requests.Session()
        req = s.get(video,headers=headers)
        html = req.text
        vS = re.findall('var vS = \'(.*?)\';', html)
        try:
            link_video = vS[0]
        except: # catch *all* exceptions
            e = sys.exc_info()[0]
            xbmc.log('EXCEP VIDEO: '+str(e),xbmc.LOGNOTICE)
    if not live and "tg.la7.it" in video:
        req = urllib2.Request(video,headers=headers) 
        page=urllib2.urlopen(req)
        html=BeautifulSoup(page,'html5lib')
        if html.find("iframe"):
            video=html.find("iframe")['src']
    if not live and  "la7.it" in video:
        link_video=get_video_link(video)
    elif not live:
        link_video=get_video_link(url_base+video)
    listitem =xbmcgui.ListItem(titolo_global)
    listitem.setInfo('video', {'Title': titolo_global})
    if (thumb_global != ""):
        listitem.setArt({ 'thumb': thumb_global})
    listitem.setInfo('video', { 'plot': plot_global })
    xbmc.Player().play(link_video, listitem)


def rivedi_la7_giorno():
    req = urllib2.Request(url_base+giorno,headers=headers) 
    page=urllib2.urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    guida_tv=html.find(id="content_guida_tv").find_all('div' ,class_='disponibile')
    if guida_tv is not None:
        for div in guida_tv:
            nome=div.find('div',class_='titolo clearfix').a.contents[0].encode('utf-8')
            thumb=div.find('img')['src']
            plot=div.find('div',class_='descrizione').p.contents[0]
            urll=div.find('div',class_='titolo').a.get('href')
            orario=div.find('div',class_='orario').contents[0].encode('utf-8')
            liStyle = xbmcgui.ListItem(orario+" "+nome)
            liStyle.setArt({ 'thumb': thumb})
            liStyle.setInfo('video', { 'plot': plot })
            url2 = sys.argv[0] + '?' + urllib.urlencode({"mode": "rivedi_la7","play": urll,"titolo": nome,"thumb":thumb,"plot":plot.encode('utf-8')})
            xbmcplugin.addDirectoryItem(handle=handle, url=url2,listitem=liStyle, isFolder=False)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def rivedi_la7d_giorno():
    req = urllib2.Request(url_base+giorno,headers=headers) 
    page=urllib2.urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    guida_tv=html.find(id="content_guida_tv").find_all('div' ,class_='disponibile')
    if guida_tv is not None:
        for div in guida_tv:
            nome=div.find('div',class_='titolo clearfix').a.contents[0].encode('utf-8')
            thumb=div.find('img')['src']
            plot=div.find('div',class_='descrizione').p.contents[0]
            urll=div.find('div',class_='titolo').a.get('href')
            orario=div.find('div',class_='orario').contents[0].encode('utf-8')
            liStyle = xbmcgui.ListItem(orario+" "+nome)
            liStyle.setArt({ 'thumb': thumb})
            liStyle.setInfo('video', { 'plot': plot })
            url2 = sys.argv[0] + '?' + urllib.urlencode({"mode": "rivedi_la7d","play": urll,"titolo": nome,"thumb":thumb,"plot":plot.encode('utf-8')})
            xbmcplugin.addDirectoryItem(handle=handle, url=url2,listitem=liStyle, isFolder=False)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

        
# Raggruppamento Programmi per lettera (A-B-C.....)
# def tutti_programmi():
    # req = urllib2.Request(url_tutti_programmi,headers=headers) 
    # page=urllib2.urlopen(req)
    # html=BeautifulSoup(page,'html5lib')        
    # lettere=html.find(id='colSx').find('div',class_='view-content').find_all('h3')
    # if lettere is not None:
        # i=0;
        # for h3 in lettere:
            # liStyle = xbmcgui.ListItem(lettere[i].contents[0])
            # addDirectoryItem({"mode": "tutti_programmi","lettera": lettere[i].contents[0]}, liStyle)
            # i=i+1
        # xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def programmi_lettera():
    req = urllib2.Request(url_tutti_programmi,headers=headers) 
    page=urllib2.urlopen(req)
    html=BeautifulSoup(page,'html5lib') 
    programmi=html.find(id='colSx').find_all('div',class_='element_menu')
    #xbmc.log(str(programmi),xbmc.LOGNOTICE)	
    if programmi is not None:
        for dati in programmi:
            titolo=dati.find('span',class_='black_overlay').contents[0].encode('utf-8').lstrip()
            #xbmc.log('TITLE: '+str(titolo),xbmc.LOGNOTICE)	
            liStyle = xbmcgui.ListItem(titolo)
            url_trovato=dati.a.get('href')
            if url_trovato == '/facciaafaccia':
                url_trovato='/faccia-a-faccia'
            link=url_base+url_trovato
            #xbmc.log("LINK1: "+str(link),xbmc.LOGNOTICE)
            img=dati
            if(len(img)>0):
                #xbmc.log('IMG: '+str(img),xbmc.LOGNOTICE)
                try:
                    thumb=img.find('img')['src']
                except: # catch *all* exceptions
                    e = sys.exc_info()[0]
                    xbmc.log('EXCEP THUMB: '+str(e),xbmc.LOGNOTICE)
                    thumb = None
                if thumb is not None:
                    #xbmc.log('THUMB: '+str(thumb),xbmc.LOGNOTICE)
                    liStyle.setArt({ 'thumb': thumb})
                else:
                    xbmc.log('NO THUMB',xbmc.LOGNOTICE)     
            addDirectoryItem({"mode": "tutti_programmi","link": link}, liStyle)
        xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def video_programma():
    req = urllib2.Request(link_global+"/rivedila7/archivio?page="+str(pagenum),headers=headers)
    try:
        page=urllib2.urlopen(req)   
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        xbmc.log('EXCEP URL: '+str(e),xbmc.LOGNOTICE)
        return
    html=BeautifulSoup(page,'html5lib')
    if pagenum==0:
        firstLa7=html.find('div',class_='contenitoreUltimaReplicaLa7')
        firstLa7d=html.find('div',class_='contenitoreUltimaReplicaLa7d')
        if firstLa7 is not None:
            first=firstLa7
        elif firstLa7d is not None:
            first=firstLa7d
        else:    
            if xbmcgui.Dialog().ok(addon.getAddonInfo('name'), language(32005)):
                return
        thumb=first.find('div',class_='kaltura-thumb').find('img')['src']
        titolo=first.find('div',class_='title').text.encode('utf-8')
        plot=first.find('div',class_='views-field-field-testo-lancio').find('p').text.encode('utf-8')
        link=url_base+first.find('a',class_='clearfix').get('href')
        #xbmc.log('LINK2: '+str(link),xbmc.LOGNOTICE)
        liStyle = xbmcgui.ListItem(titolo)
        liStyle.setArt({ 'thumb': thumb})
        liStyle.setInfo('video', { 'plot': plot })
        addDirectoryItem({"mode": "tutti_programmi","play": link,"titolo": titolo,"thumb":thumb,"plot":plot}, liStyle)
        ul=html.find('li',class_='switchBtn settimana')
        if ul is not None:
            req2= urllib2.Request(link_global+"/rivedila7",headers=headers)
            page2=urllib2.urlopen(req2)
            html2=BeautifulSoup(page2,'html5lib')
            video2=html2.find(id='block-la7it-repliche-la7it-repliche-contenuto-tid').find_all('div',class_='views-row')
            if video2 is not None:
                get_rows_video(video2)
    video=html.find(id='block-la7it-repliche-la7it-repliche-contenuto-tid').find_all('div',class_='views-row')
    if video is not None:
        get_rows_video(video)
        liStyle = xbmcgui.ListItem(language(32003))
        addDirectoryItem({"mode": "tutti_programmi","link":link_global,"page":pagenum+1}, liStyle)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def get_rows_video(video):
    for div in video:
        thumb=div.find('div',class_='kaltura-thumb').find('img')['data-src']            
        titolo=div.find('div',class_='title').a.text.encode('utf-8')
        plot=div.find('div',class_='views-field-field-testo-lancio').text.encode('utf-8')
        link=url_base+div.find('a',class_='thumbVideo').get('href')
        liStyle = xbmcgui.ListItem(titolo)
        liStyle.setArt({ 'thumb': thumb})
        liStyle.setInfo('video', { 'plot': plot })
        addDirectoryItem({"mode": "tutti_programmi","play": link,"titolo": titolo,"thumb":thumb,"plot":plot}, liStyle)

        
        
        
        
        
# Main             
params = parameters_string_to_dict(sys.argv[2])
mode = str(params.get("mode", ""))
giorno = str(params.get("giorno", ""))
play=str(params.get("play", ""))
titolo_global=str(params.get("titolo", ""))
thumb_global=str(params.get("thumb", ""))
plot_global=str(params.get("plot", ""))
#lettera_global=str(params.get("lettera", ""))
link_global=str(params.get("link", ""))


if params.get("page", "")=="":
    pagenum=0;
else:
    pagenum=int(params.get("page", ""))

if mode=="rivedi_la7":
    if play=="":
        if giorno=="":
            rivedi_la7()
        else:
            rivedi_la7_giorno()
    else:
        play_video(play,False)

elif mode=="rivedi_la7d":
    if play=="":
        if giorno=="":
            rivedi_la7d()
        else:
            rivedi_la7d_giorno()
    else:
        play_video(play,False)

elif mode=="tutti_programmi":
    if play=="":
        if link_global=="":
            # if lettera_global=="":
                # tutti_programmi()
            # else:
            programmi_lettera()
        else:
            video_programma()
    else:
        play_video(play,False)

elif mode=="diretta_live":
    titolo_global=language(32002)
    thumb_global=""
    play_video(url_live,True)

else:
    show_root_menu()
    



    
