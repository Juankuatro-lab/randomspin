import re
import random
import pandas as pd
import streamlit as st
from docx import Document
import openpyxl
from io import BytesIO

# Configuration de la page
st.set_page_config(
    page_title="Générateur de Spins",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #3366FF;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #0047AB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .file-upload-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .preview-container {
        background-color: #eef2f7;
        padding: 20px;
        border-radius: 10px;
        margin-top: 30px;
    }
    .stButton>button {
        background-color: #3366FF;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #0047AB;
    }
    .download-button {
        text-align: center;
        margin-top: 20px;
    }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stTextArea>div>div {
        background-color: white;
        border-radius: 5px;
    }
    .footer {
        text-align: center;
        color: #888888;
        margin-top: 50px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

class SpinGenerator:
    def __init__(self):
        self.variable_pattern = r'\$(\w+)'

    def replace_variables(self, text, variables_dict):
        """Remplace les variables par leurs valeurs"""
        for var, value in variables_dict.items():
            if var in text:  # Vérifie si la variable existe dans le texte
                text = text.replace(f'${var}', str(value) if value is not None else '')
        return text

    def choose_option(self, options):
        """Choisit une option aléatoire"""
        return random.choice(options) if options else ''

    def find_matching_brace(self, text, start):
        """Trouve l'accolade fermante correspondante"""
        count = 1
        pos = start + 1
        while count > 0 and pos < len(text):
            if text[pos] == '{':
                count += 1
            elif text[pos] == '}':
                count -= 1
            pos += 1
        return pos if count == 0 else -1

    def process_simple_options(self, text):
        """Règle 1: Traite les options simples {opt1|opt2}"""
        while True:
            match = re.search(r'{([^{}]+)}', text)
            if not match:
                break
            
            options = [opt.strip() for opt in match.group(1).split('|')]
            chosen = self.choose_option(options)
            text = text[:match.start()] + chosen + text[match.end():]
        
        return text

    def process_paragraph_options(self, text):
        """Règle 3: Traite les options de paragraphe {{para1|para2}}"""
        def split_options(content):
            """Sépare les options de paragraphe en gérant les imbrications"""
            options = []
            current = ''
            depth = 0
            
            for char in content + '|':
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                
                if char == '|' and depth == 0:
                    if current.strip():  # Ne garde que les options non vides
                        options.append(current.strip())
                    current = ''
                else:
                    current += char
                    
            if current.strip():  # Ajoute la dernière option si non vide
                options.append(current.strip())
            return options

        result = text
        pattern = r'\{\{([^{}]|{[^{}]*})*\}\}'
        
        while True:
            match = re.search(pattern, result, re.DOTALL)
            if not match:
                break
            
            full_match = match.group(0)
            content = full_match[2:-2]
            
            options = split_options(content)
            if options:
                chosen = self.choose_option(options)
                processed = self.process_simple_options(chosen)
                result = result[:match.start()] + processed + result[match.end():]
            else:
                result = result[:match.start()] + content + result[match.end():]
        
        return result

    def generate_spin(self, text, variables_dict):
        """Génère un spin complet en appliquant les règles dans l'ordre"""
        text = self.process_paragraph_options(text)
        text = self.process_simple_options(text)
        text = self.replace_variables(text, variables_dict)
        return text

def process_input_file(file_bytes):
    """Traite le fichier d'entrée (txt ou docx)"""
    try:
        if file_bytes.name.endswith('.docx'):
            doc = Document(BytesIO(file_bytes.read()))
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        else:  # txt
            content = file_bytes.read()
            if isinstance(content, bytes):
                return content.decode('utf-8')
            return content
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier: {str(e)}")
        raise

def generate_spins(input_text, df_variables, num_spins):
    """Génère les spins et retourne un DataFrame"""
    generator = SpinGenerator()
    results = []
    
    for index, row in df_variables.iterrows():
        if index >= num_spins:
            break
        
        variables_dict = row.to_dict()
        spin_text = generator.generate_spin(input_text, variables_dict)
        spin_text = spin_text.replace('###devider###', '###devider###\n')
        results.append([index + 1, spin_text])
    
    return pd.DataFrame(results, columns=['Spin_ID', 'Texte_Généré'])

def create_streamlit_app():
    st.title("Générateur de Spins")
    
    # Upload des fichiers
    text_file = st.file_uploader("Fichier texte (.txt ou .docx)", type=['txt', 'docx'])
    excel_file = st.file_uploader("Fichier Excel des variables", type=['xlsx'])
    
    # Nombre de spins à générer
    num_spins = st.number_input("Nombre de spins à générer", min_value=1, value=1)
    
    # Prévisualisation
    preview_count = st.number_input("Nombre de spins à prévisualiser", min_value=1, max_value=5, value=1)
    
    if st.button("Générer les spins") and text_file and excel_file:
        try:
            with st.spinner('Génération des spins en cours...'):
                # Lecture des fichiers
                input_text = process_input_file(text_file)
                df_variables = pd.read_excel(excel_file)
                
                # Génération des spins
                df_results = generate_spins(input_text, df_variables, num_spins)
                
                # Affichage de la prévisualisation
                st.subheader("Prévisualisation des spins générés")
                for i in range(min(preview_count, len(df_results))):
                    with st.expander(f"Spin #{df_results.iloc[i]['Spin_ID']}", expanded=i==0):
                        st.text_area(
                            "Texte généré",
                            value=df_results.iloc[i]['Texte_Généré'],
                            height=200,
                            disabled=True
                        )
                
                # Création du fichier Excel pour le téléchargement
                output = BytesIO()
                df_results.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                
                # Bouton de téléchargement
                st.download_button(
                    label="Télécharger tous les spins générés",
                    data=output,
                    file_name="spins_generes.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"Une erreur s'est produite: {str(e)}")

if __name__ == "__main__":
    create_streamlit_app()
