import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
import io
from openai import OpenAI

# Inizializza client OpenAI (usando la tua chiave API GPT-4 a pagamento)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Estrazione Busta Paga con GPT-4 Vision", layout="centered")
st.title("📄 Estrazione intelligente da Busta Paga con Vision")

uploaded_file = st.file_uploader("Carica una busta paga (solo PDF)", type=["pdf"])

def convert_pdf_first_page_to_image(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    page = doc.load_page(0)  # Prima pagina
    pix = page.get_pixmap(dpi=300)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return image

def estrai_info_da_immagine(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
Ti invio una busta paga sotto forma di immagine.

Per favore, estrai in formato JSON le seguenti informazioni:
- DIPENDENTE:
  - paga_base
  - livello
  - ccnl
  - mansione
- AZIENDA:
  - ragione_sociale
  - indirizzo
  - partita_iva

Se un'informazione non è presente, lascia il campo vuoto.
Restituisci solo un oggetto JSON valido.
"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/png;base64," + buffer.getvalue().hex()
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content

if uploaded_file:
    st.info("📄 Documento caricato, elaborazione in corso...")

    image = convert_pdf_first_page_to_image(uploaded_file)
    st.image(image, caption="📷 Anteprima prima pagina")

    with st.spinner("Estrazione con GPT-4 Vision..."):
        output = estrai_info_da_immagine(image)
        st.success("✅ Estrazione completata!")
        st.subheader("📊 Risultato Estratto")
        st.code(output, language="json")

