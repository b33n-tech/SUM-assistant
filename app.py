import streamlit as st
import pandas as pd
import ollama
import textwrap

st.title("📥 Analyse de projets entrants (Ollama + llama3.2)")

# --- Upload du fichier ---
uploaded_file = st.file_uploader("Téléversez un fichier .xlsx contenant les projets", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.fillna("", inplace=True)

    # --- Sélection du projet à analyser ---
    nom_projet = st.selectbox("Sélectionnez un projet à analyser :", df["Nom du projet"].unique())
    projet = df[df["Nom du projet"] == nom_projet].iloc[0]

    # --- Prompt structuré pour l'analyse par LLM ---
    prompt = f"""
Tu es un expert en incubation, stratégie early-stage et évaluation de projets innovants. Tu vas analyser une fiche de projet transmise par un porteur. Rédige une analyse experte en 4 parties distinctes, claire, concise, mais rigoureuse.

---

📌 **1. Analyse critique structurée (forces/faiblesses/leviers)**
Analyse les forces clés du projet (problématique, solution, différenciation, équipe, etc.), les faiblesses potentielles (marché, focus, modèle économique, etc.), et les leviers ou opportunités visibles.

---

🔍 **2. Analyse approfondie par composante**
Évalue les aspects suivants :
- Marché et segments : clarté, accessibilité, maturité
- Problématique et solution : pertinence, nouveauté, adéquation
- Modèle économique et stratégie : viabilité, réalisme, scalabilité
- Maturité : état d'avancement, documents existants, prévisionnel
- Ressources humaines : équipe, implication, compétences
- Écosystème : intégration, soutiens, partenariats

---

📊 **3. Scoring d’impact potentiel**
Attribue un score sur 10 (ou en niveaux : faible / modéré / fort) pour :
- Impact sociétal ou environnemental
- Potentiel économique (création de valeur)
- Potentiel d’innovation
- Capacité à réussir un accompagnement structurant

---

⚠️ **4. Risques, fragilités, zones d'ombre**
Identifie les points de vigilance, risques implicites, incohérences, ou manques d’informations dans la fiche. Mentionne ce qui mériterait d’être clarifié ou investigué lors d’un premier échange.

---

📄 **Fiche projet à analyser :**

- Nom : {projet['Nom du projet']}
- Pitch : {projet['Votre projet en 1 phrase']}
- Description : {projet['Description du projet']}
- Avancement : {projet["État d'avancement (idée, prototype, ...)"]}
- Modèle économique : {projet['Modèle économique & stratégie']}
- Marchés : {projet['Marché(s) d\'application(s)']}
- Problématiques : {projet['Problématiques adressées']}
- Segments clients : {projet['Segments clients']}
- Concurrents ou alternatives : {projet['Solutions existantes/alternatives']}
- Différenciation : {projet['Atouts différenciants']}
- Besoins d'accompagnement : {projet["Besoins d'accompagnement identifiés"]}
- Situation professionnelle du porteur : {projet["Situation professionnelle"]}
- Implantation Grand Est : {projet["Projet implanté en Région Grand Est ?"]}
"""

    # --- Affichage résumé de la fiche projet ---
    st.subheader("🗂️ Fiche projet résumée")
    resume_df = pd.DataFrame({
        "Clé": ["Pitch", "Marché", "Modèle éco", "Clients", "État d’avancement"],
        "Valeur": [
            projet['Votre projet en 1 phrase'],
            projet['Marché(s) d\'application(s)'],
            projet['Modèle économique & stratégie'],
            projet['Segments clients'],
            projet["État d'avancement (idée, prototype, ...)"]
        ]
    })
    st.dataframe(resume_df, use_container_width=True)

    # --- Bouton de génération via llama3 ---
    st.subheader("🔍 Analyse générée par llama3.2")
    if st.button("Lancer l'analyse du projet avec Ollama"):
        with st.spinner("Analyse en cours..."):
            result = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
            reponse = result["message"]["content"]
            st.markdown(reponse)

            # --- Extraction des scores si présents ---
            import re
            score_regex = re.findall(r"([A-Za-zéàùèêç ]+)\s*[:\-–]\s*(\d{1,2})/10", reponse)
            if score_regex:
                st.subheader("📊 Scoring d’impact potentiel")
                for titre, score in score_regex:
                    st.metric(titre.strip(), f"{score}/10")

    # --- Footer ---
    st.markdown("---")
    st.caption("💡 Analyse automatique préliminaire — à confronter avec un échange réel avec le porteur.")

else:
    st.info("Veuillez importer un fichier Excel (.xlsx) contenant les projets pour commencer.")
