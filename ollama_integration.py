from ollama import Client
import re
import json

def generate_question_list(prompt):
    client = Client(host='http://localhost:11434')
    response = client.generate(model="llama3:instruct", prompt=prompt)
    raw_response = response.get('response', '')
    text_match = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL)
    return text_match.strip()

def generate_full_survey_with_options(prompt):
    client = Client(host='http://localhost:11434')
    for attempt in range(3):  # 3 tentatives maximum
        try:
            response = client.generate(model="llama3:instruct", prompt=prompt)
            raw_response = response.get('response', '')
            if not raw_response:
                raise ValueError("Réponse vide reçue du modèle.")

            # Extraction du JSON entre ```json et ```
            json_match = re.search(r'```json\s*(.*?)\s*```', raw_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                json.loads(json_str)  # Vérifie la validité
                return json_str

            # Si pas de balises, tente de trouver un JSON brut
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = raw_response[json_start:json_end]
                json.loads(json_str)  # Vérifie la validité
                return json_str

            raise ValueError("Aucun JSON valide trouvé dans la réponse.")
        except Exception as e:
            if attempt < 2:
                continue  # Réessaye si ce n’est pas la dernière tentative
            return f"Échec après {attempt + 1} tentatives : {str(e)}. Réponse brute : {raw_response}"
    return "Échec inattendu : aucune réponse générée."