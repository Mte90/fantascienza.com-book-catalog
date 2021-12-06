#!/usr/bin/env python3

import os
import sys
import json
from datetime import date

path = './books.json'

if not os.path.exists(path):
    print('DB mancante, lanciare scraper.py')
    sys.exit()
else:
    with open(path, 'r') as outfile:
        books = json.load(outfile)
        outfile.close()

with open('./skeleton.html', 'r') as reader:
     html = reader.read()

html = html.replace('{data}', str(date.today()))

content_skeleton = '<div class="strict-block"><div class="block-title"><h2>{autore}</h2></div><br><ul>{list}</ul></div>' + "\n"
content = ''

for author in books['author_books']:
    content = content + content_skeleton.replace('{autore}', author)
    books_list = ''
    for book in books['author_books'][author]:
        year = ''
        if books['list'][str(book)]['italian_publish_year'] != '':
            year = ', ' + books['list'][str(book)]['italian_publish_year']
        isbn = ''
        if books['list'][str(book)]['isbn'] != '':
            isbn = ', ' + books['list'][str(book)]['isbn']
        original_title = ''
        if books['list'][str(book)]['original_title'] != '':
            original_title = ', <i>' + books['list'][str(book)]['original_title'] + '</i>'
        books_list += '<li><a href="' + books['list'][str(book)]['link'] + '" target="_blank"><b>' + books['list'][str(book)]['title'] + '</b></a>' + year + isbn + original_title + '</li>'
    content = content.replace('{list}', books_list)

html = html.replace('{content}', content)
html = html.replace('{totale}', str(len(books['list'])))

save = open('./index.html', 'w')
save.write(html)
save.close()
print('Fatto')
