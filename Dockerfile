# Usa l'immagine ufficiale di Python come base
FROM python:3.9-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia il file requirements.txt e installa le dipendenze
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutti i file del progetto nella directory di lavoro del container
COPY . .

# Scarica il modello Stanza italiano e pre-caricalo
RUN python -c "import stanza; stanza.download('it')"

# Espone la porta su cui verrà eseguita l'applicazione
EXPOSE 8000

# Comando per avviare l'applicazione FastAPI con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]