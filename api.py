# api.py
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from googlesearch import search

# 1. Initialize the Flask app
app = Flask(__name__)

# 2. This is the new, updated information-fetching function
def get_trans_info(query: str) -> str:
    """
    Fetches information using public libraries.
    """
    gendersyphoria_fyi_url = "https://genderdysphoria.fyi/"
    mayoclinic_query = f"site:mayoclinic.org transgender {query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # --- Part 1: Browse genderdysphoria.fyi with requests and BeautifulSoup ---
    gendersyphoria_fyi_results = ""
    try:
        response = requests.get(gendersyphoria_fyi_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all paragraphs, check if the query is in them (case-insensitive)
        matching_paragraphs = [p.get_text() for p in soup.find_all('p') if query.lower() in p.get_text().lower()]
        
        # Join the first 3 matching paragraphs for a concise result
        if matching_paragraphs:
            gendersyphoria_fyi_results = "\n\n".join(matching_paragraphs[:3])
        else:
            gendersyphoria_fyi_results = "No specific information found for that query on the page."

    except Exception as e:
        gendersyphoria_fyi_results = f"Could not retrieve information from genderdysphoria.fyi: {e}"

    # --- Part 2: Search Mayo Clinic with googlesearch-python ---
    mayoclinic_info = ""
    try:
        # Get the top 3 search results
        search_results = list(search(mayoclinic_query, num_results=3))
        if search_results:
            mayoclinic_info = "Here are the top results from mayoclinic.org:\n"
            for url in search_results:
                mayoclinic_info += f"- {url}\n"
        else:
            mayoclinic_info = "No relevant information found on mayoclinic.org."
    except Exception as e:
        mayoclinic_info = f"Could not retrieve information from mayoclinic.org: {e}"

    # --- Part 3: Format the output ---
    output = f"## Information on: {query}\n\n"
    output += f"### From genderdysphoria.fyi:\n{gendersyphoria_fyi_results}\n\n"
    output += f"### From Mayo Clinic:\n{mayoclinic_info}"
    
    return output

# 3. Define the API endpoint (this part remains the same)
@app.route('/api/info', methods=['GET'])
def api_info():
    if 'query' in request.args:
        query = request.args['query']
    else:
        return jsonify({"error": "No query parameter provided."}), 400

    results = get_trans_info(query)
    return jsonify({"query": query, "data": results})

# 4. Run the app (this part remains the same)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
