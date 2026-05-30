from .main_agent import MainAgent

class ConversationManager:
    
    def run_turn(user_input):
        """
        One turn in the conversation.
        """
        
        main_agent=MainAgent()
        response=main_agent.process_input(user_input)
        return response