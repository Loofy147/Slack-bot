from data_creator_agent import Agent, ArchitectureEventType


class EmbeddingAgent(Agent):
    def __init__(self, name="EmbeddingAgent", message_bus=None, config=None):
        super().__init__(name=name, message_bus=message_bus, config=config)
        if self.message_bus:
            self.message_bus.subscribe(
                ArchitectureEventType.ANALYZED_CODE_STRUCTURE, self)
            self.message_bus.subscribe(
                ArchitectureEventType.ANALYZED_DOCUMENTATION, self)

    async def handle_message(self, msg):
        if msg.get("type") in [ArchitectureEventType.ANALYZED_CODE_STRUCTURE, ArchitectureEventType.ANALYZED_DOCUMENTATION]:
            print(
                f"{self.name}: Received analyzed data for '{msg.get('source_file')}'. Generating embeddings...")

            try:
                embedding = self.generate_embedding(msg.get('analysis'))

                # Publish the structured analysis for this single file
                self.send({
                    "type": ArchitectureEventType.DATA_EMBEDDING_COMPLETE,
                    "original_payload": msg,
                    "embedding_vector": embedding
                })
            except Exception as e:
                print(f"Error analyzing {msg.get('source_file')}: {e}")

    def generate_embedding(self, analysis):
        """Generates embeddings for the given analysis."""
        # This is a placeholder and should be implemented with a proper embedding model
        return [0.1, 0.2, 0.3]
