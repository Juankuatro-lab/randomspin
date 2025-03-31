# Générateur de Spuns (Spun Generator)

## Description

Ce projet est une application Streamlit qui permet de générer des variations de texte (spuns) en utilisant des modèles de texte prédéfinis et des variables personnalisables.

## Fonctionnalités principales

- Génération de variations de texte à partir de fichiers modèles
- Support pour les fichiers texte (.txt) et Word (.docx)
- Utilisation de variables et d'options de spinning
- Interface utilisateur conviviale avec Streamlit
- Exportation des résultats en fichier Excel

## Prérequis

- Python 3.7+
- Bibliothèques requises :
  - streamlit
  - pandas
  - python-docx
  - openpyxl

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-utilisateur/spun-generator.git
cd spun-generator
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

### Fichiers requis

1. **Fichier modèle** (.txt ou .docx) : 
   - Contient le texte de base à spinner
   - Peut inclure des variables (`$variable`) 
   - Prend en charge les options de spinning :
     - Options simples : `{option1|option2}`
     - Options de paragraphe : `{{paragraphe1|paragraphe2}}`

2. **Fichier Excel des variables** (.xlsx) :
   - Contient les valeurs pour les variables du modèle
   - Chaque colonne représente une variable
   - Chaque ligne sera utilisée pour générer un spun unique

### Lancement de l'application

```bash
streamlit run spun_generator.py
```

## Syntaxe de spinning

### Variables
- Utilisez `$nom_variable` pour insérer des valeurs dynamiques

### Options simples
- `{option1|option2}` choisira aléatoirement entre les options

### Options de paragraphe
- `{{paragraphe1|paragraphe2}}` permet de spinner des blocs de texte plus importants

## Exemple

### Fichier modèle
```
Bonjour, je m'appelle $nom et j'ai {26|27|28} ans. 
{{Je suis un développeur passionné.|Je travaille dans le domaine de la tech.}}
```

### Fichier Excel de variables
| nom    | autre_variable |
|--------|----------------|
| Alice  | valeur1        |
| Bob    | valeur2        |

## Contribution

Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue.
