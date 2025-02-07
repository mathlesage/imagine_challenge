import streamlit as st

import streamlit as st
import docx
from openai import OpenAI

# ATTENTION : Gardez votre clé API en sécurité !
api_key = st.secrets["API"]
client = OpenAI(api_key=api_key)

def extract_text_from_docx(file) -> str:
    """
    Extrait et renvoie le texte contenu dans un fichier Word (.docx).
    """
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def analyze_criterion(criterion: dict, document_text: str) -> int:
    """
    Construit un prompt pour le critère donné et appelle l’API afin d'obtenir uniquement une note (1, 2 ou 3).
    """
    prompt = f"""
Critère : {criterion['name']}
Description : {criterion['description']}
Système de notation :
{criterion['scale']}

Voici le texte extrait du document :
{document_text}

En te basant sur ce texte, attribue uniquement une note pour ce critère selon le système de notation ci-dessus.
Réponds uniquement par un entier qui représente la note (1, 2 ou 3).
"""
    response = client.chat.completions.create(
        temperature=0.0,
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    output_text = response.choices[0].message.content.strip()
    try:
        score = int(output_text)
    except Exception:
        score = 0
    return score

def get_comment_from_scale(scale: str, score: int) -> str:
    """
    Extrait le commentaire associé à la note dans le champ 'scale'.
    Par exemple, si scale vaut :
      "1 : Tous les travailleurs ont des EPI et les portent
       2 : EPI disponibles mais pas toujours portés
       3 : Manque d’EPI ou refus de les porter"
    et score == 1, la fonction renverra "Tous les travailleurs ont des EPI et les portent".
    """
    for line in scale.splitlines():
        if line.strip().startswith(str(score)):
            parts = line.split(":", 1)
            if len(parts) > 1:
                return parts[1].strip()
    return ""

def get_global_evaluation(total_score: int) -> str:
    """
    Retourne une conclusion globale en fonction du score total :
      - 10 à 15 : Chantier très sécurisé 
      - 16 à 25 : Sécurité moyenne, améliorations nécessaires 
      - > 25   : Chantier dangereux, action urgente requise
    """
    if 10 <= total_score <= 15:
        return "Chantier très sécurisé"
    elif 16 <= total_score <= 25:
        return "Sécurité moyenne, améliorations nécessaires"
    elif total_score > 25:
        return "Chantier dangereux, action urgente requise"
    else:
        return "Score invalide"

# Définition des critères de notation
criteria = [
    {
        "name": "Risque lié aux matériaux dangereux",
        "description": "Présence et gestion des matériaux dangereux sur le chantier (ex. amiante, solvants, gaz toxiques, poussières fines).",
        "scale": "1 : Aucun matériau dangereux ou mesures de protection complètes\n2 : Matériaux dangereux présents mais gérés partiellement\n3 : Matériaux dangereux en grande quantité et mal maîtrisés"
    },
    {
        "name": "Risque de chute en hauteur",
        "description": "Présence de travaux en hauteur et mise en place de protections (échafaudages, harnais, garde-corps).",
        "scale": "1 : Pas de travail en hauteur ou protections complètes\n2 : Travail en hauteur avec certaines mesures de sécurité\n3 : Travail en hauteur sans protections suffisantes"
    },
    {
        "name": "Risque lié aux engins et machines",
        "description": "Utilisation d’engins lourds et formation des opérateurs (grues, pelleteuses, scies électriques).",
        "scale": "1 : Machines bien entretenues et opérateurs formés\n2 : Machines en bon état mais formations partielles\n3 : Machines vétustes, absence de formation"
    },
    {
        "name": "Conditions climatiques et exposition",
        "description": "Impact des conditions météo sur la sécurité (chaleur, froid extrême, pluie, vent fort).",
        "scale": "1 : Conditions normales ou adaptation parfaite\n2 : Conditions difficiles avec protection partielle\n3 : Conditions extrêmes avec peu d’adaptation"
    },
    {
        "name": "Fatigue et charge de travail",
        "description": "Heures travaillées par jour et pauses respectées.",
        "scale": "1 : Temps de travail raisonnable et pauses respectées\n2 : Horaires prolongés avec quelques pauses oubliées\n3 : Horaires excessifs, fatigue intense"
    },
    {
        "name": "Formation et sensibilisation à la sécurité",
        "description": "Pourcentage des travailleurs ayant suivi une formation sécurité.",
        "scale": "1 : 100% des travailleurs formés\n2 : 50-99% des travailleurs formés\n3 : Moins de 50% des travailleurs formés"
    },
    {
        "name": "Qualité des équipements de protection individuelle",
        "description": "Disponibilité et port des équipements (casques, gants, lunettes, masques, chaussures de sécurité).",
        "scale": "1 : Tous les travailleurs ont des EPI et les portent\n2 : EPI disponibles mais pas toujours portés\n3 : Manque d’EPI ou refus de les porter"
    },
    {
        "name": "Sécurité des circulations sur le chantier",
        "description": "Organisation des voies de circulation pour piétons et véhicules.",
        "scale": "1 : Zones bien séparées et signalisation claire\n2 : Séparation partielle ou signalisation insuffisante\n3 : Mélange dangereux entre véhicules et piétons"
    },
    {
        "name": "Bruit et pollution sonore",
        "description": "Niveau sonore sur le chantier et protections auditives.",
        "scale": "1 : Bruit faible ou protections disponibles\n2 : Bruit élevé avec protections limitées\n3 : Bruit excessif sans protection"
    },
    {
        "name": "Gestion des situations d’urgence (incendie, évacuation, premiers secours)",
        "description": "Présence de procédures d’urgence et de premiers secours.",
        "scale": "1 : Plans clairs, exercices réalisés, trousses de secours accessibles\n2 : Plans existants mais peu appliqués\n3 : Absence de plans ou matériel de secours"
    }
]

# --- Interface Streamlit ---
st.title("Évaluation de la sécurité d'un chantier - Notes et commentaires")
st.write("Déposez un fichier Word (.docx) contenant le rapport de chantier pour obtenir les notes par critère et leurs commentaires associés.")

uploaded_file = st.file_uploader("Choisissez un fichier Word", type=["docx"])

if uploaded_file is not None:
    with st.spinner("Extraction du texte..."):
        document_text = extract_text_from_docx(uploaded_file)
    st.success("Texte extrait avec succès !")
    
    st.subheader("Texte extrait")
    st.text_area("Contenu du document", document_text, height=300)
    
    st.subheader("Notes par critère")
    total_score = 0
    for criterion in criteria:
        st.markdown(f"**Critère : {criterion['name']}**")
        with st.spinner(f"Analyse du critère '{criterion['name']}'..."):
            score = analyze_criterion(criterion, document_text)
        # Récupération du commentaire associé à la note depuis le scale
        comment = get_comment_from_scale(criterion['scale'], score)
        st.write(f"**Note :** {score} - **Commentaire :** {comment}")
        total_score += score

    st.subheader("Score global")
    st.write(f"**Score total :** {total_score}")
    global_evaluation = get_global_evaluation(total_score)
    st.write(f"**Conclusion :** {global_evaluation}")
