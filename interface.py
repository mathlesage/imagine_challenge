import streamlit as st

import streamlit as st
from fpdf import FPDF
import io

# Initialisation du nombre de lignes dans la session
if 'rows' not in st.session_state:
    st.session_state['rows'] = 1

# Dictionnaire des facteurs d'émission carbone (en kg CO₂ par unité)
carbon_factors = {
    "Chemin de câble NIEDAX France MTC H105": 0.0,
    "Isoconfort 35 Revêtu Kraft 240": 4.66,
    "Revêtements de sols StudSytem Zeus": 24.5,
    "Revêtements de sols PlanSystem Granito": 15.4,
    "FENÊTRES ET PORTES-FENÊTRES MIXTES BOIS-ALUMINIUM TRIPLE VITRAGE MINCO": 84.1,
    "FBT PR": 1.82,
    "Panneaux Rigides Isolants en Polyuréthane Ep 40 mm KNAUF Asfalthane": 6.19,
    "Panneaux Rigides Isolants en Polyuréthane Ep 100 mm KNAUF SteelThane": 16.1,
    "Panneaux Rigides Isolants en Polyuréthane Ep 120 mm KNAUF SteelThane": 19.6,
    "Panneaux Rigides Isolants en Polyuréthane Ep 140 mm KNAUF SteelThane": 22.7,
    "Panneau Isolant KNAUF Thane Dallage 132mm": 18.5,
    "Panneau Isolant KNAUF Thane Dallage 100mm": 13.9,
    "Panneaux Rigides Isolants en Polyuréthanne Ep 80mm KNAUF Thane ET Se": 11.7,
    "Panneaux Rigides Isolants en Polyuréthane Ep 100mm KNAUF Thane ET Se": 13.9,
    "Panneaux Rigides Isolants en Polyuréthane Ep 120mm KNAUF Thane ET Se": 17.5,
    "Panneaux Rigides Isolants en Polyuréthanne Ep 130mm KNAUF Thane ET Se": 18.5,
    "Panneaux Rigides Isolants en Polyuréthane Ep 120 mm KNAUF Thane Façade MI": 19.4,
    "Panneaux Rigides Isolants en Polyuréthane Ep 82 mm KNAUF Thane Façade MI": 12.8,
    "Panneaux Rigides Isolants en Polyuréthane Ep 140 mm KNAUF Thane Façade": 22.9,
    "Panneaux Rigides Isolants en Polyuréthane Ep 82 mm KNAUF Thane Façade": 15.1,
    "Panneaux Rigides Isolants en Polyuréthane Ep 100 mm KNAUF Thane Façade MI": 13.4,
    "Panneaux Rigides Isolants en Polyuréthane Ep 100 mm KNAUF Thane Façade": 16.0,
    "Panneau Isolant KNAUF Thane MulTTI Se 100mm": 13.5,
    "Panneau Isolant KNAUF Thane MulTTI Se 80mm": 11.6,
    "Panneau Isolant KNAUF Thane MulTTI Se 120mm": 17.0,
    "RCBO 1P+N 6kA C-20A 30mA type A": 0.0,
    "Panneaux Rigides Isolants en Polyuréthane Ep 100 mm KNAUF Thane Mur B2i": 13.7,
    "Panneaux Rigides Isolants en Polyuréthane Ep 120 mm KNAUF Thane Mur B2i": 17.2,
    "Panneaux Rigides Isolants en Polyuréthane Ep 140 mm KNAUF Thane Mur B2i": 20.2,
    "Panneaux Rigides Isolants en Polyuréthane Ep 100 mm KNAUF Thane Mur RB2": 13.9,
    "Panneaux Rigides Isolants en Polyuréthane Ep 120 mm KNAUF Thane Mur RB2": 17.1,
    "Panneaux Rigides Isolants en Polyuréthane Ep 56mm KNAUF Thane Sol": 8.94,
    "Panneaux Rigides Isolants en Polyuréthane Ep 80mm KNAUF Thane Sol": 12.1,
    "Panneaux Rigides Isolants en Polyuréthane Ep 100mm KNAUF Thane Sol": 13.7,
    "Panneau Isolant QUICKCIEL PU Façade MI 82mm": 12.8,
    "Panneau Isolant QUICKCIEL PU Façade MI 100mm": 13.4,
    "Panneau Isolant QUICKCIEL PU Façade MI 120mm": 19.4,
    "Panneau Isolant QUICKCIEL Sarking 90mm": 13.6,
    "Panneau Isolant QUICKCIEL Sarking 132mm": 18.8,
    "Panneau Isolant QUICKCIEL Sarking 160mm": 23.0,
    "KNAUF Entrevous Th36 Hourdiversel et KNAUF Treillis Therm Coffrant": 19.1,
    "Entrevous KNAUF Therm Th38": 13.2,
    "KNAUF Perimaxx 108mm": 22.2,
    "KNAUF Perimaxx 148mm": 31.5,
    "Rupteur KNAUF RTK²": 1.67,
    "KNAUF Therm ATTIK Se 200mm": 13.5,
    "KNAUF Therm Chape Th38 200mm": 7.53,
    "KNAUF Therm Dallage Basis 80mm": 6.28,
    "KNAUF Therm Dallage Basis 100mm": 7.97,
    "KNAUF Therm Dalle Portée Rc50 100mm": 4.28,
    "KNAUF Therm Dalle Portée Rc50 180mm": 6.72,
    "KNAUF ITEx Th38 SE 200mm": 9.09,
    "Béton de propreté": 4.20,
    "Maçonnerie de fondation en moellons": 57.90,
    "Châpe": 122.70,
    "Béton armé": 4.92,
    "Gouttières métalliques": 61.70,
    "Revêtement en carreaux dans les salles d'eau": 84.50,
    "Pavement en carreaux": 134.60,
    "Maçonnerie de trottoirs en carreaux": 36.06,
    "Portes et fenêtres métallique vitrée et grillagées": 34.20,
    "Portes intérieur simple en bois massif": 11.0,
    "tubage et câblage": 1.0,
    "plafonniers": 11.0,
    "lampe au dessus de miroirs": 2.0,
    "interrupteur double direction": 12.0,
    "interrupteur simple": 7.0,
    "applique murale": 8.0,
    "prise de courant simple": 28.0,
    "tuyauterie d'alimentation": 1.0,
    "tuyauterie d'évacuation": 1.0,
    "douche+accessoires": 2.0,
    "lavabo+accessoires": 2.0,
    "wc l'anglaise": 2.0,
    "evier double de cuisine": 1.0,
    "miroir": 2.0,
    "regard de visite": 9.0,
    "émail sur structure métallique": 74.3,
    "vernis sur portes en bois+plafond": 253.23,
    "béton de propreté": 2.7,
    "chape sur fondation": 95.0,
    "clôture en briques cuites": 32.24,
    "clôture en structures métalliques": 30.75,
    "aménagement de la cour intérieure en pavé de béton": 88.94,
    "portail d'entrée": 1.0
}


# Liste des matériaux disponibles (les clés du dictionnaire)
available_materials = list(carbon_factors.keys())

st.title("Devis Matériaux : Calcul de l'Empreinte Carbone")
st.write("Utilisez la barre de recherche pour sélectionner un matériau et renseigner la quantité.")

# Fonction pour ajouter une nouvelle ligne
def add_row():
    st.session_state['rows'] += 1

# Affichage des lignes pour la saisie des matériaux
for i in range(st.session_state['rows']):
    st.markdown(f"#### Matériau {i+1}")

    # Barre de recherche pour filtrer les matériaux
    search_input = st.text_input("Rechercher un matériau", key=f"search_{i}")
    if search_input:
        filtered_materials = [m for m in available_materials if search_input.lower() in m.lower()]
    else:
        filtered_materials = available_materials

    # Si aucun matériau ne correspond à la recherche, on affiche un avertissement
    if not filtered_materials:
        st.warning("Aucun matériau trouvé. Veuillez modifier votre recherche.")
        selected_material = ""
    else:
        # Sélection parmi les matériaux filtrés
        selected_material = st.selectbox("Sélectionnez le matériau", filtered_materials, key=f"material_{i}")
    
    # Saisie de la quantité pour ce matériau
    quantity = st.number_input("Quantité", min_value=0.0, value=0.0, step=0.1, key=f"quantity_{i}")

    st.markdown("---")

# Champ de saisie pour la superficie (en m²)
superficie = st.number_input("Saisir la superficie (en m²)", min_value=0.0, value=0.0, step=0.1, key="superficie")

# Bouton pour ajouter une nouvelle ligne de matériau
if st.button("Ajouter un matériau"):
    add_row()

# Bouton pour calculer l'empreinte carbone
if st.button("Calculer le CO utilisé"):
    total_footprint = 0.0
    st.write("### Récapitulatif")
    # Parcours de chaque ligne pour le calcul
    for i in range(st.session_state['rows']):
        material = st.session_state.get(f"material_{i}", None)
        quantity = st.session_state.get(f"quantity_{i}", 0.0)
        if material and material in carbon_factors:
            footprint = quantity * carbon_factors[material]
            total_footprint += footprint
            st.write(f"**Matériau {i+1}** : {material} — Quantité : {quantity} — Empreinte carbone : {footprint:.2f} kg CO₂")
        else:
            st.write(f"**Matériau {i+1}** : Non renseigné ou matériau inconnu.")
    st.markdown(f"### Empreinte carbone totale : **{total_footprint:.2f} kg CO₂**")
    
    if superficie > 0:
        co2_par_m2 = total_footprint / superficie
        st.markdown(f"### Empreinte carbone par m² : **{co2_par_m2:.2f} kg CO₂/m²**")
    else:
        st.warning("Superficie non renseignée ou nulle, impossible de calculer l'empreinte carbone par m².")

# Bouton pour exporter les résultats dans un PDF
if st.button("Exporter les résultats en PDF"):
    total_footprint = 0.0
    # Création d'un document PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Titre
    pdf.cell(0, 10, txt="Devis Matériaux : Calcul de l'Empreinte Carbone", ln=1, align="C")
    pdf.ln(5)
    
    # Détails pour chaque matériau
    for i in range(st.session_state['rows']):
        material = st.session_state.get(f"material_{i}", None)
        quantity = st.session_state.get(f"quantity_{i}", 0.0)
        if material and material in carbon_factors:
            footprint = quantity * carbon_factors[material]
            total_footprint += footprint
            line = f"Matériau {i+1} : {material} | Quantité : {quantity} | Empreinte : {footprint:.2f} kg CO₂"
        else:
            line = f"Matériau {i+1} : Non renseigné ou matériau inconnu."
        pdf.multi_cell(0, 10, txt=line)
    
    pdf.ln(5)
    pdf.cell(0, 10, txt=f"Empreinte carbone totale : {total_footprint:.2f} kg CO₂", ln=1)
    pdf.cell(0, 10, txt=f"Superficie : {superficie:.2f} m²", ln=1)
    
    if superficie > 0:
        co2_par_m2 = total_footprint / superficie
        pdf.cell(0, 10, txt=f"Empreinte carbone par m² : {co2_par_m2:.2f} kg CO₂/m²", ln=1)
    else:
        pdf.cell(0, 10, txt="Superficie non renseignée ou nulle, calcul de l'empreinte par m² impossible.", ln=1)
    
    # Génération du PDF en mémoire
    pdf_data = pdf.output(dest="S").encode("utf-8")
    
    st.download_button("Télécharger le PDF", data=pdf_data, file_name="devis_carbone.pdf", mime="application/pdf")
