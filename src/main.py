def main():
    manager = ConversationManager()

    # Initial setup
    manager.fill_registration_form()

    # Conversation loop
    while True:
        user_input = input("User: ")

        response = manager.run_turn(user_input)

        print(f"Assistant: {response}")

        # Exit handling
        if (
            isinstance(response, dict)
            and response.get("end_conversation") is True
        ):
            break


if __name__ == "__main__":
    main()