import google.generativeai as genai
import PyPDF2
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Configure a API Key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("learnlm-1.5-pro-experimental")

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

def process_pdf_with_gemini(pdf_path):
    # Extract text from the PDF
    extracted_text = extract_text_with_page_info(pdf_path)

    # Send the extracted text to the Gemini model for specific responses
    prompt = f"Extraia as seguintes informações do texto:\n\n" \
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

    # Call the API to process the content
    response = model.generate_content([prompt])
    return response.text

# Modern and organized layout with Streamlit
st.set_page_config(page_title="JurisScanner", page_icon="📜", layout="wide")

# Title
st.title("JurisScanner - Legal Data Extraction System")

# Subtitle
st.subheader("Upload a PDF file and automatically extract key legal information")

# PDF file upload
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# PDF processing
if uploaded_file is not None:
    with st.spinner("Processing the PDF... Please wait a moment"):
        # Save the file temporarily
        with open("uploaded_pdf.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Process the PDF and extract the information
        extracted_data = process_pdf_with_gemini("uploaded_pdf.pdf")

    # Display the extracted information
    st.success("Information successfully extracted!")
    st.subheader("Extracted Results:")
    st.write(extracted_data)

else:
    st.info("Please upload a PDF file to start the extraction.")
