from shared import ConversationManager

def main():
    manager = ConversationManager()

    # Conversation loop
    while True:
        user_input = input("User: ")

        response = manager.run_turn(user_input)

        print(f"Assistant: {response}")

        # Exit handling
        if (response.get("end_conversation") is True):
            break


if __name__ == "__main__":
    main()