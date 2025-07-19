from data_creator_agent import Agent, ArchitectureEventType


class VectorDBStorageAgent(Agent):
    def __init__(self, name="VectorDBStorageAgent", message_bus=None, config=None):
        super().__init__(name=name, message_bus=message_bus, config=config)
        if self.message_bus:
            self.message_bus.subscribe(
                ArchitectureEventType.DATA_EMBEDDING_COMPLETE, self)

    async def handle_message(self, msg):
        if msg.get("type") == ArchitectureEventType.DATA_EMBEDDING_COMPLETE:
            print(
                f"{self.name}: Received data embedding for '{msg.get('original_payload').get('source_file')}'. Storing in vector DB...")

            try:
                self.store_in_vector_db(msg)
            except Exception as e:
                print(
                    f"Error storing data in vector DB for {msg.get('original_payload').get('source_file')}: {e}")

    def store_in_vector_db(self, msg):
        """Stores the data in a vector DB."""
        # This is a placeholder and should be implemented with a proper vector DB connection
        print(
            f"Storing embedding for {msg.get('original_payload').get('source_file')} in vector DB.")
