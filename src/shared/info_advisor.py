class InfoAdvisor:
    def process(self, chat_history):
        """
        Processes the complete chat history.
        Decides whether information retrieval is needed.
        """

        if self.is_info_needed(chat_history):
            info = self.vector_retrieve(chat_history)
            return self.send_output(info)

        return self.send_output("Info not needed")

    def is_info_needed(self, chat_history):
        """
        Decide if external info retrieval is required.
        """
        # TODO: Implement logic
        pass

    def vector_retrieve(self, chat_history):
        """
        Retrieve information from vector database / RAG system.
        """
        # TODO: Implement vector retrieval
        pass

    def send_output(self, result):
        """
        Sends output back to MainAgent.
        """
        return result