class InfoAdvisor:
    def process(self):
        """
        Processes the complete chat history.
        Decides whether information retrieval is needed.
        """

        if self.is_info_needed():
            info = self.vector_retrieve()
            return self.send_output(info)

        return self.send_output("Info not needed")

    def is_info_needed(self):
        """
        Decide if external info retrieval is required.
        """
        # TODO: Implement logic
        pass

    def vector_retrieve(self):
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