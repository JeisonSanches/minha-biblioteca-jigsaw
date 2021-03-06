from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import urllib
import requests
import re
import sys
from shutil import copyfileobj, rmtree
from os import mkdir, listdir, makedirs, path
from urllib.parse import urljoin
from datetime import datetime
from fpdf import FPDF
import json
import io

"""
Primeiro cookie tem que ser obtido manualmente. Abra MinhaBiblioteca pelo SIGA normalmente.
No browser abra o developers console e faça um request para https://jigsaw.vitalsource.com/books/9788582601044
Olhe o último request que termina com um número (".../encrypted/1600" por exemplo). Nos response headers,
vai ter um parâmetro Set-Cookie. Copie e cole o valor no arquivo cookie.txt
"""
starting_cookie = None


def main(_id=None):
    """
    Ache essa URL entrando num livro qualquer e achando o request que termina com
    pages. Copie o link address.
    Bonus: o valor :id é o ISBN do livro na URL
    https://jigsaw.vitalsource.com/api/v0/books/:id/pages
    """
    #Pasting ISBN here is easier for me, deal with it.
    _id = _id or "9788537803868"
    metadata =  get_metadata(_id)
    title = metadata['title'] if metadata else None
    print("Book title is: " + title if title else "I couldn't download the metadata")
    url = "https://jigsaw.vitalsource.com/api/v0/books/{}/pages".format(_id)
    filename = write_api_response(url)
    download_from_api_response(filename, title)
    #download_from_api_response('out2.json')

"""
Most of these are probably unnecessary, but I'm too lazy to find out which.
"""
page_headers = {
    'User-Agent': UserAgent().chrome,
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch, br',
    'Accept-Language':'en-US,en;q=0.8',
    'Host':'jigsaw.vitalsource.com'
}

image_headers = {
    'User-Agent': UserAgent().chrome,
    'Accept':'image/webp,image/*,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch, br',
    'Accept-Language':'en-US,en;q=0.8',
    'Host':'jigsaw.vitalsource.com'
}

api_headers = {
    'User-Agent': UserAgent().chrome,
    'Accept':'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding':'gzip, deflate, sdch, br',
    'Accept-Language':'en-US,en;q=0.8',
    'Host':'jigsaw.vitalsource.com',
    'Referer':'https://jigsaw.vitalsource.com/books/9788582601044/pages/recent?jigsaw_brand=integradaminhabiblioteca&xdm_e=https%3A%2F%2Fintegrada.minhabiblioteca.com.br&xdm_c=default4014&xdm_p=1',
    'X-Requested-With':'XMLHttpRequest'
}

def get_metadata(_id):
    """
    There's a bunch of book data available here. Title, author, ISBN, etc etc etc
    """
    url = "https://jigsaw.vitalsource.com/books/{}".format(_id)
    response = requests.get(url, headers=page_headers)
    soup = BeautifulSoup(response.content,'html.parser')
    for script in soup.find_all('script'):
        #This shouldn't be allowed to work. I fucking love it.
        match = re.search("VST.currentBookData.*(\{.*\});",script.get_text())
        if match:
            return json.loads(match.group(1))
    return None

def download_from_api_response(source, book_title):
    baseurl = "https://jigsaw.vitalsource.com"
    with open(source) as f:
        pages = json.loads(f.read())
    pdf = FPDF(orientation='P',format='A4')
    pdf.set_auto_page_break(False)
    epub = '<head><meta charset="UTF-8"></head>'

    """
    If you download the same book twice I will remove the old files. Back it up.
    Or don't I'm not your boss.
    """
    dirname = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    mkdir(dirname)

    session = requests.Session()
    is_epub = False
    for index, page in enumerate(pages):
        url = baseurl + page['absoluteURL']
        if url.endswith('html'):
            """
            Book pages are HTML (EPUB)
            """
            is_epub = True
            response = session.get(url, headers=page_headers)
            soup = BeautifulSoup(response.content,'html.parser').find('body')
            """
            Essa parte acha as imagens na página faz download, colocando no mesmo
            path relativo à imagem original. Então as imagens do ebook funcionam localmente
            sem alterar os atributos da página original.
            Alguma coisa similar deve ser feita para HTML anchors, mas existem complicadores.
            """
            for img in soup.find_all('img'):
                real_src = urljoin(url, img['src'])
                common = path.commonprefix([url, real_src])
                target = path.join(dirname, real_src[len(common):])
                if not path.isfile(target):
                    if not path.exists(path.dirname(target)):
                        makedirs(path.dirname(target))
                    image_response = session.get(real_src, stream=True)
                    with io.open(target, "wb") as out:
                        copyfileobj(image_response.raw, out)
            epub += str(soup)
        else:
            """
            Book pages are images
            """
            response = session.get(url, headers=page_headers)

            soup = BeautifulSoup(response.content,'html.parser')
            pageurl = soup.find('img',id='pbk-page')['src']

            image_headers['Cookie'] = response.headers['Set-Cookie']
            page_headers['Cookie'] = response.headers['Set-Cookie']

            image_headers['Referer'] = url
            image_response = session.get(baseurl + pageurl,headers=image_headers, stream=True)

            image_headers['Cookie'] = image_response.headers['Set-Cookie']
            page_headers['Cookie'] = image_response.headers['Set-Cookie']

            filename = str(index).zfill(3) + "." + path.split(image_response.headers['content-type'].split(';')[0])[1]
            with io.open(path.join(dirname,filename), 'wb', encoding="utf-8") as out:
                copyfileobj(image_response.raw, out)

            pdf.add_page()
            pdf.image(path.join(dirname,filename),x=0,w=210,h=297)
        print("{}/{}".format(index+1,len(pages)))

    if is_epub:
        epub_name = "{}/Text/{}.html".format(dirname,book_title)
        makedirs(path.dirname(epub_name))
        with io.open(epub_name,'w+', encoding="utf-8") as f:
            f.write(epub)
        print("EPUB file: {}".format(epub_name))
    else:
        print("Done downloading images. Creating PDF. This may take a while...")
        print("PDF name will be the same as dir where data is kept until I figure out how to extract book title from...somewhere")
        pdf_name = "{}.pdf".format(book_title)
        print("PDF title: {}".format(pdf_name))
        pdf.output(pdf_name, "F")
    print("Done. Yes, I am that cool.")

def write_api_response(url):
    response = requests.get(url, headers=api_headers)
    filename = "out.json"
    with io.open(filename,'w+', encoding="utf-8") as f:
        f.write(json.dumps(response.json()))
    print("Got everything I need. Starting download...")
    return filename

import argparse

if __name__ == "__main__":
    if not path.isfile('cookie.txt'):
        print("Coloque o cookie inicial no arquivo cookie.txt")
    with open('cookie.txt') as f:
        starting_cookie = f.read()
        page_headers['Cookie'] = starting_cookie
        api_headers['Cookie'] = starting_cookie
    _id = sys.argv[1] if len(sys.argv) > 1 else None
    main(_id)
