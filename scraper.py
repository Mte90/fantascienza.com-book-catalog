#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import os
import json
import re

start_from = 1006 # Il primo libro è a questo id
path = '/tmp/books.json'

if not os.path.exists(path):
    print('Nuovo DB')
    books = {'list':{},'author_books':{}}
else:
    print('Aggiornamento DB')
    with open(path, 'r') as outfile:
        books = json.load(outfile)
        outfile.close()
    start_from = int(sorted(books['list'].keys())[-1])

data = requests.get('https://www.fantascienza.com/')
soup = BeautifulSoup(data.content, 'html.parser')
last_article = soup.select_one('.home-main-block a')
last_article_id = int(last_article['href'].split('/')[3]) - start_from

print('Totale articoli da elaborare: ' + str(last_article_id))
print('Ultimo articolo elaborato: ' + str(start_from))

for article in range(start_from + 1, int(last_article_id)):
    URL = f'https://www.fantascienza.com/' + str(article)
    data = requests.get(URL)
    soup = BeautifulSoup(data.content, 'html.parser')
    blog_review = soup.select_one('.blog-style .column4')

    if blog_review != None:
        is_movie = soup.select_one('.blog-style .column4.scheda label:nth-of-type(1)').text
        if is_movie == 'Regia':
            continue
        print("%d articolo trovato!" % article)

        if soup.select_one('.blog-style .column4:nth-of-type(1) img') != None:
            if soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(2)') == None:
                author = soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(1)').text
            else:
                author = soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(2)').text

            ita_year = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(3)').text
            isbn = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(4)').text
            original_title = str(soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(1)').text).split(',')[0]

            if soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(7)') != None:
                ita_year = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(4)').text
                isbn = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(5)').text

            if soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(6)') != None:
                ita_year = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(3)').text
                isbn = ''
        else:
            if soup.select_one('.blog-style .column4:nth-of-type(1) p:nth-of-type(2)') == None:
                author = soup.select_one('.blog-style .column4:nth-of-type(1) p:nth-of-type(1)').text
            else:
                author = soup.select_one('.blog-style .column4:nth-of-type(1) p:nth-of-type(2)').text

            ita_year = ''
            if soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(3)') != None:
                ita_year =soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(3)').text

            isbn = ''
            original_title = str(soup.select_one('.blog-style .column4:nth-of-type(1) p:nth-of-type(1)').text).split(',')[0]

            if soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(5)') == None:
                ita_year = soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(2)').text

            if author == 'Fantascienza' or author == 'Fantastico' or author == 'Horror':
                author = soup.select_one('.blog-style .column4:nth-of-type(1) p:nth-of-type(1)').text

        if isbn == '1':
            isbn = ''

        if not ita_year.isdigit() or italian_publish_year == '1':
            ita_year = ''

        books['list'][article] = {
            'title': soup.find('title').text,
            'author': author,
            'original_title': original_title.replace('\n',''),
            'italian_publish_year': ita_year,
            'isbn': isbn.replace('-',''),
            'link': data.url
            }

        if author in books['author_books']:
            books['author_books'][author].append(article)
        else:
            books['author_books'][author] = [article]

        with open(path, 'w') as outfile:
            json.dump(books, outfile, indent=4)
            outfile.close()

print('Finito, trovati ' + str(len(books['list'])))
