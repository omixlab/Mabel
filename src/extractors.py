import methods

# Um form será recebido
form = {
    'keyword': '(cancer of the prostate) AND (molecular targeted therapy)',
    'num_of_articles': 10,
    'pubmed': True,
    'scidir': True,
    'scopus': True
}

def main():
    # Chamar as funções
    extract = methods.Extractor(form['keyword'], form['num_of_articles'])
    if form['pubmed']:                  
        extract.pubmed()
    if form['scidir']:
        extract.scidir()
    if form['scopus']:
        extract.scopus()


if __name__ == '__main__':
    main()
