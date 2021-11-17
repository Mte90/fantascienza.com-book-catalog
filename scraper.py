#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
from natsort import natsorted
import os
import json
import re
import time
import concurrent.futures

MAX_THREADS = 10 # Numero massimo di thread
start_from = 1006 # Il primo libro è a questo id
path = './books.json'

def finally_save(path, books, mode):
    with open(path, mode) as outfile:
        json.dump(books, outfile, indent=4)
        outfile.close()

def save(path, books):
    books['author_books'] = dict(natsorted(books['author_books'].items()))
    books['list'] = dict(natsorted(books['list'].items()))
    print('Aggiorno il DB locale')
    finally_save(path, books, 'w')

def parse_page(article):
    # Per calcolare la posizione dell'autore
    generi = ['Horror', 'Fantascienza', 'Giallo', 'Saggistica', 'Thriller', 'Noir', 'Fantasy', 'Fantastico', 'Drammatico', 'Azione', 'Avventura', 'Illustrazione', 'Divulgazione scientifica', 'Cinema']
    genere_ignorare = ['colonna sonora', 'antologia brani']
    editore_ignorare = ['Panini Comics', 'Planeta De Agostini', 'Sergio Bonelli Editore', 'Silva Screen', 'Sony', 'Walt Disney Italia', 'Lo Stregatto', 'Music', 'RW Edizioni', 'Decca', 'Audioglobe']
    sezioni_ignorare = ['Durata', 'Brani', 'Sviluppatore', 'Episodio', 'Regia']

    URL = f'https://www.fantascienza.com/' + str(article)

    try:
        data = requests.get(URL)
    except Exception as e:
        print(e + ':' + URL)
        return

    if any('<label>' + x + '</label>' in str(data.content) for x in sezioni_ignorare):
        return

    soup = BeautifulSoup(data.content, 'html.parser')
    blog_review = soup.select_one('.blog-style .column4')

    if blog_review != None:
        is_soundtrack = soup.select_one('.blog-style .column4 p.genere')
        is_editore_ignore = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(1)')
        is_editore_ignore2 = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(2)')
        is_broken = soup.select_one('.blog-style .column4 p.origine')
        is_broken2 = soup.select_one('.blog-style .column4 p.origine .label')
        if is_soundtrack != None and any(x in is_soundtrack.text for x in genere_ignorare):
            return
        if is_editore_ignore != None and any(x in is_editore_ignore.text for x in editore_ignorare) or is_editore_ignore2 != None and any(x in is_editore_ignore2.text for x in editore_ignorare):
            return
        if is_broken2 != None and is_broken2.text == 'colore':
            return
        if is_broken != None and (is_broken.text == ', ' or is_broken.text == ''):
            return

        isbn = ''
        italian_publish_year = ''
        original_title = ''

        # Sanitizzazione dei dati perchè le vecchie schede non sono standard
        if soup.select_one('.blog-style .column4:nth-of-type(1) img') != None:
            author_temp = soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(2)')
            if author_temp == None or any(x in author_temp.text for x in generi):
                author = soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(1)').text
            else:
                author = soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(2)').text

            if soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(4)') != None:
                isbn = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(4)').text

            if ',' in soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(1)').text:
                original_title = str(soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(1)').text).split(',')[0]

            if original_title == '' and soup.select_one('.blog-style .column4:nth-of-type(2) p span.titolo_originale') != None:
                original_title = soup.select_one('.blog-style .column4:nth-of-type(2) p span.titolo_originale').text

            if soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(7)') != None:
                italian_publish_year = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(4)').text
                isbn = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(5)').text

            if soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(6)') != None:
                italian_publish_year = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(3)').text
                isbn = ''

            if len(italian_publish_year) > 4 or italian_publish_year == '':
                italian_publish_year = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(2)').text
                isbn = ''

            if author == 'Romanzo Storico':
                author = soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(2)').text

        else:
            author_temp = soup.select_one('.blog-style .column4:nth-of-type(1) p:nth-of-type(2)')
            if author_temp == None or any(x in author_temp.text for x in generi):
                author = soup.select_one('.blog-style .column4:nth-of-type(1) p:nth-of-type(1)').text
            else:
                author = soup.select_one('.blog-style .column4:nth-of-type(1) p:nth-of-type(2)').text

            if soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(3)') != None:
                italian_publish_year =soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(3)').text

            if ',' in soup.select_one('.blog-style .column4:nth-of-type(1) p:nth-of-type(1)').text:
                original_title = str(soup.select_one('.blog-style .column4:nth-of-type(1) p:nth-of-type(1)').text).split(',')[0]

            if soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(5)') == None:
                italian_publish_year = soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(2)').text

            if author == 'Fantascienza' or author == 'Fantastico' or author == 'Horror':
                author = soup.select_one('.blog-style .column4:nth-of-type(1) p:nth-of-type(1)').text

        # In alcuni casi resetto quando la pulizia/dato corretto non funziona
        if isbn == '1':
            isbn = ''

        if ',' in italian_publish_year and soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(2)') != None:
            italian_publish_year = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(2)').text

        if not italian_publish_year.isdigit() or italian_publish_year == '1':
            italian_publish_year = ''

        if '(' in original_title:
            original_title = ''

        if author == '' or "\t\t" in author or 'Artisti AA.VV.' in author or 'Artisti Vari' in author:
            return

        # Normalizziamo i dati
        author = author.replace('AA. VV.','AA.VV.')
        author = author.replace('aa.vv.','AA.VV.')
        author = author.replace('Autori Vari','AA.VV.')
        author = author.replace('Vari','AA.VV.')
        author = author.replace('R. R.','R.R.')
        author = author.replace(' -',',')
        author = author.replace(' /',',')
        author = author.replace(' &',',')

        print("%d, scheda trovata!" % article)

        books['list'][str(article)] = {
            'title': soup.find('title').text,
            'author': author,
            'original_title': original_title.replace('\n','').strip(),
            'italian_publish_year': italian_publish_year,
            'isbn': isbn.replace('-',''),
            'link': data.url
            }

        if author in books['author_books']:
            books['author_books'][author].append(article)
        else:
            books['author_books'][author] = [article]

if not os.path.exists(path):
    print('Nuovo DB in corso')
    books = {'list':{},'author_books':{}}
    finally_save(path, books, 'w')
else:
    print('Aggiornamento DB dall\'ultima esecuzione')
    with open(path, 'r') as outfile:
        books = json.load(outfile)
        outfile.close()
    if 'list' in books and len(books['list']):
        start_from = int(natsorted(books['list'].keys())[-1])

data = requests.get('https://www.fantascienza.com/')
soup = BeautifulSoup(data.content, 'html.parser')
last_article = soup.select_one('.home-main-block a')
last_article_id = int(last_article['href'].split('/')[3]) - start_from

print('Totale articoli da elaborare: ' + str(last_article_id))
print('Ultimo articolo elaborato: ' + str(start_from))

if int(last_article_id) < int(start_from):
    last_article_id = last_article_id + start_from

saved = False
for article in range(start_from + 1, int(last_article_id)):
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.submit(parse_page, article)
    # Ogni 10 articoli elaborati salva per sicurezza
    if '.0' in str(len(books['list'])/10):
        if saved == False:
            save(path, books)
            saved = True
    else:
        saved = False

# Salva alla fine in caso ne manchi qualcuno
save(path, books)
print('Finito, trovati ' + str(len(books['list'])))
