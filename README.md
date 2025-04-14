# Estrazione Busta Paga con Streamlit + GPT-4

Questa web app permette di caricare una busta paga in PDF o immagine e usare l'intelligenza artificiale per estrarre le seguenti informazioni:

**Dipendente**:
- Paga base
- Livello
- CCNL
- Mansione

**Azienda**:
- Ragione sociale
- Indirizzo
- Partita IVA

## Come usare
1. Aggiungi la tua chiave API OpenAI nei `Secrets` su Streamlit Cloud come `OPENAI_API_KEY`
2. Carica il file `streamlit_app.py` e `requirements.txt` su GitHub
3. Collega il repository a Streamlit Cloud e deploya
