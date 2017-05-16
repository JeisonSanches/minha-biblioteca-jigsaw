# Read Readme
##### Requisitos
- Python3
- Python3-pip

##### Preparação
```
$ sudo pip3 install virtualenv
$ git clone xxx
$ cd xxx
$ virtualenv -p python3 venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

##### Utilização
1) Através do SIGA3, acesse o site MinhaBiblioteca via Biblioteca > E-books MinhaBiblioteca 
2) Abra o Developer's Console (F12?) na aba Network
3) Selecione o livro que você quer baixar
4) Olhe os últimos requests, ignore os \*.svg e procure por `pages` (ou figures, ou bookmarks, ou...)
5) Verifique a Request URL, tem parecer com essa: `https://jigsaw.vitalsource.com/api/v0/books/9788582601044/pages`
6) Na URL que você encontrou, o número que segue `books/` é o ISBN do livro. Guarde esse número.
7) Nesse mesmo request, procure nos Reponse Headers pelo parâmetro Set-Cookie. Copie **todo** o valor dele e coloque na variável `starting_cookie`. Sim, é enorme. Se faltar algum caractere não vai funcionar.
8) `python main.py :isbn`
9) Se o livro estiver em HTML, será criada uma pasta com o timestamp atual no diretório de execução. Abra o livro em `./[timestamp]/Text/[book_title].html`. Se o livro for um conjunto de imagens, será criado o PDF `./[book_title].pdf`
10) Décimo passo porque 10 é importante.

![picture](http://i.imgur.com/gERRb9G.jpg)
