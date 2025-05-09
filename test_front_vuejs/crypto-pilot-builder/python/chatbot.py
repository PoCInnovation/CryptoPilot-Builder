import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python chatbot.py 'message'")
        return

    message = sys.argv[1]
    print(f"Réponse Python : {message[::-1]}")

if __name__ == "__main__":
    main()