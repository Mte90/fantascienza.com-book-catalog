#!/usr/bin/python3
import bs4, sys; print([requests.__version__, bs4.__version__, sys.version])
from bs4 import BeautifulSoup
from natsort import natsorted
import os
import json
import re
import time
import aiohttp
import asyncio
import aiofiles
import requests

class Fantascienza_Scraper:
    start_from = 1006 # Il primo libro è a questo id
    path = './books.json'

    async def finally_save(self, mode):
        async with aiofiles.open(self.path, mode) as outfile:
            await outfile.write(json.dumps(self.books, indent=4))
            await outfile.flush()

    async def save(self):
        self.books['author_books'] = dict(natsorted(self.books['author_books'].items()))
        self.books['list'] = dict(natsorted(self.books['list'].items()))
        print('Aggiorno il DB locale')
        await self.finally_save('w')

    async def parse_page(self, article, asyncio_semaphore):
        # Per calcolare la posizione dell'autore
        generi = ['Horror', 'Fantascienza', 'Giallo', 'Saggistica', 'Thriller', 'Noir', 'Fantasy', 'Fantastico', 'Drammatico', 'Azione', 'Avventura', 'Illustrazione', 'Divulgazione scientifica', 'Cinema', 'Fumettistico', 'Romanzo Storico']
        genere_ignorare = ['colonna sonora', 'antologia brani']
        editore_ignorare = ['Panini', 'Planeta De Agostini', 'Sergio Bonelli Editore', 'Silva Screen', 'Sony', 'Walt Disney Italia', 'Lo Stregatto', 'Music', 'RW Edizioni', 'Decca', 'Audioglobe', 'Varèse Sarabande', 'Warner', 'Minus', 'DreamWorks', 'Marvel', 'Emi', 'Cagliostro', 'Varése Sarabande', 'Comics', 'Magic Press', 'MagicPress', 'Walt Disney']
        sezioni_ignorare = ['Durata', 'Brani', 'Sviluppatore', 'Episodio', 'Regia', 'Sceneggiatura']

        URL = f'https://www.fantascienza.com/' + str(article)

        async with asyncio_semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(URL) as data:
                        URL = str(data.url)
                        data = await data.text()
            except Exception as e:
                print(str(e) + ':' + URL)
                return

            if any('<label>' + x + '</label>' in str(data) for x in sezioni_ignorare):
                return

            soup = BeautifulSoup(data, 'html.parser')
            blog_review = soup.select_one('.blog-style .column4')

            if blog_review != None:
                is_soundtrack = soup.select_one('.blog-style .column4 p.genere')
                is_editore_ignore = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(1)')
                is_editore_ignore2 = soup.select_one('.blog-style .column4:nth-of-type(3) p:nth-of-type(2)')
                is_editore_ignore3 = soup.select_one('.blog-style .column4:nth-of-type(2) p:nth-of-type(2)')
                is_broken = soup.select_one('.blog-style .column4 p.origine')
                is_broken2 = soup.select_one('.blog-style .column4 p.origine .label')
                if is_soundtrack != None and any(x in is_soundtrack.text for x in genere_ignorare):
                    return
                if is_editore_ignore != None and any(x in is_editore_ignore.text for x in editore_ignorare) or is_editore_ignore2 != None and any(x in is_editore_ignore2.text for x in editore_ignorare) or is_editore_ignore3 != None and any(x in is_editore_ignore3.text for x in editore_ignorare):
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
                author = author.replace('Vari(e)','AA.VV.')
                author = author.replace('aa.vv.','AA.VV.')
                author = author.replace('Aa.Vv.','AA.VV.')
                author = author.replace('Aa. Vv.','AA.VV.')
                author = author.replace('Autori Vari','AA.VV.')
                author = author.replace('Vari','AA.VV.')
                author = author.replace('R. R.','R.R.')
                author = author.replace(' -',',')
                author = author.replace(' e ',', ')
                author = author.replace(' /',',')
                author = author.replace(';',', ')
                author = author.replace(' &',',')
                author = author.replace('P. K. Dick','Philip K. Dick')
                author = author.replace('Ursula K. Le Guin','Ursula Kroeber Le Guin')
                author = author.replace('Robert A. Heinlein','Robert Anson Heinlein')
                author = author.replace('A.C.Clarke','Arthur Charles Clarke')
                author = author.replace('Arthur C. Clarke','Arthur Charles Clarke')
                author = author.replace('Walter Tevis','Walter S. Tevis')
                author = author.replace('J.T. LeRoy','J.T. Leroy')
                author = author.replace('James G. Ballard','James Graham Ballard')
                author = author.replace('J.K. Rowling','Joanne K. Rowling')
                author = author.replace('Kurt Vonnegut jr.','Kurt Vonnegut jr')
                author = author.replace('Kurt Vonnegut jr','Kurt Vonnegut')
                author = author.replace('Larry Mc Caffery','Larry McCaffery')
                author = author.replace('Orson Scoot Card','Orson Scott Card')
                author = author.replace('Philip Jose Farmer','Philip José Farmer')
                author = author.replace('Robert E. Howard', 'Robert Ervin Howard')
                author = author.replace('Walter J. Williams', 'Walter Jon Williams')
                author = author.replace('Alfred E. Van Vogt', 'Alfred Elton van Vogt')
                author = author.strip()

                print("%d, scheda trovata!" % article)

                self.books['list'][str(article)] = {
                    'title': soup.find('title').text,
                    'author': author,
                    'original_title': original_title.replace('\n','').strip(),
                    'italian_publish_year': italian_publish_year,
                    'isbn': isbn.replace('-',''),
                    'link': URL
                    }

                if author in self.books['author_books']:
                    self.books['author_books'][author].append(article)
                else:
                    self.books['author_books'][author] = [article]

    async def main(self) -> None:
        if not os.path.exists(self.path):
            print('Nuovo DB in corso')
            self.books = {'list':{},'author_books':{}}
        else:
            print('Aggiornamento DB dall\'ultima esecuzione')
            with open(self.path, 'r') as outfile:
                self.books = json.load(outfile)
                outfile.close()
            if 'list' in self.books and len(self.books['list']):
                self.start_from = int(natsorted(self.books['list'].keys())[-1])

        data = requests.get('https://www.fantascienza.com/')
        soup = BeautifulSoup(data.content, 'html.parser')
        last_article = soup.select_one('.home-main-block a')
        last_article_id = int(last_article['href'].split('/')[3]) - self.start_from

        print('Totale articoli da elaborare: ' + str(last_article_id))
        print('Ultimo articolo elaborato: ' + str(self.start_from))

        if int(last_article_id) < int(self.start_from):
            last_article_id = last_article_id + self.start_from

        jobs = []
        asyncio_semaphore = asyncio.BoundedSemaphore(20)
        for article in range(self.start_from + 1, int(last_article_id)):
            jobs.append(asyncio.ensure_future(self.parse_page(article, asyncio_semaphore)))
        await asyncio.gather(*jobs)

        print('Finito, trovati ' + str(len(self.books['list'])))
        # Salva alla fine in caso ne manchi qualcuno
        await self.save()

async def app() -> None:
    scraper = Fantascienza_Scraper()
    await scraper.main()
if __name__ == "__main__":
    asyncio.run(app())
