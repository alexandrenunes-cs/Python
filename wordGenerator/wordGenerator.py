# Importing packages
from bs4 import BeautifulSoup
import urllib.request
import requests
import random
from googletrans import Translator
import unidecode

# Defining the Urls
url_words = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
url_en = f'https://www.oxfordlearnersdictionaries.com/us/definition/english/'
url_en_synonyms = f'https://www.thesaurus.com/browse/'
url_pt = f'https://www.dicio.com.br/'

# Getting the HTML
def get_html(url):    
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        print(f'\n[404] Page not found for {url}')
        return None

    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    return soup

# Getting all words
def get_words(url):
    words = []
    try:
        conn = urllib.request.urlopen(url)
        response = urllib.request.urlopen(url_words)
        long_txt = response.read().decode()
        words = long_txt.splitlines()
    except urllib.error.HTTPError as e:
        # Return code error (e.g. 404, 501, ...)
        # ...
        print('\nHTTPError: {}'.format(e.code))
    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        # ...
        print('\nURLError: {}'.format(e.reason))
    else:
        # 200
        # ...
        return words
    
def random_word(words, word_len=3):
    filteredWords =  list(filter(lambda x : len(x) >= word_len , words))
    word = random.choice(filteredWords)
    return word

def get_definition(html, lang):
    all_definitions = []    
    
    if lang == 'en':
        definitions = html.find_all('li', class_='sense')
        if definitions:
            for definition in definitions:
                sense = definition.find('span', class_='def')
                if sense is None:
                    return None
                else:
                    all_definitions.append(sense.text)
        else:
            return None
        
    elif lang == 'pt':
        card = html.find('div', class_='card')

        description = card.find('p',itemprop='description')
        for span in description.find_all('span', class_=None):
            all_definitions.append(span.text)
    else:
        pass
    
    return all_definitions

def get_synonyms(html, lang):
    all_synonyms = []
    all_synonyms_less_used = []
        
    if lang == 'en':       
        synonyms = html.find_all('a', class_='css-18rr30y etbu2a31')
        for synonym in synonyms:
            all_synonyms.append(synonym.text)
            
        synonyms = html.find_all('a', class_='css-7854fb etbu2a31')
        for synonym in synonyms:
            all_synonyms_less_used.append(synonym.text)
    elif lang == 'pt':
        additional_synonyms = html.find('p',class_='adicional sinonimos')
        if additional_synonyms:
            synonyms = additional_synonyms.find_all('a')
            for synonym in synonyms:
                all_synonyms.append(synonym.text)
            return all_synonyms
        else:
            return ['Sem Sinônimos']
    else:
        pass
    
    return (all_synonyms, all_synonyms_less_used)

def get_phrases(html, lang):
    all_examples = []
    if lang == 'en': 
        container = html.find('ol', class_='senses_multiple')
        if container is None:
            container = html.find('ol', class_='sense_single')

        if container is not None:
            examples = container.find_all('span',class_='x')
            if examples is None:
                return None
            for example in examples:
                all_examples.append(example.text)
        else:
             return None
    elif lang == 'pt':
        examples = html.find_all('div', class_='frase')
        if examples:
            for example in examples:
                all_examples.append(example.text)
        else:
            print('\nSem frases')
            return None
    else:
        pass
    
    return all_examples
    
def translate(word):
    translator = Translator()
    palavra = translator.translate(word, src='en', dest='pt').text
    return unidecode.unidecode(palavra.lower())    




if __name__ == "__main__":
    words = get_words(url_words)
    got_a_word = False
    if words:
        while not got_a_word:        
            word = random_word(words)        
            url = f'{url_en}{word}/'
            html_en = get_html(url)
            if html_en:
                definitions = get_definition(html_en, 'en')
                examples = get_phrases(html_en, 'en')
                if definitions and examples:
                    got_a_word = True

        print('\nWord')
        print('--> ' +word)

        if definitions:
            print('\nDefinitions')
            for definition in definitions:
                print('--> ' + definition)

        if examples:
            print('\nExamples')
            for example in examples:
                print('--> ' + example)


        url = f'{url_en_synonyms}{word}/'
        html_syn_en = get_html(url)
        synonyms, synonyms_less_used = get_synonyms(html_syn_en, 'en')
        if synonyms:
            print('\nSynonyms')
            for synonym in synonyms:
                print('--> ' + synonym)

        if synonyms_less_used:
            print('\nSynonyms less common')
            for synonym in synonyms_less_used:
                print('--> ' + synonym)

        # Portuguese    
        palavra = translate(word)
        url = f'{url_pt}{palavra}/'
        html_pt = get_html(url)
        if html_pt:
            definitions = get_definition(html_pt, 'pt')

            print('\nPalavra')
            print('--> ' + palavra)

            if definitions:
                print('\nDefinição')
                for definition in definitions:
                    print('--> ' + definition)

            synonyms = get_synonyms(html_pt, 'pt')
            if synonyms:
                print('\nSinônimos')
                for synonym in synonyms:
                    print('--> ' + synonym)

            examples = get_phrases(html_pt, 'pt')
            if examples:
                print('\nExemplos')
                for example in examples:
                    print('--> ' + example.lstrip())
        else:
            print('\nPalavra não encontrada.')
            
        print('\n\n')
    


        