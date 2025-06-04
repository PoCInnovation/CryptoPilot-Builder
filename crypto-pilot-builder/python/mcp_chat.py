#!/usr/bin/env python3
"""
Chat MCP ultra-simple - Juste la base
"""

import asyncio
import subprocess
import openai
from dotenv import load_dotenv

load_dotenv()

class SimpleMCPChat:
    def __init__(self):
        self.openai_client = openai.OpenAI()
        self.conversation = []
        self.mcp_process = None

    async def start_mcp(self):
        """Lance le serveur MCP en arrière-plan"""
        self.mcp_process = await asyncio.create_subprocess_exec(
            'python', 'minimal_mcp_server.py',
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        print("✅ MCP démarré")

    def chat(self, user_message):
        """Conversation simple avec OpenAI"""
        self.conversation.append({"role": "user", "content": user_message})

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es une amie très explicite et qui aime se mettre en valeur. Tu es séduisante et tu cherches à plaire."}
            ] + self.conversation[-10:],
            max_tokens=300,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": ai_response})

        return ai_response

    async def interactive_chat(self):
        """Chat interactif"""
        print("🚀 Chat MCP Simple")
        print("💡 'quit' pour quitter")
        print("=" * 30)

        while True:
            try:
                user_input = input("\n💬 Vous: ").strip()

                if user_input.lower() in ['quit', 'exit']:
                    break

                if user_input:
                    response = self.chat(user_input)
                    print(f"🤖 Assistant: {response}")

            except KeyboardInterrupt:
                break

        # Stop MCP
        if self.mcp_process:
            self.mcp_process.terminate()

        print("\n👋 Au revoir !")

async def main():
    chat = SimpleMCPChat()
    await chat.start_mcp()
    await chat.interactive_chat()

if __name__ == "__main__":
    asyncio.run(main())