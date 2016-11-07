import urllib,urllib2,sys,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os,json
import net

AddonID ='plugin.video.off_uktvnow'
fanart = xbmc.translatePath(os.path.join('special://home/addons/' + AddonID , 'fanart.jpg'))
icon = xbmc.translatePath(os.path.join('special://home/addons/' + AddonID, 'icon.png'))
artpath = xbmc.translatePath(os.path.join('special://home/addons/' + AddonID + '/resources/art/'))
dialog = xbmcgui.Dialog()
selfAddon = xbmcaddon.Addon(id=AddonID)
net = net.Net()
user = selfAddon.getSetting('username')
password = selfAddon.getSetting('password')
dialog = xbmcgui.Dialog()

if user == '' or password == '':
        ret = dialog.yesno('UKTV Now', 'Please enter your UKTV Now account details','or register if you dont have an account at','http://uktvnow.net/signup','Cancel','Login')
        if ret == 1:
                keyb = xbmc.Keyboard('', 'Enter Username')
                keyb.doModal()
                if (keyb.isConfirmed()):
                    username = keyb.getText()
                    keyb = xbmc.Keyboard('', 'Enter Password:')
                    keyb.doModal()
                    if (keyb.isConfirmed()):    
                        password = keyb.getText()
                        selfAddon.setSetting('username',username)
                        selfAddon.setSetting('password',password)
        else:quit()      
user = selfAddon.getSetting('username')
password = selfAddon.getSetting('password')

def Login():
        auth=net.http_GET('http://uktvnow.net/app3/index2.php?case=login&username=%s&password=%s'%(user,password)).content
        if 'Invalid' in auth:
                dialog.ok('UKTV Now', 'Invalid username and password provided!','Please check your account details in Add-on settings','')
                sys.exit()
        elif 'not approved' in auth:
                dialog.ok('UKTV Now', 'Your subscription has expired','To renew please login at','http://uktvnow.net/signup')
                sys.exit()
        elif 'inactive' in auth:
                dialog.ok('UKTV Now', 'Your subscription has been suspended','Please contact us at','contact@uktvnow.net')
                sys.exit()
        else:
                authresponse=json.loads(auth)
                session=authresponse["msg"]
                Main(session)

def Main(session):
        cats=net.http_GET('http://uktvnow.net/app3/index2.php?case=get_all_cats&username=%s&sessionID=%s'%(user,session)).content
        catsresponse=json.loads(cats)
        for cat in catsresponse:
                catid=cat["pk_id"]
                catname=cat["name"].replace('.','')
                addDir(catname,catid,1,artpath+catname+'.png',fanart,session)
	xbmc.executebuiltin('Container.SetViewMode(500)')

def GetChannels(url,session):
        chans=net.http_GET('http://uktvnow.net/app3/index2.php?case=get_channel_by_cat&cat_id=%s&username=%s&sessionID=%s'%(url,user,session)).content
        chansresponse=json.loads(chans)
        if not 'http_stream' in chans:
                if 'logged' in chans:dialog.ok('UKTV Now', 'Please re-login to watch channels. We have recieved notification of possible account sharing, continued sharing will result in your IP and account being banned. You can change your password by logging in at http://uktvnow.net/login')
                else:dialog.ok('UKTV Now', 'An error has occurred retrieving channel list','Please contact us at','contact@uktvnow.net')
        else:
                for channels in chansresponse:
                        name=channels["name"]
                        img='http://uktvnow.net/app3/'+channels["img"].replace(' ','%20')
                        chanid=channels["pk_id"]
                        addDir(name,chanid,2,img,fanart,session)
        xbmc.executebuiltin('Container.SetViewMode(500)')

def GetStreams(name,url,iconimage,session):
        chan=net.http_GET('http://uktvnow.net/app3/index2.php?case=get_channel_details&channel_id=%s&username=%s&sessionID=%s'%(url,user,session)).content
        chanresponse=json.loads(chan)
        if 'logged' in chan:dialog.ok('UKTV Now', 'Please re-login to watch channels. We have recieved notification of possible account sharing, continued sharing will result in your IP and account being banned. You can change your password by logging in at http://uktvnow.net/login')
        else:
                chanresponse=chanresponse["msg"]
                streamname=chanresponse["name"]
                http=chanresponse["http_stream"]
                rtmp=chanresponse["rtmp_stream"]
                streamurl=[]
                streamname=[]
                streamurl=[]
                streamurl.append(http)
                streamurl.append(rtmp)
                streamname.append('Stream 1 (http)')
                streamname.append('Stream 2 (rtmp)')
                select = dialog.select(name,streamname)
                if select == -1:return
                else:
                        url=streamurl[select]
                        if 'rtmp' in url: url = url+' timeout=10'
                        ok=True
                        liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage); liz.setInfo( type="Video", infoLabels={ "Title": name } )
                        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
                        xbmc.Player().play(url, liz, False)
                        return ok
 
def addDir(name,url,mode,iconimage,fanart,session=''):
		u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&session="+str(session)
		ok=True
		liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
		liz.setInfo( type="Video", infoLabels={ "Title": name})
		liz.setProperty('fanart_image', fanart)
		if mode==1:isFolder=True
		else:isFolder=False
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isFolder)
		return ok

def get_params():
		param=[]
		paramstring=sys.argv[2]
		if len(paramstring)>=2:
				params=sys.argv[2]
				cleanedparams=params.replace('?','')
				if (params[len(params)-1]=='/'):params=params[0:len(params)-2]
				pairsofparams=cleanedparams.split('&')
				param={}
				for i in range(len(pairsofparams)):
						splitparams={}
						splitparams=pairsofparams[i].split('=')
						if (len(splitparams))==2:param[splitparams[0]]=splitparams[1]	
		return param
		   
params=get_params()
url=None
name=None
mode=None
iconimage=None
session=None

try:url=urllib.unquote_plus(params["url"])
except:pass
try:name=urllib.unquote_plus(params["name"])
except:pass
try:mode=int(params["mode"])
except:pass
try:iconimage=urllib.unquote_plus(params["iconimage"])
except:pass
try:session=str(params["session"])
except:pass

if mode==None or url==None or len(url)<1:Login()#Main()
elif mode==1:GetChannels(url,session)
elif mode==2:GetStreams(name,url,iconimage,session)
elif mode==3:Schedule(url)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
