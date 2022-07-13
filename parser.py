#!/usr/bin/env python
# coding: utf-8

# In[143]:


from bs4 import BeautifulSoup
from ebooklib import epub
import urllib3
from os.path import exists
import re
import time


# In[144]:


url = 'https://younettranslate.com/projects/blagoslovenie-nebozhiteley/vyrvetsya-iz-plena-mednoy-pechi-bozhestvo-stoyashchee-mezh-nebom-i-zemley-chast-pervaya'
target_volume = '5'


# In[146]:


# Get all chapters of one volume
def downloader(url, target_volume):
  response = http.request('GET', url)
  webpage = response.data.decode('utf-8')

  soup = BeautifulSoup(webpage, 'html.parser')
  navheader = str(soup.h3)
  volume = re.findall('v \d+', navheader)[0].split(' ')[1]
  chapter = re.findall('- \d+', navheader)[0].split('- ')[1]
  
  print(chapter,url)
  
  if volume == target_volume:
    with open('v' + target_volume + '_chapters.txt', 'a') as file:
      file.write(chapter + '\n')
    with open('v' + target_volume + '-' + chapter + '.html', 'w', encoding='utf-8') as file:
      file.write(webpage)
      navpanel = soup.find('div', {'class': 'chapters-navpanel'})
      url_next = navpanel.find_all('a')
      if len(url_next) > 1:
        url_next = url_next[-1]['href']
        downloader(url_next, target_volume)
  

if not exists('v' + target_volume + '_chapters.txt'):
  http = urllib3.PoolManager()
  downloader(url, target_volume)


# In[147]:


# Get a body text from webpages and write down it to new files
with open('v' + target_volume + '_chapters.txt', 'r') as file:
  chapters = file.read().splitlines()
  
if not exists('v' + target_volume + '_cleaned'):
  for neo in chapters:
    filename = 'v' + target_volume + '-' + neo + '.html'
    with open(filename, 'r',encoding='utf-8') as file:
      soup = BeautifulSoup(file.read(), 'html.parser')
      with open(filename.replace('.', '_clean.'), 'w', encoding='utf-8') as new_file:
        new_file.write(str(soup.h1).replace('<h1>', '<h1>Глава ' + neo + '. ').replace('h1', 'h3'))
      body = soup.find('main', {'class': 'site-main'})
      body.find('div', id='comments').decompose()
      body.find('div', {'class': 'other-posts-area'}).decompose()
      with open(filename.replace('.', '_clean.'), 'a', encoding='utf-8') as new_file:
        new_file.write( str(body).replace('p style="text-align:justify"', 'p style="text-align:justify;text-indent:1.5em"') )

  with open('v' + target_volume + '_cleaned', 'w') as file:
    file.write('')


# In[148]:


# Create epub book from clean webpages
book = epub.EpubBook()

book.set_identifier('younettranslate')
book.set_title('Благословение небожителей' + '. Том ' + target_volume)
book.set_language('ru')
book.add_author('Мосян Тунсю')
book.set_cover('v'+target_volume+'-cover.jpg', open('v'+target_volume+'-cover.jpg', 'rb').read())

contents, j = [], 0
for neo in chapters:
  filename = 'v' + target_volume + '-' + neo + '.html'
  clean_filename = filename.replace('.', '_clean.')
  with open(filename, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file.read(), 'html.parser')
    chapter_title = 'Глава ' + neo + '. ' + re.sub('</*h1>', '', str(soup.h1))
    contents.append(epub.EpubHtml(title=chapter_title, file_name=clean_filename, lang='ru'))
    with open (clean_filename, 'r', encoding='utf-8') as content_file:
      contents[j].content = content_file.read()
    book.add_item(contents[j])
    j += 1

book.toc = contents

book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

style = 'p {text-indent: 30px;}'
nav_css = epub.EpubItem(uid="p_indent", file_name="style/nav.css", media_type="text/css", content=style)

book.add_item(nav_css)

book.spine = contents

epub.write_epub('Благословение небожителей' + '. Том ' + target_volume+'.epub', book, {})

