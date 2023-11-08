import random
import requests
import PyPDF2
import re
import csv
from SPARQLWrapper import SPARQLWrapper, JSON

def check_word_in_geonames(word):
    url = f"http://api.geonames.org/searchJSON?q={word}&maxRows=1&username=demo"
    response = requests.get(url)
    data = response.json()

    if 'geonames' in data and len(data['geonames']) > 0:
        return True
    else:
        return False

def search_gnd(word):
    # GND-API-URL für die Suche nach Geographika
    url = "https://lobid.org/gnd/search?q={}&filter=%2B%28type%3APlaceOrGeographicName%29".format(word)

    # Führe die Anfrage an die GND-API aus
    response = requests.get(url)

    # Überprüfe den Statuscode der Antwort
    if response.status_code == 200:
        # Extrahiere die JSON-Daten aus der Antwort
        data = response.json()

        # Überprüfe, ob es Ergebnisse gibt
        if "member" in data and len(data["member"]) > 0:
            return True
        else:
            return False
    else:
        # Bei einem Fehlercode wird False zurückgegeben
        return False

def has_wikidata_population(word):
    # Erstelle eine SPARQLWrapper-Instanz für die Wikidata-Abfrage-URL
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    # Setze das SPARQL-Abfrage-Skript mit dem übergebenen Wort
    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT ?entity ?population
    WHERE {{
      ?entity wdt:P1082 ?population ;
              rdfs:label "{word}"@en .
    }}
    """

    # Setze das Abfrage-Skript in die SPARQLWrapper-Instanz
    sparql.setQuery(query)

    # Setze das Ausgabeformat auf JSON
    sparql.setReturnFormat(JSON)

    # Führe die SPARQL-Abfrage aus und erhalte die Ergebnisse
    results = sparql.query().convert()

    # Überprüfe, ob es Ergebnisse gibt
    if len(results["results"]["bindings"]) > 0:
        return True
    else:
        return False

def read_pdf(file_path):
    # PDF öffnen und den Text extrahieren
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    # Interpunktion löschen und Wörter trennen
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    #words = capitalize_words(words)

    return words

def capitalize_words(word_list):
    capitalized_words = []
    for word in word_list:
        capitalized_words.append(word.capitalize())
    return capitalized_words

def remove_element_from_list(lst):
    elements = ["und", "oder", "der", "die", "das"]
    for element in elements:
        for word in lst:
            if word == element:
                lst.remove(word)

# Test ob Wörter gelöscht wurden.
def find_element(lst, element):
    if element in lst:
        index = lst.index(element)
        return index
    else:
        return -1   
    
def search_and_write(word_list, output_file):
   
        word_column = []
        previous_words_column = []
        next_words_column = []

        for word in word_list:
            if search_gnd(word):
                word_column.append(word)
                if word_list.index(word) == 0:
                    string = "No previous words."
                elif word_list.index(word) == 1:
                    string = "No word here" + " " + word_list[word_list.index(word) - 2] + " " + word_list[word_list.index(word) - 1]
                elif word_list.index(word) == 2:
                    string = "No word here" + " " + "No word here" + " " + word_list[word_list.index(word) - 1]
                else:
                    string = (word_list[word_list.index(word) - 3]) + " " + word_list[word_list.index(word) - 2] + " " + word_list[word_list.index(word) - 1]
                previous_words_column.append(string)  
            
                
                if word_list.index(word) == len(word_list) -1:
                    string = "No next words."
                elif word_list.index(word) == len(word_list) - 2:
                    string = word_list[word_list.index(word) + 1] + " " + "No word here" + " " + "No word here"
                elif word_list.index(word) == len(word_list) - 3:
                    string = word_list[word_list.index(word) + 1] + " " + word_list[word_list.index(word) + 2] + " " + "No word here"
                else:
                    string = (word_list[word_list.index(word) + 1]) + " " + word_list[word_list.index(word) + 2] + " " + word_list[word_list.index(word) + 3]
                next_words_column.append(string) 

        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Schreibe den Header
            writer.writerow(['Word', 'Previous Words', 'Next Words'])

            # Schreibe die Daten aus den Listen
            for i in range(len(word_column)):
                writer.writerow([word_column[i], previous_words_column[i], next_words_column[i]])

        print(f'Die Datei {output_file} wurde erfolgreich erstellt.')
                
        
# PDF aufrufen, durchsuchbar machen und bereinigen.

pdf_file = (r"C:\Users\muegab00\projekte\reiseberichte\Sitzung Thalmann_26.6.2023_beispiel.pdf")
word_list = read_pdf(pdf_file)
remove_element_from_list(word_list)
#print(word_list)



output_file = 'output.csv'
search_and_write(word_list, output_file)




