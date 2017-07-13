import requests
from bs4 import BeautifulSoup
import pprint
import re
import pandas as pd
import csv

def name_to_url(name):
    name = name.lower().split(' ')

    base = 'http://www.basketball-reference.com/players/'
    addon = name[1][0] + '/' + name[1][0:5] + name[0][0:2] + '01.html'

    return base + addon


def populate_stats(url):
    r = requests.get(url)
    r_html = r.text
    soup = BeautifulSoup(r_html, 'html.parser')

    stats = soup.body.find('div', attrs={'class': 'stats_pullout'})
    try:
        stat2 = stats.findAll('div')
        stats_out = stat2[3:7] + stat2[8:12] + stat2[13:15]
        stats_row = []
        for i in range(0, len(stats_columns)):
            start = str(stats_out[i]).find('<p>') + 3
            end = str(stats_out[i]).find('</p>')
            res = str(stats_out[i])[start:end]

            start2 = str(stats_out[i]).find(str(res)) + len(str(res)) + 8
            end2 = str(stats_out[i]).find('</p></div>')
            res2 = str(stats_out[i])[start2:end2]
            stats_row.append(res2)

        return stats_row

    except AttributeError:
        print 'Missing Data'


def parse_players_csv(filename):
    playerlist = []
    with open(filename, 'rb') as csvfile:
        players = csv.reader(csvfile, delimiter=',')
        for p in players:
            playerlist.append(p)

    players = playerlist[0]
    players = players[1:]
    # print players[0]

    urls = []

    for player in players:
        # print player
        urls.append(name_to_url(player))

    # print urls[0:5]
    return playerlist


def clean_stats_table(stats_table):
    stats_table.insert(0, 'Player', all_active_players[1:10])
    try:
        for col in stats_columns:
            stats_table = stats_table[stats_table[col].map(len) < 6]
            stats_table.reset_index(drop=True, inplace=True)

    except TypeError:
        print 'NoneType'

    return stats_table

if __name__ == '__main__':
    stats_columns = [
                     'Games',
                     'Points',
                     'Total Rebounds',
                     'Assists',
                     'Field Goal Percentage',
                     '3-Point Field Goal Percentage',
                     'Free Throw Percentage',
                     'Effective Field Goal Percentage',
                     'Efficiency Rating',
                     'Win Shares']

    all_active_players = parse_players_csv('playernames.csv')[0]
    stats_table = pd.DataFrame(columns=stats_columns, index=range(1))

    i = 0
    for player in all_active_players[1:10]:
        print player
        url = name_to_url(player)
        row = populate_stats(url)
        # print row
        stats_table.ix[i, stats_columns] = row
        i += 1

    stats_table = clean_stats_table(stats_table)
    stats_table.to_csv('output_stats.csv', sep=',')
    print stats_table
