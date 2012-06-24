ART 			= 'art-default.png'
ICON 			= 'icon-default.png'
ICON_MORE		= 'icon-more.png'
NAME 			= L('Title')

baseurl = 'http://www.eredivisielive.nl'
liveurl = baseurl + '/video/'

## Todo
# - fix competitie function
# - Add more content?
# - Check strings

####################################################################################################
def Start():

	Plugin.AddPrefixHandler("/video/eredivisielive", MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')

	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)
	
	DirectoryItem.thumb = R(ICON)

	VideoClipObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:8.0) Gecko/20100101 Firefox/8.0'

####################################################################################################
def MainMenu():
	oc = ObjectContainer()

	oc.add(DirectoryObject(key = Callback(getClubs), title=L('Club')))
	oc.add(DirectoryObject(key = Callback(getCompetitie), title=L('Competition')))
	
	return oc
		
####################################################################################################
def getClubs():
	oc = ObjectContainer()

	### TRY staat uit totdat het goed werkt daarna aanzetten en indenten
	#try:
	for team in HTML.ElementFromURL(liveurl).xpath('//div[@id="filter-club-options"]/ul/li/a'):
		club = team.xpath('./span[@class="name"]')[0].text
		if club == 'Geen filter op clubs':
			continue
		teamlink = team.get('href')
			
		competitie=""
		oc.add(DirectoryObject(key = Callback(getVideo, teamlink=teamlink, competitie=competitie), title=club))
	#except:
	#	Log(L('WebError') + liveurl)

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
		Log(L('WebError') + liveurl)

	return oc

####################################################################################################
def getVideo(teamlink, competitie, page=1):
	oc = ObjectContainer()
	
	pagestr=str(page)
	if teamlink != "":
		videourl = baseurl + teamlink + "pagina/"	+ pagestr
	elif competitie != "":
		videourl = baseurl + competitie + "pagina/" + pagestr
		#http://eredivisielive.nl/video/overzicht/competitie/eredivisie/
		
#CLIPS:	
#	<ul class="clearfix">
#		<li class="video-item">
#			<a href="/video/62201-transfer-targets-de-sterren-van-feyenoord.html">
#				<span class="video-play-button">&nbsp;</span>
#				<img src="http://static.eredivisielive.nl/data/images/2012/05/30/160_90/39077.jpg" width="145" height="81" title="Transfer Targets: De sterren van Feyenoord" />
#				<span class="date">30 mei 2012 om 12:30<br />Duur: 1:24. Views: 5.151</span>	
#				<span class="title">Transfer Targets: De sterren van Feyenoord</span>
#			</a>
#		</li>
#		<li class="video-item">
#			<a href="/video/61875-feyenoord-tv-26-05-de-mooiste-momenten-van-het-seizoen.html">
#				<span class="video-play-button">&nbsp;</span>
#				<img src="http://static.eredivisielive.nl/data/images/2012/05/25/160_90/38907.jpg" width="145" height="81" title="Feyenoord TV 26-05: De mooiste momenten van het seizoen" />
#				<span class="date">26 mei 2012 om 17:20<br />Duur: 17:55. Views: 745</span>		
#				<span class="title">Feyenoord TV 26-05: De mooiste momenten van het seizoen</span>
#			</a>
#		</li>
	
# Meerder paginas:
#	<div id="pagination-forward">
#		<a href="/video/overzicht/club/vvv/categorie/analyse/pagina/2/" class="forward active">Volgende</a>
#	</div>	
	
	content = HTML.ElementFromURL(videourl)
	
	for video in content.xpath('//li[@class="video-item"]'):
		vid_url = video.xpath('./a')[0].get('href')
		vid_url = baseurl + vid_url
		vid_title = video.xpath('./a/span[@class="title"]')[0].text
		thumb = video.xpath('./a/img')[0].get('src')
		
		oc.add(VideoClipObject(
		url = vid_url,
		title = vid_title,
		thumb = Callback(GetThumb, url=thumb)
		))

	if len(oc) == 0:
		return MessageContainer(L('NoVideo'))
		
	else:
		if len(content.xpath('//div[@id="pagination-forward"]')) > 0:
			oc.add(DirectoryObject(key=Callback(getVideo, teamlink=teamlink, competitie=competitie, page=page+1), title=L('More'), thumb=R(ICON_MORE)))
	
	return oc
	
####################################################################################################
def GetThumb(url):
	try:
		image = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
		return DataObject(image, 'image/jpeg')
	except:
		return Redirect(R(ICON))
