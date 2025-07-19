from data_creator_agent import Agent, ArchitectureEventType


class TrainingDataFormatterAgent(Agent):
    def __init__(self, name="TrainingDataFormatterAgent", message_bus=None, config=None):
        super().__init__(name=name, message_bus=message_bus, config=config)
        if self.message_bus:
            self.message_bus.subscribe(
                ArchitectureEventType.ANALYZED_CODE_STRUCTURE, self)
            self.message_bus.subscribe(
                ArchitectureEventType.ANALYZED_DOCUMENTATION, self)

    async def handle_message(self, msg):
        if msg.get("type") == ArchitectureEventType.ANALYZED_CODE_STRUCTURE:
            print(
                f"{self.name}: Received analyzed code structure for '{msg.get('source_file')}'. Formatting training data...")

            try:
                for training_pair in self.format_code_training_data(msg.get('analysis')):
                    # Publish the structured analysis for this single file
                    self.send({
                        "type": ArchitectureEventType.TRAINING_PAIR_GENERATED,
                        "training_pair": training_pair
                    })
            except Exception as e:
                print(f"Error analyzing {msg.get('source_file')}: {e}")
        elif msg.get("type") == ArchitectureEventType.ANALYZED_DOCUMENTATION:
            print(
                f"{self.name}: Received analyzed documentation for '{msg.get('source_file')}'. Formatting training data...")

            try:
                for training_pair in self.format_doc_training_data(msg.get('analysis')):
                    # Publish the structured analysis for this single file
                    self.send({
                        "type": ArchitectureEventType.TRAINING_PAIR_GENERATED,
                        "training_pair": training_pair
                    })
            except Exception as e:
                print(f"Error analyzing {msg.get('source_file')}: {e}")

    def format_code_training_data(self, analysis):
        """Formats code analysis into training data."""
        training_pairs = []
        for function in analysis.get('functions', []):
            if function.get('docstring'):
                training_pairs.append({
                    "instruction": f"Write a Python function that does the following: {function.get('docstring')}",
                    "response": f"def {function.get('name')}({', '.join(function.get('args'))}):\n    ..."
                })
        for class_def in analysis.get('classes', []):
            if class_def.get('docstring'):
                training_pairs.append({
                    "instruction": f"Write a Python class that does the following: {class_def.get('docstring')}",
                    "response": f"class {class_def.get('name')}:\n    ..."
                })
        return training_pairs

    def format_doc_training_data(self, analysis):
        """Formats documentation analysis into training data."""
        training_pairs = []
        if analysis.get('summary'):
            training_pairs.append({
                "instruction": "Summarize the following text:",
                "response": analysis.get('summary')
            })
        for section, content in analysis.get('sections', {}).items():
            training_pairs.append({
                "instruction": f"What is the '{section}' section about?",
                "response": content
            })
        return training_pairs
