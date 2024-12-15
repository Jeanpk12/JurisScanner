import google.generativeai as genai
import PyPDF2
import streamlit as st
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Configure a API Key
genai.configure(api_key=API_KEY)
primary_model = genai.GenerativeModel("gemini-1.5-flash")
verification_model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text
        return extracted_text

def extract_text_with_page_info(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = ""
        page_number = 1
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += f"Page {page_number}:\n{text}\n\n"
            page_number += 1
        return extracted_text

async def process_pdf_with_gemini(pdf_path):
    extracted_text = extract_text_with_page_info(pdf_path)

    # Primary extraction
    primary_prompt = f"Extraia as seguintes informações do texto:\n\n" \
                     f"- Nome dos autores: [NOME] (página [NÚMERO])\n" \
                     f"- Data de ingresso da ação: [DATA] (página [NÚMERO])\n" \
                     f"- Data de tomada de posse: [DATA] (página [NÚMERO])\n" \
                     f"- Bairro do imóvel usucapiendo: [BAIRRO] (página [NÚMERO])\n" \
                     f"- Quadra e lote onde o imóvel está: [QUADRA] (página [NÚMERO])\n" \
                     f"- Número do cadastro junto a prefeitura: [NÚMERO DO CADASTRO] (página [NÚMERO])\n" \
                     f"- Interesse da prefeitura na ação: [SIM OU NAO] (página [NÚMERO])\n" \
                     f"- Nome dos antigos proprietários: [NOME] (página [NÚMERO])\n" \
                     f"- Status da sentença (Sim ou Não): [SIM OU NAO] (se sim, página [NÚMERO])\n\n" \
                     f"Texto extraído:\n{extracted_text}"

    primary_response = primary_model.generate_content([primary_prompt])
    primary_results = primary_response.text

    # Immediately return primary results for display
    return primary_results

async def verify_results_with_gemini(primary_results):
    verification_prompt = f"Verifique a consistência das seguintes informações extraídas de um documento legal. Certifique-se de que as informações estão corretas e que as páginas correspondentes são coerentes com os dados apresentados:\n\n" \
                          f"{primary_results}\n\n" \
                          f"Para cada item, responda:\n" \
                          f"- Está correto? (Sim ou Não)\n" \
                          f"- Caso não esteja correto, forneça a correção e a página onde foi encontrada.\n" \
                          f"- Justifique a revisão (se necessário)."

    verification_response = verification_model.generate_content([verification_prompt])
    verified_results = verification_response.text
    return verified_results

# Streamlit configuration for modern UI
st.set_page_config(page_title="JurisScanner", page_icon="📜", layout="wide")

# Sidebar for navigation and extra info
st.sidebar.title("JurisScanner")
st.sidebar.write("**Legal Data Extraction System**")
st.sidebar.markdown("---")
st.sidebar.info(
    "👋 **How does it work?**\n\n"
    "- Upload a PDF file.\n"
    "- Our system automatically extracts important legal information.\n"
    "- View the results on the main panel."
)

# Main title and description
st.title("📜 JurisScanner")
st.markdown(
    """
    **Turn legal PDF files into structured information!**
    Upload documents and automatically get organized and specific data.
    """
)

# Upload PDF file section
st.markdown("### 🔍 **Upload PDF File**")
uploaded_file = st.file_uploader(
    "Drag or select a PDF file", type="pdf", label_visibility="collapsed"
)

# Display spinner and results
if uploaded_file is not None:
    with st.spinner("⏳ Extracting primary results..."):
        with open("uploaded_pdf.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        pdf_path = "uploaded_pdf.pdf"

        # Run primary extraction and display the results immediately
        primary_results = asyncio.run(process_pdf_with_gemini(pdf_path))
        st.success("🎉 Primary extraction completed!")
        st.markdown("### 📋 **Extracted Results (Primary)**")
        st.write(primary_results)

        # Start verification in the background
        with st.spinner("⏳ Verifying results in the background..."):
            verified_results = asyncio.run(verify_results_with_gemini(primary_results))
            st.success("🎉 Verification completed!")
            st.markdown("### 📋 **Verified Results**")
            st.write(verified_results)

    # Download button for results
    st.markdown("### 💾 **Save Results**")
    st.download_button(
        label="📥 Download Verified Results as TXT",
        data=verified_results,
        file_name="verified_results.txt",
        mime="text/plain"
    )
else:
    st.info("📂 Please upload a PDF file to start extraction.")

# Footer with credits
st.markdown("---")
st.markdown(
    "<div style='text-align: center;'>"
    "Created by Jean Oliveira with AI technologies 🌟</div>",
    unsafe_allow_html=True
)
