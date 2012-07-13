ART 			= 'art-default.jpg'
ICON 			= 'icon-default.png'
ICON_MORE		= 'icon-more.png'
NAME 			= L('Title')

baseurl = 'http://www.eredivisielive.nl'
liveurl = baseurl + '/video/'
mijnurl = 'https://mijn.eredivisielive.nl'
loginurl = mijnurl + '/inloggen/'
accounturl = mijnurl + '/account/'

## Todo
# - Add more content? for example VOD --> Only internet abbo's at the moment possible
# - update urluservice with test url
# - Perhaps get video date in there.. see servicecode.pys
####################################################################################################
def Start():

	Plugin.AddPrefixHandler("/video/eredivisielive", MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')

	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)
	
	VideoClipObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:13.0) Gecko/20100101 Firefox/13.0.1'

####################################################################################################
def MainMenu():
	oc = ObjectContainer()

	oc.add(DirectoryObject(key = Callback(getClubs), title=L('Club')))
	oc.add(DirectoryObject(key = Callback(getCompetitie), title=L('Competition')))
	oc.add(DirectoryObject(key = Callback(VideoOnDemand), title=L('Login')))
	oc.add(PrefsObject(title=L('Settings')))
	
	return oc

####################################################################################################
def getClubs():
	oc = ObjectContainer()

	try:
		for team in HTML.ElementFromURL(liveurl).xpath('//div[@id="filter-club-options"]/ul/li/a'):
			club = team.xpath('./span[@class="name"]')[0].text
			 
			if club == 'Geen filter op clubs':
				continue
			teamlink = team.get('href')
			clublogo = team.xpath('./span/img')[0].get('src')	
			clublogo = clublogo.replace('20x20', '100x100')
			competitie=""
			oc.add(DirectoryObject(key = Callback(getVideo, teamlink=teamlink, competitie=competitie), title=club, thumb=clublogo))
	except:
		Log.Exception(L('WebError') + liveurl)

	return oc

####################################################################################################
def getCompetitie():
	oc = ObjectContainer()
	
	try:
		for competities in HTML.ElementFromURL(liveurl).xpath('//div[@id="filter-competition-options"]/ul/li/a'):
			comp = competities.xpath('./span[@class="name"]')[0].text
			if comp == 'Alle competities':
				continue

			competitie = competities.get('href')
		
			teamlink = ""
		
			oc.add(DirectoryObject(key = Callback(getVideo, teamlink=teamlink, competitie=competitie), title=comp))
	except:
		Log.Exception(L('WebError') + liveurl)

	return oc

####################################################################################################
def getVideo(teamlink, competitie, page=1):
	oc = ObjectContainer()
	
	pagestr=str(page)
	if teamlink != "":
		videourl = baseurl + teamlink + "pagina/" + pagestr
	elif competitie != "":
		videourl = baseurl + competitie + "pagina/" + pagestr
		
	content = HTML.ElementFromURL(videourl)
	
	for video in content.xpath('//li[@class="video-item"]'):
		vid_url = video.xpath('./a')[0].get('href')
		vid_url = baseurl + vid_url
		vid_title = video.xpath('./a/span[@class="title"]')[0].text
		thumb = video.xpath('./a/img')[0].get('src')
		
		oc.add(VideoClipObject(
			url = vid_url,
			title = vid_title,
			thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
		))

	if len(oc) == 0:
		return MessageContainer(L('NoVideo'))
		
	else:
		if len(content.xpath('//div[@id="pagination-forward"]')) > 0:
			oc.add(DirectoryObject(key=Callback(getVideo, teamlink=teamlink, competitie=competitie, page=page+1), title=L('More'), thumb=R(ICON_MORE)))
	
	return oc

####################################################################################################
def VideoOnDemand():	
	
	if Prefs['email'] == "" or Prefs['email'] == None:
		oc = ObjectContainer(header = "Login Error", message = "No email adres configured for login")
		return oc
	if Prefs['password'] == "" or Prefs['password'] == None:
		oc = ObjectContainer(header = "Login Error", message = "No password configured for login")
		return oc
		
	Log.Debug('Logging in with')
	Log.Debug(Prefs['email'])
	Log.Debug(Prefs['password'])
	
	content = HTTP.Request(loginurl, values=dict(
				email = Prefs['email'],
				account = "yes",
				password = Prefs['password']
				))
	
	
	#try:
    #   req = HTTP.Request('https://www.youtube.com/', values=dict(
    #        session_token = Dict['Session'],
    #        action_logout = "1"
    #      )) 
	Log.Debug(content)
	
	## post to loginurl needs to contain username and password
	#  keywords = query.replace(" ", "%20")
	#  pageUrl = pageUrl + keywords 
	
	## I will need to make an account before being able to continu
	
	