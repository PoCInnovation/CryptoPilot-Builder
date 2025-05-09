from flask import Flask, request, render_template_string
from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from textwrap import dedent
from dotenv import load_dotenv
from agno.tools.duckduckgo import DuckDuckGoTools
from tools.test_tool import get_crypto_price

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

# @app.route("/", methods=["GET", "POST"])
def home():
    response = None
    comportement = """
You are an enthusiastic news reporter with a flair for storytelling and passionate about cryptocurrency.

When using get_crypto_price to fetch cryptocurrency prices:
1. The tool accepts two parameters: crypto_id (like 'bitcoin', 'ethereum') and currency (like 'eur', 'usd', 'gbp')
2. If the tool returns valid price data, use that exact price in your response.
3. If the tool reports an error (like rate limiting), acknowledge the issue and provide general information
   about the cryptocurrency instead, clearly stating that it's not real-time data.

Be transparent with users about any data limitations while maintaining your enthusiastic reporting style.
"""
    prompt = "Tell me the current price of Bitcoin in USD and Ethereum in GBP."
    agent = Agent(
        model=OpenAIChat(id="gpt-4"),
        instructions=dedent(comportement),
        markdown=True,
        tools=[get_crypto_price]
    )

    # Exécution de l'agent avec le prompt
    agent.print_response(prompt, stream=True)

if __name__ == "__main__":
    home()
