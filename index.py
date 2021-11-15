#!/usr/bin/python3

import os
import json
from datetime import date

path = '/tmp/books.json'

if not os.path.exists(path):
    print('DB mancante, lanciare scraper.py')
    os.exit()
else:
    with open(path, 'r') as outfile:
        books = json.load(outfile)
        outfile.close()

with open('./index.html', 'r') as reader:
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
            original_title = ', ' + books['list'][str(book)]['original_title']
        books_list += '<li><a href="' + books['list'][str(book)]['link'] + '" target="_blank">' + books['list'][str(book)]['title'] + year + isbn + original_title + '</a></li>'
    content = content.replace('{list}', books_list)

html = html.replace('{content}', content)
html = html.replace('{totale}', str(len(books['list'])))

save = open('/tmp/index.html', 'w')
save.write(html)
save.close()
