# Read Readme
##### Requisitos
- Python3
- Python3-pip

##### Preparação
```
sudo pip3 install virtualenv
git clone https://github.com/fnzr/minha-biblioteca-jigsaw
cd minha-biblioteca-jigsaw
virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt
```

##### Utilização
1) Através do SIGA3, acesse o site MinhaBiblioteca via Biblioteca > E-books MinhaBiblioteca
2) Abra o Developer's Console (F12?) na aba Network
3) Selecione o livro que você quer baixar
4) Olhe os últimos requests, ignore os \*.svg e procure por `pages` (ou figures, ou bookmarks, ou...)
5) Verifique a Request URL, tem parecer com essa: `https://jigsaw.vitalsource.com/api/v0/books/9788582601044/pages`
6) Na URL que você encontrou, procure nos Reponse Headers pelo parâmetro Set-Cookie. Copie **todo** o valor dele e coloque no arquivo cookie.txt. Sim, é enorme. Se faltar algum caractere não vai funcionar. Se houver caracteres extras não vai funcionar. O cookie que você obtém aqui vale por algumas horas, então não é preciso realizar esse passo todas as vezes.
7) No Request URL, o número que segue `books/` é o ISBN do livro. Use no próximo passo.
8) `python main.py isbn`
9) Se o livro estiver em HTML, será criada uma pasta com o timestamp atual no diretório de execução. Abra o livro em `./[timestamp]/Text/[book_title].html`. Se o livro for um conjunto de imagens, será criado o PDF `./[book_title].pdf`

![picture](http://i.imgur.com/gERRb9G.jpg)
