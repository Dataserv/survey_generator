import streamlit as st
import json
import pandas as pd
from ollama_integration import generate_question_list, generate_full_survey_with_options
import os
import time
import threading
import io
import re
from openai import OpenAI  # Pour l'API OpenAI
import anthropic  # Pour l'API Claude

# Gestion multilingue
LANGUAGES = {"Français": "French", "English": "English", "Español": "Spanish", "العربية": "Arabic"}
DETAIL_LEVELS = {"basic": "basic", "detailed": "detailed", "very_detailed": "very detailed"}
TONES = {"formal": "formal", "friendly": "friendly", "neutral": "neutral"}

# Standards internationaux
STANDARDS = {
    "ISO 20252": "Ensure clarity, transparency, and consistency in question design.",
    "AAPOR": "Minimize bias, ensure clarity, and pretest questions for reliability.",
    "ESS": "Ensure cross-cultural comparability and rigorous pretesting.",
    "OCDE": "Focus on psychometric validity and international comparability.",
    "ESOMAR": "Respect respondent privacy and avoid intrusive questions."
}

# Chargement des traductions
translation_files = {}
for lang, code in LANGUAGES.items():
    file_path = f"translations/{code.lower()[:2]}.json"  # ex. "fr.json" pour "French"
    try:
        with open(file_path, encoding="utf-8") as f:
            translation_files[code] = json.load(f)
    except Exception as e:
        st.error(f"Error with {file_path}: {str(e)}")
        translation_files[code] = {}

# Initialisation de l’état
if "questions_raw" not in st.session_state:
    st.session_state.questions_raw = ""
if "survey" not in st.session_state:
    st.session_state.survey = {"intro": "", "questions": [], "outro": ""}
if "config_params" not in st.session_state:
    st.session_state.config_params = {}

# Interface utilisateur
interface_lang = st.sidebar.selectbox("Interface Language", list(LANGUAGES.keys()), key="interface_lang")
lang_code = LANGUAGES[interface_lang]
tr = translation_files.get(lang_code, {})
st.title(tr.get("survey_generator", "Survey Generator"))


# Choix du service AI
ai_service = st.sidebar.selectbox(
    "AI Service",
    ["Ollama (Local)", "OpenAI (ChatGPT)", "Claude (Anthropic)"],
    help="Select the AI service to generate the survey."
)

# Configuration des clés API si nécessaire
if ai_service == "OpenAI (ChatGPT)":
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key.")
    client_openai = OpenAI(api_key=openai_api_key) if openai_api_key else None

elif ai_service == "Claude (Anthropic)":
    claude_api_key = st.sidebar.text_input("Claude API Key", type="password")
    if not claude_api_key:
        st.warning("Please enter your Claude API key.")
    client_claude = anthropic.Anthropic(api_key=claude_api_key) if claude_api_key else None

# Fonction pour appeler le service AI
def call_ai_service(prompt, service):
    if service == "Ollama (Local)":
        return generate_full_survey_with_options(prompt)
    elif service == "OpenAI (ChatGPT)" and client_openai:
        response = client_openai.chat.completions.create(
            model="gpt-4",  # ou "gpt-3.5-turbo" selon votre abonnement
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    elif service == "Claude (Anthropic)" and client_claude:
        response = client_claude.messages.create(
            model="claude-3-opus-20240229",  # ou un autre modèle Claude
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    else:
        return "Error: Service not configured properly."


# Étapes avec onglets
tabs = st.tabs([
    tr.get("step1", "Step 1: Configuration"),
    tr.get("step2", "Step 2: Questions"),
    tr.get("step3", "Step 3: Editing"),
    tr.get("step4", "Step 4: Finalization")
])

# Étape 1 : Configuration
with tabs[0]:
    st.subheader(tr.get("survey_details", "Survey Details"))

    # Section 1 : Informations générales
    st.markdown(f"### {tr.get('general_info', 'General Information')}")
    entity_name = st.text_input(
        tr.get("entity_label", "Entity Name (company, institution, etc.)"),
        help="Ex: Acme Corp, Université de Paris"
    )
    if not entity_name:
        st.warning(tr.get("warning_message", "Please fill in all fields."))
    
    survey_title = st.text_input(
        tr.get("survey_title_label", "Survey Title"),
        help="Ex: Enquête de satisfaction 2025"
    )

    # Section 2 : Objectifs et contexte
    st.markdown(f"### {tr.get('objectives_context', 'Objectives and Context')}")
    survey_types = {
        tr.get("client_satisfaction", "Client Satisfaction"): "Customer satisfaction survey (e.g., NPS, CSAT)",
        tr.get("product_feedback", "Product Feedback"): "Product feedback survey",
        tr.get("market_study", "Market Study"): "Market research survey",
        tr.get("academic_survey", "Academic Survey"): "Academic research survey",
        tr.get("employee_evaluation", "Employee Evaluation"): "Employee evaluation survey",
        tr.get("custom", "Custom"): "Custom survey"
    }
    survey_type = st.selectbox(tr.get("survey_type_label", "Survey Type"), list(survey_types.keys()))
    survey_context = survey_types[survey_type]
    if survey_type == tr.get("custom", "Custom"):
        survey_context = st.text_input(tr.get("custom_survey_type", "Describe the custom survey type"), "")

    objectives_options = [
        tr.get("measure_satisfaction", "Measure Satisfaction"),
        tr.get("collect_opinions", "Collect Opinions"),
        tr.get("analyze_behaviors", "Analyze Behaviors"),
        tr.get("collect_demographics", "Collect Demographics"),
        tr.get("other", "Other")
    ]
    objectives = st.multiselect(
        tr.get("objectives_label", "Survey Objectives"),
        options=objectives_options,
        default=[tr.get("measure_satisfaction", "Measure Satisfaction")]
    )
    if tr.get("other", "Other") in objectives:
        custom_objective = st.text_input(tr.get("custom_objective", "Specify the custom objective"), "")

    sectors = [
        tr.get("technology", "Technology"),
        tr.get("health", "Health"),
        tr.get("education", "Education"),
        tr.get("commerce", "Commerce"),
        tr.get("services", "Services"),
        tr.get("other", "Other")
    ]
    sector = st.selectbox(tr.get("sector_label", "Sector of Activity"), sectors)
    if sector == tr.get("other", "Other"):
        sector = st.text_input(tr.get("custom_sector", "Specify the sector"), "")

    # Section 3 : Public cible
    st.markdown(f"### {tr.get('target_audience', 'Target Audience')}")
    target_groups_options = [
        tr.get("individual", "Individuals"),
        tr.get("business", "Businesses"),
        tr.get("students", "Students"),
        tr.get("employees", "Employees"),
        tr.get("patients", "Patients"),
        tr.get("other", "Other")
    ]
    target_groups = st.multiselect(
        tr.get("target_groups_label", "Target Groups"),
        options=target_groups_options,
        default=[tr.get("individual", "Individuals")]
    )
    if tr.get("other", "Other") in target_groups:
        custom_target = st.text_input(tr.get("custom_target", "Specify the target group"), "")

    target_size = st.slider(
        tr.get("target_size_label", "Target Sample Size"),
        min_value=10, max_value=10000, value=100, step=10
    )

    # Section 4 : Structure du questionnaire
    st.markdown(f"### {tr.get('survey_structure', 'Survey Structure')}")
    sections = st.number_input(
        tr.get("sections_label", "Number of Sections"),
        min_value=1, max_value=10, value=3
    )
    
    question_types_options = [
        tr.get("single_choice", "Single Choice"),
        tr.get("multiple_choice", "Multiple Choice"),
        tr.get("open_ended", "Open-ended"),
        tr.get("scales", "Scales (1-5)"),
        tr.get("conditional", "Conditional")
    ]
    question_types = st.multiselect(
        tr.get("question_types_label", "Desired Question Types"),
        options=question_types_options,
        default=[tr.get("single_choice", "Single Choice"), tr.get("multiple_choice", "Multiple Choice"), tr.get("open_ended", "Open-ended")]
    )
    
    detail_level_options = [tr.get("basic", "Basic"), tr.get("detailed", "Detailed"), tr.get("very_detailed", "Very Detailed")]
    detail_level = st.selectbox(
        tr.get("detail_level_label", "Detail Level"),
        detail_level_options
    )
    
    duration = st.slider(
        tr.get("duration_label", "Estimated Duration (minutes)"),
        min_value=1, max_value=60, value=10
    )

    # Section 5 : Personnalisation
    st.markdown(f"### {tr.get('customization', 'Customization')}")
    survey_lang = st.selectbox(tr.get("survey_lang_label", "Survey Language"), list(LANGUAGES.keys()))
    tone_options = [tr.get("formal", "Formal"), tr.get("friendly", "Friendly"), tr.get("neutral", "Neutral")]
    tone = st.selectbox(tr.get("tone_label", "Survey Tone"), tone_options)
    custom_instructions = st.text_area(
        tr.get("custom_instructions_label", "Specific Instructions for Generation"),
        placeholder=tr.get("custom_instructions_placeholder", "Ex: Add questions about customer loyalty.")
    )

    # Section 6 : Standards internationaux
    st.markdown(f"### {tr.get('standards_section', 'International Standards')}")
    selected_standards = st.multiselect(
        tr.get("standards_label", "Standards to Follow"),
        options=list(STANDARDS.keys()),
        default=["ISO 20252"],
        help=tr.get("standards_help", "Select one or more standards to guide the design.")
    )

    # Sauvegarde des paramètres
    if st.button(tr.get("save_config", "Save Configuration")):
        st.session_state.config_params = {
            "entity_name": entity_name,
            "survey_title": survey_title,
            "ai_service": ai_service,
            "survey_context": survey_context,
            "objectives": objectives + ([custom_objective] if tr.get("other", "Other") in objectives else []),
            "sector": sector,
            "target_groups": target_groups + ([custom_target] if tr.get("other", "Other") in target_groups else []),
            "target_size": target_size,
            "sections": sections,
            "question_types": question_types,
            "detail_level": list(DETAIL_LEVELS.keys())[detail_level_options.index(detail_level)],
            "duration": duration,
            "survey_lang": survey_lang,
            "tone": list(TONES.keys())[tone_options.index(tone)],
            "custom_instructions": custom_instructions,
            "standards": selected_standards
        }
        st.success(tr.get("success_message", "Configuration saved successfully!"))

# Étape 2 : Génération des questions
with tabs[1]:
    if not st.session_state.config_params:
        st.warning(tr.get("warning_message", "Please save the configuration in Step 1 before generating questions."))
    else:
        if st.button(tr.get("generate_questions_button", "Generate Question List")):
            params = st.session_state.config_params
            standards_instructions = "\n".join([f"- {standard}: {STANDARDS[standard]}" for standard in params["standards"]])
            question_types_translated = {
                "French": {"Choix unique": "Choix unique", "Choix multiple": "Choix multiple", "Ouvertes": "Ouvertes", "Échelles (1-5)": "Échelles (1-5)", "Conditionnelles": "Conditionnelles"},
                "English": {"Single Choice": "Single-choice", "Multiple Choice": "Multiple-choice", "Open-ended": "Open-ended", "Scales (1-5)": "Scales (1-5)", "Conditional": "Conditional"},
                "Spanish": {"Opción única": "Opción única", "Opción múltiple": "Opción múltiple", "Abiertas": "Abiertas", "Escalas (1-5)": "Escalas (1-5)", "Condicionales": "Condicionales"},
                "Arabic": {"اختيار واحد": "اختيار واحد", "اختيار متعدد": "اختيار متعدد", "مفتوحة": "مفتوحة", "مقاييس (1-5)": "مقاييس (1-5)", "مشروطة": "مشروطة"}
            }
            translated_types = [question_types_translated[params['survey_lang']].get(t, t) for t in params['question_types']]

            example = (
                "Section 1: Satisfaction\n- Comment êtes-vous satisfait ? (Ouvertes)\n- Recommanderiez-vous ? (Choix unique)\n- Si oui, pourquoi ? (Ouvertes, conditionnelle)"
                if params['survey_lang'] == 'French'
                else "Section 1: Satisfaction\n- How satisfied are you? (Open-ended)\n- Would you recommend? (Single-choice)\n- If yes, why? (Open-ended, conditional)"
            )

            prompt = f"""
            Generate a professional survey outline for '{params['entity_name']}' titled '{params['survey_title']}'.
            Context: {params['survey_context']}.
            Objectives: {', '.join(params['objectives'])}.
            Sector: {params['sector']}.
            Target audience: {', '.join(params['target_groups'])}, approximately {params['target_size']} respondents.
            Structure: {params['sections']} sections, using {', '.join(translated_types)} question types.
            Detail level: {params['detail_level']} (basic: 5-7 questions, detailed: 8-12, very detailed: 12+).
            Estimated duration: {params['duration']} minutes.
            Language: Generate all content exclusively in {params['survey_lang']}.
            Tone: {params['tone']}.
            Additional instructions: {params['custom_instructions'] if params['custom_instructions'] else 'None'}.
            Standards to follow:
            {standards_instructions}
            Include a mix of question types and conditional logic where appropriate.
            Output as plain text with sections and question types in parentheses, entirely in {params['survey_lang']}.
            Example in {params['survey_lang']}:
            {example}
            """
            with st.spinner(tr.get("generating", "Generating in progress...")):
                result = [None]
                def run_generation():
                    try:
                        result[0] = generate_question_list(prompt)
                    except Exception as e:
                        result[0] = f"Error generating: {str(e)}"
                thread = threading.Thread(target=run_generation)
                thread.start()
                thread.join()
                if result[0] and "Error" not in result[0]:
                    st.session_state.questions_raw = result[0]
                    st.success(tr.get("success_message", "Questions generated successfully!"))
                else:
                    st.error(result[0] or tr.get("error_message", "Error: No response received from the model."))

        if st.session_state.questions_raw:
            st.text_area(tr.get("questions_list", "Question List (editable)"), st.session_state.questions_raw, height=200)

# Étape 3 : Édition des questions
with tabs[2]:
    st.subheader(tr.get("edit_questions", "Edit Questions"))
    if not st.session_state.questions_raw:
        st.info(tr.get("info_generate_questions", "Generate questions in Step 2 first."))
    else:
        questions_text = st.text_area(
            tr.get("questions_list", "Question List (editable)"),
            value=st.session_state.questions_raw,
            height=300
        )
        if st.button(tr.get("save_edits", "Save Edits")):
            st.session_state.questions_raw = questions_text
            st.success(tr.get("success_message", "Edits saved successfully!"))

# Étape 4 : Finalisation et exportation
with tabs[3]:
    if not st.session_state.config_params or not st.session_state.questions_raw:
        st.warning(tr.get("warning_complete_steps", "Please complete the previous steps (configuration and question generation)."))
    else:
        if st.button(tr.get("generate_full_survey_button", "Generate Full Survey")):
            params = st.session_state.config_params
            standards_instructions = "\n".join([f"- {standard}: {STANDARDS[standard]}" for standard in params["standards"]])
            prompt = f"""
            Create a complete, professional survey from this outline:
            {st.session_state.questions_raw}
            Context: {params['survey_context']}.
            Objectives: {', '.join(params['objectives'])}.
            Sector: {params['sector']}.
            Target audience: {', '.join(params['target_groups'])}, approximately {params['target_size']} respondents.
            Structure: {params['sections']} sections, using {', '.join(params['question_types'])} question types.
            Detail level: {params['detail_level']}.
            Estimated duration: {params['duration']} minutes.
            Language: Generate all content exclusively in {params['survey_lang']}.
            Tone: {params['tone']}.
            Additional instructions: {params['custom_instructions'] if params['custom_instructions'] else 'None'}.
            Standards to follow:
            {standards_instructions}
            Output as a JSON object with 'intro', 'questions', and 'outro', entirely in {params['survey_lang']}.
            For each question: include 'type', 'text', 'options' (set to null for open-ended questions), and 'condition' (e.g., "If Q2 = Yes" for question 2).
            Multiple-choice: 4+ relevant options. Single-choice: scale (e.g., 1-5, Yes/No).
            Wrap in ```json and ``` markers.
            Example in {params['survey_lang']}:
            ```json
            {{
                "intro": {"Merci de participer..." if params['survey_lang'] == 'French' else "Thank you for participating..."},
                "questions": [
                    {{"type": {"Choix unique" if params['survey_lang'] == 'French' else "Single-choice"}, "text": {"Recommanderiez-vous notre service ?" if params['survey_lang'] == 'French' else "Would you recommend our service?"}, "options": ["Oui", "Non"], "condition": null}},
                    {{"type": {"Ouvertes" if params['survey_lang'] == 'French' else "Open-ended"}, "text": {"Si oui, pourquoi ?" if params['survey_lang'] == 'French' else "If yes, why?"}, "options": null, "condition": "If Q1 = Oui"}}
                ],
                "outro": {"Merci !" if params['survey_lang'] == 'French' else "Thank you!"}
            }}
            """
            with st.spinner(tr.get("generating", "Generating in progress...")):
                result = [None]
                def run_generation(prompt=prompt):
                    try:
                        result[0] = call_ai_service(prompt, params["ai_service"])
                    except Exception as e:
                        result[0] = f"Error generating: {str(e)}"
                thread = threading.Thread(target=run_generation)
                thread.start()
                thread.join()
                if result[0] is None:
                    st.error(tr.get("error_message", "Error: No response received from the model."))
                elif isinstance(result[0], str) and "Error" in result[0]:
                    st.error(result[0])
                else:
                    try:
                        survey_data = json.loads(result[0])
                        st.session_state.survey = survey_data
                        st.success(tr.get("success_message", "Survey generated successfully!"))
                    except json.JSONDecodeError as e:
                        st.error(f"{tr.get('json_error', 'JSON parsing error')}: {str(e)}. Response: {result[0]}")
                    except Exception as e:
                        st.error(f"{tr.get('unexpected_error', 'Unexpected error')}: {str(e)}. Response: {result[0]}")


            def check_consistency(survey):
                issues = []
                if not survey.get("questions") or not isinstance(survey["questions"], (list, tuple)):
                    issues.append(tr.get("no_questions", "No valid questions found in survey"))
                    return issues

                for i, q in enumerate(survey["questions"]):
                    q_num = f"Q{i+1}"
                    
                    # Vérification des champs obligatoires
                    if not q.get("text") or not q.get("type"):
                        issues.append(f"{q_num}: {tr.get('missing_field', 'Missing required field (text or type)')} - {q}")
                        continue

                    # Vérification des options selon le type
                    q_type = q.get("type", "").lower()
                    options = q.get("options")
                    if "choice" in q_type and (options is None or not isinstance(options, (list, tuple)) or not options):
                        issues.append(f"{q_num}: {tr.get('missing_options', 'Choice question requires options')} - {q}")
                        continue
                    if "open" in q_type and options is not None:
                        issues.append(f"{q_num}: {tr.get('unexpected_options', 'Open-ended question should not have options')} - {q}")
                        continue

                    # Vérification des conditions
                    condition = q.get("condition")
                    if condition:
                        try:
                            if isinstance(condition, str):
                                # Condition sous forme de chaîne : "If Q5 = Yes"
                                cond_parts = condition.split(" = ")
                                if len(cond_parts) != 2:
                                    issues.append(f"{q_num}: {tr.get('invalid_condition_format', 'Invalid condition format')} ({condition})")
                                    continue
                                cond_q, cond_val = cond_parts
                            elif isinstance(condition, dict):
                                # Condition sous forme de dictionnaire : {"question": "Q5", "value": "Yes"}
                                cond_q = condition.get("question", "")
                                cond_val = condition.get("value", "")
                                if not cond_q or not cond_val:
                                    issues.append(f"{q_num}: {tr.get('invalid_condition_dict', 'Invalid condition dictionary')} ({condition})")
                                    continue
                            else:
                                issues.append(f"{q_num}: {tr.get('unsupported_condition_type', 'Unsupported condition type')} ({condition})")
                                continue

                            # Extraire l'index de la question référencée
                            cond_q_clean = cond_q.replace("If Q", "").strip()
                            try:
                                cond_idx = int(cond_q_clean) - 1  # Convertir en index 0-based
                            except ValueError:
                                issues.append(f"{q_num}: {tr.get('invalid_question_ref', 'Invalid question reference')} ({cond_q})")
                                continue

                            # Vérifier si l'index est valide
                            if cond_idx < 0 or cond_idx >= len(survey["questions"]):
                                issues.append(f"{q_num}: {tr.get('out_of_bounds', 'Condition references out-of-bounds question')} ({cond_q})")
                                continue

                            # Vérifier les options de la question référencée
                            ref_q = survey["questions"][cond_idx]
                            ref_options = ref_q.get("options", [])
                            if ref_options is None:
                                ref_options = []

                            # Normaliser les options pour la comparaison
                            ref_option_values = []
                            for opt in ref_options:
                                if isinstance(opt, (int, str)):
                                    ref_option_values.append(str(opt).strip().lower())
                                elif isinstance(opt, dict):
                                    ref_option_values.append(str(opt.get("value", opt)).strip().lower())
                                else:
                                    issues.append(f"Q{cond_idx+1}: {tr.get('invalid_option_format', 'Invalid option format')} ({opt})")

                            # Nettoyer la valeur de la condition
                            cond_val_cleaned = str(cond_val).strip("'\"").lower()

                            # Vérifier si la valeur est dans les options
                            if not ref_option_values:
                                issues.append(f"{q_num}: {tr.get('no_options_ref', 'Referenced question has no options')} (Q{cond_idx+1})")
                            elif cond_val_cleaned not in ref_option_values:
                                issues.append(f"{q_num}: {tr.get('invalid_condition_value', 'Invalid condition value')} ({condition}) - '{cond_val}' not in Q{cond_idx+1} options: {ref_option_values}")
                        except Exception as e:
                            issues.append(f"{q_num}: {tr.get('condition_error', 'Error processing condition')} ({condition}) - {str(e)}")

                return issues


            if st.session_state.survey.get("questions"):
                        issues = check_consistency(st.session_state.survey)
                        if issues:
                            st.warning(f"{tr.get('issues_detected', 'Issues detected')}:\n" + "\n".join(issues))

                        st.subheader(tr.get("generated_survey", "Generated Survey"))
                        st.write(f"{tr.get('introduction', 'Introduction')}: {st.session_state.survey['intro']}")
                        for i, q in enumerate(st.session_state.survey["questions"]):
                            condition = f" ({tr.get('condition', 'Condition')}: {q['condition']})" if q.get("condition") else ""
                            st.write(f"{i+1}. {q['text']} ({q['type']}{condition})")
                            if q.get("options"):
                                options = q.get("options")
                                if options and isinstance(options[0], dict):
                                    option_texts = [opt.get("value", str(opt)) for opt in options]
                                else:
                                    option_texts = options or []
                                st.write(f"{tr.get('options', 'Options')}: " + ", ".join(str(opt) for opt in option_texts))
                            # Débogage des conditions
                            if q.get("condition"):
                                try:
                                    if isinstance(q["condition"], str):
                                        cond_parts = q["condition"].split(" = ")
                                        if len(cond_parts) == 2:
                                            cond_q = cond_parts[0].replace("If Q", "").strip()
                                            cond_idx = int(cond_q) - 1
                                            if 0 <= cond_idx < len(st.session_state.survey["questions"]):
                                                ref_q = st.session_state.survey["questions"][cond_idx]
                                                st.write(f"-> Référence à Q{cond_idx+1} options: {ref_q.get('options', 'Aucune')}")
                                except (ValueError, IndexError):
                                    st.write(f"-> Erreur dans la condition : {q['condition']}")
                        st.write(f"{tr.get('conclusion', 'Conclusion')}: {st.session_state.survey['outro']}")

                        # Exportation améliorée
                        export_format = st.selectbox(tr.get("export_label", "Export Format"), ["JSON", "Excel", "CSV"])
                        if export_format == "JSON":
                            st.json(st.session_state.survey)
                        else:
                            df = pd.DataFrame(st.session_state.survey["questions"])
                            st.dataframe(df)

                        if st.button(tr.get("export_button", "Export")):
                            try:
                                if export_format == "JSON":
                                    json_str = json.dumps(st.session_state.survey, ensure_ascii=False, indent=2)
                                    json_bytes = json_str.encode('utf-8')
                                    st.download_button(
                                        label=tr.get("download", "Download"),
                                        data=json_bytes,
                                        file_name="survey.json",
                                        mime="application/json"
                                    )
                                elif export_format == "Excel":
                                    output = io.BytesIO()
                                    df = pd.DataFrame(st.session_state.survey["questions"])
                                    df.to_excel(output, index=False, engine='openpyxl')
                                    output.seek(0)
                                    st.download_button(
                                        label=tr.get("download", "Download"),
                                        data=output,
                                        file_name="survey.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                                elif export_format == "CSV":
                                    output = io.StringIO()
                                    df = pd.DataFrame(st.session_state.survey["questions"])
                                    df.to_csv(output, index=False)
                                    csv_bytes = output.getvalue().encode('utf-8')
                                    output.close()
                                    st.download_button(
                                        label=tr.get("download", "Download"),
                                        data=csv_bytes,
                                        file_name="survey.csv",
                                        mime="text/csv"
                                    )
                                st.success(tr.get("export_success", "File ready for download!"))
                            except Exception as e:
                                st.error(f"{tr.get('export_error', 'Export failed')}: {str(e)}")
