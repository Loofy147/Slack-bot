from typing import Any, Dict

class PromptManager:
    async def get_template(self, template_id: str) -> Any:
        # This is a placeholder. In a real implementation, this method
        # would retrieve a prompt template from a file or database.
        return "This is a test template for {input}"

    async def format_prompt(self, template_id: str, data: Dict[str, Any]) -> str:
        # This is a placeholder. In a real implementation, this method
        # would format the prompt with the given data.
        template = await self.get_template(template_id)
        return template.format(**data)
