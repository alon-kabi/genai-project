import sys
import traceback

from shared import ConversationManager


def main():
    manager = ConversationManager()

    try:
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

            if response.get("end_conversation") is True:
                manager.reset()
                print("Conversation state reset. Starting a new conversation...")
    except Exception as exc:
        dump_path = manager.dump_session(error={
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        })
        print(f"Error: {exc}")
        print(f"Session dump written to: {dump_path}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
