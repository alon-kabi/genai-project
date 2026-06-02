from shared import ConversationManager

def main():
    manager = ConversationManager()

    # Conversation loop
    while True:
        user_input = input("User: ")
        if user_input.strip().lower() == "exit":
            break

        response = manager.run_turn(user_input)

        print(f"Assistant: {response.get('message', response)}")

        # Exit handling
        if (response.get("end_conversation") is True):
            manager.reset()
            print("Conversation state reset. Starting a new conversation...")


if __name__ == "__main__":
    main()