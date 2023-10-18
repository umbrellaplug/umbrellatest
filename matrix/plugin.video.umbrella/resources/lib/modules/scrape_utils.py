# -*- coding: utf-8 -*-
"""
	Scrapers Utility Module adapted from FS Umbrella Dev 08/21/23
"""

import re
from resources.lib.modules import cleantitle

RES_4K = ('2160', '216o', '.4k', 'ultrahd', 'ultra.hd', '.uhd.')
RES_1080 = ('1080', '1o8o', '108o', '1o80', '.fhd.')
RES_720 = ('720', '72o')
SCR = ('dvdscr', 'screener', '.scr.', '.r5', '.r6')
CAM = ('1xbet', 'betwin', '.cam.', 'camrip', 'cam.rip', 'dvdcam', 'dvd.cam', 'dvdts', 'hdcam', '.hd.cam', '.hctc', '.hc.tc', '.hdtc',
				'.hd.tc', 'hdts', '.hd.ts', 'hqcam', '.hg.cam', '.tc.', '.tc1', '.tc7', '.ts.', '.ts1', '.ts7', 'tsrip', 'telecine', 'telesync', 'tele.sync')

def info_from_name(release_title, title, year, hdlr=None, episode_title=None, season=None, pack=None):
	try:
		release_title = release_title.lower().replace('&', 'and').replace("'", "")
		release_title = re.sub(r'[^a-z0-9]+', '.', release_title)
		title = title.lower().replace('&', 'and').replace("'", "")
		title = re.sub(r'[^a-z0-9]+', '.', title)
		name_info = release_title.replace(title, '').replace(year, '')
		if hdlr: name_info = name_info.replace(hdlr.lower(), '')
		if episode_title:
			episode_title = episode_title.lower().replace('&', 'and').replace("'", "")
			episode_title = re.sub(r'[^a-z0-9]+', '.', episode_title)
			name_info = name_info.replace(episode_title, '')
		if pack:
			if pack == 'season':
				season_fill = season.zfill(2)
				str1_replace = ('.s%s' % season, '.s%s' % season_fill, '.season.%s' % season, '.season%s' % season, '.season.%s' % season_fill, '.season%s' % season_fill, 'complete')
				for i in str1_replace: name_info = name_info.replace(i, '')
			elif pack == 'show':
				str2_replace = ('.all.seasons', 'seasons', 'season', 'the.complete', 'complete', 'all.torrent', 'total.series', 'tv.series', 'series', 'edited', 's1', 's01')
				for i in str2_replace: name_info = name_info.replace(i, '')
		name_info = name_info.lstrip('.').rstrip('.')
		name_info = '.%s.' % name_info
		return name_info
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return release_title

def get_qual(term):
	if any(i in term for i in SCR): return 'SCR'
	elif any(i in term for i in CAM): return 'CAM'
	elif any(i in term for i in RES_720): return '720p'
	elif any(i in term for i in RES_1080): return '1080p'
	elif any(i in term for i in RES_4K): return '4K'
	elif '.hd.' in term: return '720p'
	else: return 'SD'

def get_release_quality(release_info, release_link=None):
	try:
		quality = None ; info = []
		if release_info: quality = get_qual(release_info)
		if not quality:
			if release_link:
				release_link = release_link.lower()
				quality = get_qual(release_link)
				if not quality: quality = 'SD'
			else: quality = 'SD'
		return quality, info
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return 'SD', []

def convert_size(size_bytes, to='GB'):
	try:
		import math
		if size_bytes == 0: return 0, ''
		power = {'B' : 0, 'KB': 1, 'MB' : 2, 'GB': 3, 'TB' : 4, 'EB' : 5, 'ZB' : 6, 'YB': 7}
		i = power[to]
		p = math.pow(1024, i)
		float_size = round(size_bytes / p, 2)
		# if to == 'B' or to  == 'KB': return 0, ''
		str_size = "%s %s" % (float_size, to)
		return float_size, str_size
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return 0, ''

def check_title(title, aliases, release_title, hdlr, year, years=None): # non pack file title check, single eps and movies
	if years: # for movies only, scraper to pass None for episodes
		if not any(value in release_title for value in years): return False
	else: 
		if not re.search(r'%s' % hdlr, release_title, re.I): return False
	aliases = aliases_to_array(aliases)
	title_list = []
	title_list_append = title_list.append
	if aliases:
		for item in aliases:
			try:
				alias = item.replace('&', 'and').replace(year, '')
				if years: # for movies only, scraper to pass None for episodes
					for i in years: alias = alias.replace(i, '')
				if alias in title_list: continue
				title_list_append(alias)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
	try:
		
		title = title.replace('&', 'and').replace(year, '') # year only in meta title if an addon custom query added it
		if title not in title_list: title_list_append(title)
		release_title = re.sub(r'([(])(?=((19|20)[0-9]{2})).*?([)])', '\\2', release_title) #remove parenthesis only if surrounding a 4 digit date
		t = re.split(r'%s' % hdlr, release_title, 1, re.I)[0].replace(year, '').replace('&', 'and')
		if years:
			for i in years: t = t.split(i)[0]
		t = re.split(r'2160p|216op|4k|1080p|1o8op|108op|1o80p|720p|72op|480p|48op', t, 1, re.I)[0]
		cleantitle_t = cleantitle.get(t)
		if all(cleantitle.get(i) != cleantitle_t for i in title_list): return False

# filter to remove episode ranges that should be picked up in "filter_season_pack()" ex. "s01e01-08"
		if hdlr != year: # equal for movies but not for shows
			range_regex = (
					r's\d{1,3}e\d{1,3}[-.]e\d{1,3}',
					r's\d{1,3}e\d{1,3}[-.]\d{1,3}(?!p|bit|gb)(?!\d{1,3})',
					r's\d{1,3}[-.]e\d{1,3}[-.]e\d{1,3}',
					r'season[.-]?\d{1,3}[.-]?ep[.-]?\d{1,3}[-.]ep[.-]?\d{1,3}',
					r'season[.-]?\d{1,3}[.-]?episode[.-]?\d{1,3}[-.]episode[.-]?\d{1,3}') # may need to add "to", "thru"
			for regex in range_regex:
				if bool(re.search(regex, release_title, re.I)): return False
		return True
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return False

def aliases_to_array(aliases, filter=None):
	try:
		if all(isinstance(x, str) for x in aliases): return aliases
		if not filter: filter = []
		if isinstance(filter, str): filter = [filter]
		return [x.get('title') for x in aliases if not filter or x.get('country') in filter]
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return []

def get_release_quality(release_info, release_link=None):
	try:
		quality = None ; info = []
		if release_info: quality = get_qual(release_info)
		if not quality:
			if release_link:
				release_link = release_link.lower()
				quality = get_qual(release_link)
				if not quality: quality = 'SD'
			else: quality = 'SD'
		return quality, info
	except:
		from cocoscrapers.modules import log_utils
		log_utils.error()
		return 'SD', []

def get_qual(term):
	if any(i in term for i in SCR): return 'SCR'
	elif any(i in term for i in CAM): return 'CAM'
	elif any(i in term for i in RES_720): return '720p'
	elif any(i in term for i in RES_1080): return '1080p'
	elif any(i in term for i in RES_4K): return '4K'
	elif '.hd.' in term: return '720p'
	else: return 'SD'

def info_from_name(release_title, title, year, hdlr=None, episode_title=None, season=None, pack=None):
	try:
		release_title = release_title.lower().replace('&', 'and').replace("'", "")
		release_title = re.sub(r'[^a-z0-9]+', '.', release_title)
		title = title.lower().replace('&', 'and').replace("'", "")
		title = re.sub(r'[^a-z0-9]+', '.', title)
		name_info = release_title.replace(title, '').replace(year, '')
		if hdlr: name_info = name_info.replace(hdlr.lower(), '')
		if episode_title:
			episode_title = episode_title.lower().replace('&', 'and').replace("'", "")
			episode_title = re.sub(r'[^a-z0-9]+', '.', episode_title)
			name_info = name_info.replace(episode_title, '')
		if pack:
			if pack == 'season':
				season_fill = season.zfill(2)
				str1_replace = ('.s%s' % season, '.s%s' % season_fill, '.season.%s' % season, '.season%s' % season, '.season.%s' % season_fill, '.season%s' % season_fill, 'complete')
				for i in str1_replace: name_info = name_info.replace(i, '')
			elif pack == 'show':
				str2_replace = ('.all.seasons', 'seasons', 'season', 'the.complete', 'complete', 'all.torrent', 'total.series', 'tv.series', 'series', 'edited', 's1', 's01')
				for i in str2_replace: name_info = name_info.replace(i, '')
		name_info = name_info.lstrip('.').rstrip('.')
		name_info = '.%s.' % name_info
		return name_info
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return release_title