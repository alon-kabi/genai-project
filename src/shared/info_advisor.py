class InfoAdvisor:
    def process(self):
        """
        Processes the complete conversation.
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
        # TODO: Replace with LLM / RAG decision
        return True

    def vector_retrieve(self):
        """
        Retrieve information from vector database / RAG system.
        """
        # TODO: Implement vector retrieval (Chroma)
        return "Job info placeholder — RAG not wired yet."

    def send_output(self, result):
        """
        Sends output back to MainAgent.
        """
        return result