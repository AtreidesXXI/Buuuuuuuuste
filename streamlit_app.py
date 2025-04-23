import streamlit as st
import fitz  # PyMuPDF per OCR da PDF scansionati
import pytesseract
from PIL import Image
from openai import OpenAI  # Nuova API OpenAI

# Inizializza client OpenAI con la chiave da secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Estrazione Busta Paga con AI", layout="centered")
st.title("📄 Estrazione Intelligente da Busta Paga")

uploaded_file = st.file_uploader("Carica una busta paga (PDF o Immagine)", type=["pdf", "png", "jpg", "jpeg"])

# OCR per immagini
def image_to_text(image_file):
    image = Image.open(image_file)
    return pytesseract.image_to_string(image, lang='ita')

# Prompt AI
def estrai_info_con_ai(testo):
    prompt = f"""
Ti fornirò il testo di una busta paga italiana. Da questo testo, estrai in modo preciso le seguenti informazioni e restituiscile in JSON.

- DIPENDENTE:
    - paga_base
    - livello
    - ccnl
    - mansione

- AZIENDA:
    - ragione_sociale
    - indirizzo
    - partita_iva

Formato JSON di esempio:
{{
    "dipendente": {{
        "paga_base": "1450,00 €",
        "livello": "2",
        "ccnl": "Commercio",
        "mansione": "Addetto vendite"
    }},
    "azienda": {{
        "ragione_sociale": "Supermarket S.r.l.",
        "indirizzo": "Via Roma 123, Milano",
        "partita_iva": "12345678901"
    }}
}}

Testo busta paga:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sei un assistente esperto nell'estrazione di dati da documenti."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content

# Processo file
if uploaded_file:
    st.info("📤 Documento caricato. Inizio elaborazione...")

    if uploaded_file.type == "application/pdf":
        # OCR su PDF (ogni pagina convertita in immagine)
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        testo = ""
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            testo += pytesseract.image_to_string(img, lang="ita") + "\n"
    else:
        testo = image_to_text(uploaded_file)

    # Mostra testo grezzo per debugging
    st.subheader("🧾 Testo grezzo della busta paga (debug)")
    st.text(testo)

    if testo.strip():
        st.subheader("📜 Testo estratto")
        st.text_area("Contenuto del documento:", testo, height=200)

        with st.spinner("Estrazione delle informazioni con IA in corso..."):
            output = estrai_info_con_ai(testo)
            st.success("✅ Estrazione completata!")
            st.subheader("📊 Risultato Estratto")
            st.code(output, language="json")
    else:
        st.error("⚠️ Non è stato possibile estrarre testo leggibile dal documento.")
