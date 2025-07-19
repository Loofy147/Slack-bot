import ast

from data_creator_agent import Agent, ArchitectureEventType


class CodeAnalysisAgent(Agent):
    def __init__(self, name="CodeAnalysisAgent", message_bus=None, config=None):
        super().__init__(name=name, message_bus=message_bus, config=config)
        self.code_file_extensions = self.config.get(
            "code_extensions", ['.py', '.js'])
        if self.message_bus:
            # This agent listens for the raw data from the first agent
            self.message_bus.subscribe(
                ArchitectureEventType.REPO_DATA_EXTRACTED, self)

    async def handle_message(self, msg):
        if msg.get("type") == ArchitectureEventType.REPO_DATA_EXTRACTED:
            print(
                f"{self.name}: Received repository data for '{msg.get('source_repo')}'. Analyzing code files...")

            repo_name = msg.get('source_repo')
            files_data = msg.get('data', [])

            for file_info in files_data:
                file_path = file_info.get("file_path")

                # Check if the file is a code file we can parse
                if any(file_path.endswith(ext) for ext in self.code_file_extensions):
                    if file_path.endswith('.py'):  # Specific logic for Python
                        try:
                            analysis_result = self.analyze_python_code(
                                file_info['content'])

                            # Publish the structured analysis for this single file
                            self.send({
                                "type": ArchitectureEventType.ANALYZED_CODE_STRUCTURE,
                                "source_file": file_path,
                                "repo": repo_name,
                                "analysis": analysis_result
                            })
                        except Exception as e:
                            print(f"Error analyzing {file_path}: {e}")

    def analyze_python_code(self, code_content):
        """Parses Python code using AST and extracts structure."""
        tree = ast.parse(code_content)
        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })

        return {"functions": functions, "classes": classes}
