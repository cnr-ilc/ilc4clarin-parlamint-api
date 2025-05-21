import stanza

# Carica il modello NLP una sola volta
stanza.download('it')
nlp = stanza.Pipeline('it')

def get_nlp():
    return nlp
