import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image
from openai import OpenAI  # ✅ Nuova importazione

# ✅ Inizializza client OpenAI con chiave dalle secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Estrazione Busta Paga con AI", layout="centered")
st.title("📄 Estrazione Intelligente da Busta Paga")

# ✅ Caricamento file
uploaded_file = st.file_uploader("Carica una busta paga (PDF o Immagine)", type=["pdf", "png", "jpg", "jpeg"])

# ✅ OCR immagine
def image_to_text(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image, lang='ita')
    return text

# ✅ Estrazione testo da PDF
def pdf_to_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# ✅ Prompt e richiesta al modello GPT-4
def estrai_info_con_ai(testo):
    prompt = f"""
    Estrai le seguenti informazioni dalla busta paga qui sotto:

    COLONNA 1 - DIPENDENTE:
    - Paga base
    - Livello
    - CCNL applicato
    - Mansione

    COLONNA 2 - AZIENDA:
    - Ragione sociale
    - Indirizzo
    - Partita IVA

    Restituisci la risposta in questo formato JSON:
    {{
        "dipendente": {{
            "paga_base": "",
            "livello": "",
            "ccnl": "",
            "mansione": ""
        }},
        "azienda": {{
            "ragione_sociale": "",
            "indirizzo": "",
            "partita_iva": ""
        }}
    }}

    Testo della busta paga:
    {testo}
    """

    response = client.chat.completions.create(  # ✅ Nuovo metodo corretto
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sei un assistente esperto nell'estrazione di dati da documenti."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content

# ✅ Esecuzione dopo caricamento
if uploaded_file:
    st.info("📤 Documento caricato. Inizio elaborazione...")

    # Estrazione testo
    if uploaded_file.type == "application/pdf":
        testo = pdf_to_text(uploaded_file)
    else:
        testo = image_to_text(uploaded_file)

    if testo.strip():
        st.subheader("📜 Testo estratto")
        st.text_area("Contenuto del documento:", testo, height=200)

        with st.spinner("Estrazione delle informazioni con IA in corso..."):
            output = estrai_info_con_ai(testo)
            st.success("✅ Estrazione completata!")
            st.subheader("📊 Risultato Estratto")
            st.code(output, language="json")
    else:
        st.error("⚠️ Impossibile estrarre testo dal documento. Prova con un altro file.")

