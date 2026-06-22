import sys
import traceback

from shared import ConversationManager


def main():
    manager = ConversationManager()
    session_id = manager.create_session_id()

    try:
        while True:
            user_input = input("User: ")
            command = user_input.strip().lower()
            if command == "exit":
                break
            if command == "dump":
                dump_path = manager.dump_session(session_id)
                print(f"Session dump written to: {dump_path}")
                break

            response = manager.run_turn(user_input, session_id)

            print(f"Assistant: {response.get('message', response)}")

            if response.get("end_conversation") is True:
                manager.reset(session_id)
                session_id = manager.create_session_id()
                print("Conversation state reset. Starting a new conversation...")
    except Exception as exc:
        dump_path = manager.dump_session(session_id, error={
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        })
        print(f"Error: {exc}")
        print(f"Session dump written to: {dump_path}")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
