from flask import Flask, request, render_template_string
from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from textwrap import dedent
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Test Agno + Flask</title>
</head>
<body>
    <h1>Ton Agent IA personnalisé</h1>
    <form method="POST">
        <label for="comportement">Comportement :</label><br>
        <textarea name="comportement" rows="4" cols="50">{{ comportement or '' }}</textarea><br><br>
        <label for="prompt">Prompt :</label><br>
        <textarea name="prompt" rows="4" cols="50">{{ prompt or '' }}</textarea><br><br>
        <input type="submit" value="Envoyer">
    </form>
    {% if response %}
        <h2>Réponse :</h2>
        <p>{{ response }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    comportement = ""
    prompt = ""
    if request.method == "POST":
        comportement = request.form.get("comportement")
        prompt = request.form.get("prompt")
        agent = Agent(
            model=OpenAIChat(id="gpt-4o"),
            instructions=dedent(comportement),
            markdown=True
        )
        response = agent.run(prompt).content
    return render_template_string(HTML_PAGE, response=response, comportement=comportement, prompt=prompt)
if __name__ == "__main__":
    app.run(debug=True)
