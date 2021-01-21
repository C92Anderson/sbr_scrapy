# -*- coding: utf-8 -*-
# To run: scrapy runspider sbr_scrapy.py -o your_filename.csv

import datetime
import json
import re
import time

import scrapy
from pytz import timezone

class SbrBettingOddsSpider(scrapy.Spider):
    name = 'sbr_betting_odds'
    allowed_domains = ['sportsbookreview.com']
    sports_book_ids = {
        '138.com': '78',
        '5dimes': '3',
        'bet365': '5',
        'betcris': '10',
        'betmania': '83',
        'betonline': '8',
        'betphoenix': '28',
        'bodog': '9',
        'bookmaker': '10',
        'bovada': '9',
        'cloudbet': '93',
        'gtbets': '65',
        'heritage': '44',
        'intertops': '29',
        'jazzsports': '15',
        'justbet': '16',
        'matchbook': '18',
        'mybookie': '82',
        'nitrogen': '92',
        'pinnacle': '20',
        'sbr': '45',
        'skybook': '84',
        'sportbet': '3',
        'sportsbetting': '8',
        'sportsinteraction': '35',
        'the greek sportsbook': '22',
        'wagerweb': '54',
        'william_hill': '36',
        'youwager': '38'
    }
    league_market = {
        'nhl-hockey': {
            'totals': {
                'mtid': "412",
                'lid': "7",
                'spid': "6"
            },
            'money-lines': {
                'mtid': "125",
                'lid': "7",
                'spid': "6"
            },
            'pointspread': {
                'mtid': "411",
                'lid': "7",
                'spid': "6"
            },
        },
        'college-football': {
            'totals': {
                'mtid': "402",
                'lid': "6",
                'spid': "4"
            },
            'money-lines': {
                'mtid': "83",
                'lid': "6",
                'spid': "4"
            },
            'pointspread': {
                'mtid': "401",
                'lid': "6",
                'spid': "4"
            },
        },
        'ncaa-basketball': {
            'totals': {
                'mtid': "402",
                'lid': "14",
                'spid': "5"
            },
            'money-lines': {
                'mtid': "83",
                'lid': "14",
                'spid': "5"
            },
            'pointspread': {
                'mtid': "401",
                'lid': "14",
                'spid': "5"
            },
        },
        'mlb-baseball': {
            'totals': {
                'mtid': "402",
                'lid': "3",
                'spid': "3"
            },
            'money-lines': {
                'mtid': "83",
                'lid': "3",
                'spid': "3"
            },
            'pointspread': {
                'mtid': "401",
                'lid': "3",
                'spid': "3"
            },
        },
        'nba-basketball': {
            'totals': {
                'mtid': "402",
                'lid': "5",
                'spid': "5"
            },
            'money-lines': {
                'mtid': "83",
                'lid': "5",
                'spid': "5"
            },
            'pointspread': {
                'mtid': "401",
                'lid': "5",
                'spid': "5"
            },
        },
        'wnba-basketball': {
            'totals': {
                'mtid': "402",
                'lid': "15",
                'spid': "5"
            },
            'money-lines': {
                'mtid': "83",
                'lid': "15",
                'spid': "5"
            },
            'pointspread': {
                'mtid': "401",
                'lid': "15",
                'spid': "5"
            },
        },
        'nfl-football': {
            'totals': {
                'mtid': "402",
                'lid': "16",
                'spid': "4"
            },
            'money-lines': {
                'mtid': "83",
                'lid': "16",
                'spid': "4"
            },
            'pointspread': {
                'mtid': "401",
                'lid': "16",
                'spid': "4"
            },
        },
        'cfl-football': {
            'totals': {
                'mtid': "402",
                'lid': "19",
                'spid': "4"
            },
            'money-lines': {
                'mtid': "83",
                'lid': "19",
                'spid': "4"
            },
            'pointspread': {
                'mtid': "401",
                'lid': "19",
                'spid': "4"
            }
        }
    }
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 1
    }

    tz = timezone('US/Eastern')

    def start_requests(self):
        def prompt(key, default):
            print(key)
            inp = input()
            return inp if inp != '' else default

        def get_dates_in_range():
            m = re.search(r'(\d{1,2})\D(\d{1,2})\D(\d{4})', start_date)
            start = datetime.date(int(m[3]), int(m[1]), int(m[2]))
            m = re.search(r'(\d{1,2})\D(\d{1,2})\D(\d{4})', end_date)
            end = datetime.date(int(m[3]), int(m[1]), int(m[2]))
            return [str(int(time.mktime((start + datetime.timedelta(n)).timetuple()))) + "000"
                    for n in range(int((end - start).days) + 1)]

        sport = prompt('Select League: [mlb-baseball (default), college-football, cfl-football, nba-basketball, ncaa-basketball, nfl-football, nhl-hockey, wnba-basketball]', 'mlb-baseball')
        start_date = prompt('Start Date: ['+datetime.datetime.now().strftime('%m-%d-%Y')+' (default)]', datetime.datetime.now().strftime('%m-%d-%Y'))
        end_date = prompt('End Date: ['+datetime.datetime.now().strftime('%m-%d-%Y')+' (default)]', datetime.datetime.now().strftime('%m-%d-%Y'))
        sports_book = prompt('Sports Book: [pinnacle (default), 5dimes, bet365, betcris, betonline, bookmaker, heritage, nitrogen, william_hill]', 'pinnacle')
        bet_type = prompt('Bet Type: [money-lines (default), pointspread, totals]', 'money-lines')
        team_name_format = prompt('Team Format: [abbreviation (default), full]', 'abbreviation')

        # sport = 'college-football'
        # start_date = '01-05-2019'
        # end_date = '01-05-2019'
        # sports_book = 'pinnacle'
        # team_name_format = 'abbreviation'
        # bet_type = 'money-lines'

        query_data = self.league_market.get(sport, {}).get(bet_type, {})
        if not query_data:
            return
        mtid = query_data.get('mtid')
        lid = query_data.get('lid')
        spid = query_data.get('spid')
        sbid = self.sports_book_ids.get(sports_book)

        dates = get_dates_in_range()
        for date in dates:
            url = "https://www.sportsbookreview.com/ms-odds-v2/odds-v2-service?query=" \
                  f"%7B+eventsByDateByLeagueGroup%28leagueGroups:+%5B%7Bmtid:+{mtid}%2C+lid:+{lid}%2C+spid:+{spid}" \
                  "%7D%5D%2C+providerAcountOpener:+3%2C+hoursRange:+25%2C+showEmptyEvents:+true%2C+marketTypeLayout:+" \
                  f"%22PARTICIPANTS%22%2C+ic:+false%2C+startDate:+{date}%2C+timezoneOffset:+-5%2C+nof:+" \
                  "true%2C+hl:+true%29+%7B+events+%7B+dt+participants+%7B+ih+rot+partid+startingPitcher+%7B+fn+lnam+" \
                  "%7D+source+%7B+...+on+Team+%7B+nam+abbr+%7D+%7D+eid+psid+tr+sppil+%7D+statistics%28sgid:+3%2C+" \
                  f"sgidWhenFinished:+4%29+%7B+nam+partid+typ+val+%7D+currentLines%28paid:+%5B{sbid}%5D%29+%7D+%7D+%7D"
            yield scrapy.Request(url, meta={'sports_book': sports_book, 'bet_type': bet_type,
                                            'sbid': sbid,
                                            'sport': sport,
                                            'team_name_format': team_name_format})

    def parse(self, response):
        sports_book = response.meta.get('sports_book')
        bet_type = response.meta.get('bet_type')
        # sbid = response.meta.get('sports_book_id')
        sport = response.meta.get('sport')
        team_name_format = response.meta.get('team_name_format')

        def get_score(index):
            lines = list(
                filter(
                    lambda l: l['nam'] == 'runs' and l['partid'] == event['participants'][index]['partid'] and l[
                        'typ'] == 'eventside',
                    event['statistics']))

            if len(lines) > 0:
                return lines[0]['val'] or 0

        data = json.loads(response.text)
        for event in data.get('data', {}).get('eventsByDateByLeagueGroup', {}).get('events', []):
            home_index = 0 if event['participants'][0]['ih'] else 1
            away_index = 1 - home_index
            item = dict()
            item['game_date'] = datetime.datetime.fromtimestamp(event['dt'] / 1000, self.tz).strftime('%m-%d-%Y')
            item['game_time'] = datetime.datetime.fromtimestamp(event['dt'] / 1000, self.tz).strftime('%H:%M:%S')
            item['home_rot'] = str(event['participants'][home_index]['rot']).zfill(2)
            item['away_rot'] = str(event['participants'][away_index]['rot']).zfill(2)

            mlb_abbr = dict()
            mlb_abbr['CWS'] = 'CHW'
            mlb_abbr['KC'] = 'KCR'
            mlb_abbr['LAA'] = 'ANA'
            mlb_abbr['TB'] = 'TBD'
            mlb_abbr['MIA'] = 'FLA'
            mlb_abbr['SF'] = 'SFG'
            mlb_abbr['SD'] = 'SDP'
            mlb_abbr['WSH'] = 'WSN'

            nba_abbr = dict()
            nba_abbr['CHA'] = 'CHO'
            nba_abbr['BKN'] = 'BRK'
            nba_abbr['PHX'] = 'PHO'

            nfl_abbr = dict()
            nfl_abbr['WAS'] = 'WSH'
            nfl_abbr['JAC'] = 'JAX'
            nfl_abbr['LA'] = 'LAR'

            if team_name_format == 'abbreviation':
                item['home_team_abbr'] = event['participants'][home_index]['source']['abbr']
                item['away_team_abbr'] = event['participants'][away_index]['source']['abbr']
                if sport == 'mlb-baseball':
                    if item['home_team_abbr'] in mlb_abbr:
                        item['home_team_abbr'] = mlb_abbr[item['home_team_abbr']]
                    if item['away_team_abbr'] in mlb_abbr:
                        item['away_team_abbr'] = mlb_abbr[item['away_team_abbr']]
                if sport == 'nba-basketball':
                    if item['home_team_abbr'] in nba_abbr:
                        item['home_team_abbr'] = nba_abbr[item['home_team_abbr']]
                    if item['away_team_abbr'] in nba_abbr:
                        item['away_team_abbr'] = nba_abbr[item['away_team_abbr']]
                if sport == 'nfl-football':
                    if item['home_team_abbr'] in nfl_abbr:
                        item['home_team_abbr'] = nfl_abbr[item['home_team_abbr']]
                    if item['away_team_abbr'] in nfl_abbr:
                        item['away_team_abbr'] = nfl_abbr[item['away_team_abbr']]

            else:
                item['home_team_full'] = event['participants'][home_index]['source']['nam']
                item['away_team_full'] = event['participants'][away_index]['source']['nam']

            if sport == 'mlb-baseball':
                item['home_sp'] = None
                item['away_sp'] = None
                if 'startingPitcher' in event['participants'][away_index]:
                    starting_pitcher = event['participants'][away_index].get('startingPitcher')
                    if starting_pitcher:
                        item['away_sp'] = starting_pitcher.get('fn') + ' ' + starting_pitcher.get('lnam')
                        item['away_sp'] = item['away_sp'].replace('í', 'i').replace('á', 'a').replace('ó', 'o').replace('é', 'e').replace('ñ', 'n')
                if 'startingPitcher' in event['participants'][home_index]:
                    starting_pitcher = event['participants'][home_index].get('startingPitcher')
                    if starting_pitcher:
                        item['home_sp'] = starting_pitcher.get('fn') + ' ' + starting_pitcher.get('lnam')
                        item['home_sp'] = item['home_sp'].replace('í', 'i').replace('á', 'a').replace('ó', 'o').replace('é', 'e').replace('ñ', 'n')

            item['home_score'] = get_score(home_index) or 0
            item['away_score'] = get_score(away_index) or 0
            item['sportsbook'] = sports_book
            item['bet_type'] = bet_type

            line = event['currentLines'][0]

            url = 'https://www.sportsbookreview.com/ms-odds-v2/odds-v2-service?query=%7B+historyLines' \
                  f'(eid:{line["eid"]},+mtid:+{line["mtid"]},+paid:+{line["paid"]},' \
                  f'+partid:+[{event["participants"][away_index]["partid"]}' \
                  f',+{event["participants"][home_index]["partid"]},+15143,+15144])+%7B+' \
                  f'line{event["participants"][away_index]["partid"]}:+historyLine' \
                  f'(groupId:+{event["participants"][away_index]["partid"]})' \
                  f'line{event["participants"][home_index]["partid"]}:+historyLine' \
                  f'(groupId:+{event["participants"][home_index]["partid"]})line15143:+historyLine(groupId:+15143)' \
                  'line15144:+historyLine(groupId:+15144)+%7D+%7D'
            if bet_type == 'totals':
                away_part_id = event['currentLines'][0]['partid']
                home_part_id = event['currentLines'][1]['partid']
            else:
                away_part_id = event["participants"][away_index]['partid']
                home_part_id = event["participants"][home_index]['partid']
            yield scrapy.Request(url, self.parse_history,
                                 meta={'away_part_id': away_part_id,
                                       'home_part_id': home_part_id,
                                       'teams': event["participants"], 'item': item, 'bet_type': bet_type,
                                       'home_index': home_index,
                                       'away_index': away_index})

    def parse_history(self, response):
        item = response.meta.get('item')
        bet_type = response.meta.get('bet_type')
        away_part_id = response.meta.get('away_part_id')
        home_part_id = response.meta.get('home_part_id')

        data = json.loads(response.text)
        for line in data['data']['historyLines']['line' + str(away_part_id)]:
            lines = list(filter(lambda line2: line['tim'] == line2['tim'],
                                data['data']['historyLines']['line' + str(home_part_id)]))
            if len(lines) > 0:
                next_line = lines[0]
                lines = [line, next_line]
                more = self.get_more(bet_type, lines)
                merged = {**item, **more}
                yield merged

    def get_point_spread(self, lines):
        item = dict()
        item['line_move_date'] = datetime.datetime.fromtimestamp(lines[0]['tim'] / 1000, self.tz).strftime('%m-%d-%Y')
        item['line_move_time'] = datetime.datetime.fromtimestamp(lines[0]['tim'] / 1000, self.tz).strftime('%H:%M:%S')
        item['home_line'] = lines[1]['adj']
        item['away_line'] = lines[0]['adj']
        item['home_odds'] = lines[1]['ap']
        item['away_odds'] = lines[0]['ap']
        return item

    def get_more(self, bet_type, lines):
        if bet_type == 'pointspread':
            return self.get_point_spread(lines)
        item = dict()
        item['line_move_date'] = datetime.datetime.fromtimestamp(lines[0]['tim'] / 1000, self.tz).strftime('%m-%d-%Y')
        item['line_move_time'] = datetime.datetime.fromtimestamp(lines[0]['tim'] / 1000, self.tz).strftime('%H:%M:%S')
        if bet_type != 'money-lines':
            if 'adj' in lines[0]:
                item['total'] = abs(lines[0]['adj'])
        item['home_odds'] = lines[1]['ap']
        item['away_odds'] = lines[0]['ap']
        return item
