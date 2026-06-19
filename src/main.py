from shared import ConversationManager

def main():
    manager = ConversationManager()

    # Conversation loop
    while True:
        user_input = input("User: ")
        command = user_input.strip().lower()
        if command == "exit":
            break
        if command == "dump":
            dump_path = manager.dump_session()
            print(f"Session dump written to: {dump_path}")
            break

        response = manager.run_turn(user_input)

        print(f"Assistant: {response.get('message', response)}")

        # Exit handling
        if (response.get("end_conversation") is True):
            manager.reset()
            print("Conversation state reset. Starting a new conversation...")


if __name__ == "__main__":
    main()