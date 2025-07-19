"""
Base class for orchestrators.
"""
import json
import logging
import os
import time
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from openai import OpenAI

logger = logging.getLogger(__name__)


class BaseOrchestrator:
    """Base class for orchestrators."""

    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        self.phases = []

    def _load_template(self, name):
        """تحميل قالب من مجلد prompts"""
        try:
            env = Environment(loader=FileSystemLoader('prompts'))
            return env.get_template(name)
        except Exception as e:
            logger.error("خطأ في تحميل القالب %s: %s", name, e)
            raise

    def call_model(self, prompt, max_retries=3):
        """استدعاء نموذج OpenAI مع إعادة المحاولة"""
        for attempt in range(max_retries):
            try:
                # قراءة system prompt
                with open('prompts/system_prompt.md', 'r', encoding='utf-8') as file:
                    system_content = file.read()

                response = self.client.chat.completions.create(
                    model=os.getenv('OPENAI_MODEL', 'gpt-4'),
                    messages=[
                        {'role': 'system', 'content': system_content},
                        {'role': 'user', 'content': prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )

                return response.choices[0].message.content

            except (IOError, json.JSONDecodeError) as e:
                logger.warning("المحاولة %s فشلت: %s", attempt + 1, e)
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + 1  # Exponential backoff
                    logger.info(
                        "انتظار %s ثانية قبل المحاولة التالية...", wait_time)
                    time.sleep(wait_time)
                if attempt == max_retries - 1:
                    logger.error(
                        "فشل في استدعاء النموذج بعد %s محاولات", max_retries)
                    return f"خطأ: لم يتمكن من الحصول على استجابة من النموذج. {str(e)}"
        return None

    def process_topic(self, topic):
        """معالجة موضوع عبر جميع المراحل"""
        logger.info("بدء معالجة الموضوع: %s", topic)

        try:
            user_template = self._load_template('user_prompt_template.md')
            user_template.render(topic=topic)
            logger.info("تم تحميل قالب المستخدم بنجاح")
        except IOError as e:
            logger.error("خطأ في تحميل قالب المستخدم: %s", e)
            return None

        outputs = {
            'metadata': {
                'topic': topic,
                'timestamp': datetime.now().isoformat(),
                'total_phases': len(self.phases)
            },
            'phases': {}
        }

        successful_phases = 0

        for phase_code, phase_name in self.phases:
            logger.info("معالجة %s: %s", phase_code, phase_name)

            try:
                task_tpl = self._load_template('task_prompt.md')
                prompt_text = task_tpl.render(
                    phase_name=f'{phase_code}: {phase_name}',
                    task_name='Main Task',
                    context=topic,
                    task_description=f'Define the main goals and requirements for {phase_name} '
                    f'given the topic: {topic}'
                )

                result = self.call_model(prompt_text)

                outputs['phases'][phase_code] = {
                    'phase': phase_name,
                    'prompt': prompt_text,
                    'response': result,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }

                successful_phases += 1
                logger.info("تم إنجاز %s بنجاح", phase_code)

            except IOError as e:
                logger.error("خطأ في معالجة %s: %s", phase_code, e)
                outputs['phases'][phase_code] = {
                    'phase': phase_name,
                    'error': str(e),
                    'status': 'failed',
                    'timestamp': datetime.now().isoformat()
                }

        outputs['metadata']['successful_phases'] = successful_phases
        outputs['metadata']['success_rate'] = f"{(successful_phases/len(self.phases)*100):.1f}%"

        return outputs
