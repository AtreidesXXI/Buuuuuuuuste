import streamlit as st
import requests
from openai import OpenAI

# Inizializza OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

OCR_API_KEY = st.secrets["OCR_SPACE_API_KEY"]  # Inserita nei secrets Streamlit

st.set_page_config(page_title="Estrazione Busta Paga (OCR+GPT)", layout="centered")
st.title("📄 Estrazione da Busta Paga con OCR + GPT-4")

uploaded_file = st.file_uploader("Carica una busta paga in PDF (anche scansionata)", type=["pdf"])

def estrai_testo_da_pdf_ocr(file):
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": file},
        data={"language": "ita", "isOverlayRequired": False},
        headers={"apikey": OCR_API_KEY},
    )
    result = response.json()
    if result.get("IsErroredOnProcessing") or "ParsedResults" not in result:
        return ""
    return result["ParsedResults"][0]["ParsedText"]

def estrai_info_con_gpt(testo):
    prompt = f"""
Estrai in formato JSON queste informazioni da una busta paga:

- dipendente:
  - paga_base
  - livello
  - ccnl
  - mansione

- azienda:
  - ragione_sociale
  - indirizzo
  - partita_iva

Testo:
{text}
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sei un assistente esperto in buste paga italiane."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

if uploaded_file:
    st.info("📤 Documento caricato. Invio all’OCR...")
    testo = estrai_testo_da_pdf_ocr(uploaded_file)
    if not testo.strip():
        st.error("⚠️ Non è stato possibile leggere testo dal PDF.")
    else:
        st.subheader("📜 Testo estratto (OCR):")
        st.text_area("Testo:", testo, height=200)

        with st.spinner("📊 Estrazione dati con GPT-4 in corso..."):
            output = estrai_info_con_gpt(testo)
            st.success("✅ Estrazione completata!")
            st.code(output, language="json")


