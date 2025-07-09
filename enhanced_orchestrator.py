"""
محرك التنسيق المحسن مع قدرات التكامل المباشر
"""
import os
import json
import logging
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
import argparse
from datetime import datetime
from dotenv import load_dotenv
import time
from system_integrator import SystemIntegrator
from config import Config

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_orchestrator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedOrchestrator:
    """محرك التنسيق المحسن مع التكامل المباشر"""
    
    def __init__(self):
        self.config = Config()
        self.system_integrator = SystemIntegrator(self.config)
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        
        # المراحل مع قدرات التكامل
        self.phases = [
            ('Phase 0', 'Ideation', True),
            ('Phase 1', 'Research', True),
            ('Phase 2', 'Design', True),
            ('Phase 3', 'Development Plan', True),
            ('Phase 4', 'Execution', True),  # مرحلة التنفيذ المباشر
            ('Phase 5', 'Review & Optimize', True),
            ('Phase 6', 'Deploy & Integrate', True)  # مرحلة جديدة للنشر والتكامل
        ]
    
    def call_model_with_integration(self, prompt: str, enable_integration: bool = False, max_retries: int = 3):
        """استدعاء النموذج مع إمكانية التكامل المباشر"""
        
        # إضافة تعليمات التكامل للنموذج
        if enable_integration:
            integration_prompt = self._get_integration_prompt()
            prompt = f"{prompt}\n\n{integration_prompt}"
        
        for attempt in range(max_retries):
            try:
                # قراءة system prompt المحسن
                with open('prompts/enhanced_system_prompt.md', 'r', encoding='utf-8') as f:
                    system_content = f.read()
                
                response = self.client.chat.completions.create(
                    model=self.config.OPENAI_MODEL,
                    messages=[
                        {'role': 'system', 'content': system_content},
                        {'role': 'user', 'content': prompt}
                    ],
                    max_tokens=self.config.OPENAI_MAX_TOKENS,
                    temperature=self.config.OPENAI_TEMPERATURE
                )
                
                response_content = response.choices[0].message.content
                
                # معالجة طلبات التكامل إذا كانت مفعلة
                if enable_integration:
                    response_content = self._process_integration_requests(response_content)
                
                return response_content
                
            except Exception as e:
                logger.warning(f"المحاولة {attempt + 1} فشلت: {e}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + 1
                    logger.info(f"انتظار {wait_time} ثانية قبل المحاولة التالية...")
                    time.sleep(wait_time)
                if attempt == max_retries - 1:
                    logger.error(f"فشل في استدعاء النموذج بعد {max_retries} محاولات")
                    return f"خطأ: لم يتمكن من الحصول على استجابة من النموذج. {str(e)}"
    
    def _get_integration_prompt(self) -> str:
        """الحصول على تعليمات التكامل للنموذج"""
        return """
## قدرات التكامل المباشر المتاحة:

يمكنك الآن طلب تنفيذ عمليات مباشرة في النظام باستخدام التنسيق التالي:

```json
{
  "integration_request": {
    "type": "نوع_العملية",
    "parameters": {
      "المعاملات": "القيم"
    }
  }
}
```

### أنواع العمليات المتاحة:

1. **file_system**: إنشاء، تعديل، حذف الملفات والمجلدات
2. **git_operations**: عمليات Git (commit, push, branch)
3. **package_management**: تثبيت وإدارة الحزم
4. **database_operations**: عمليات قاعدة البيانات
5. **api_calls**: استدعاءات API خارجية
6. **deployment**: نشر التطبيقات
7. **system_commands**: تنفيذ أوامر النظام
8. **environment_variables**: إدارة متغيرات البيئة

### أمثلة:

```json
{
  "integration_request": {
    "type": "file_system",
    "parameters": {
      "operation": "create_file",
      "path": "new_feature.py",
      "content": "# كود الميزة الجديدة"
    }
  }
}
```

```json
{
  "integration_request": {
    "type": "package_management",
    "parameters": {
      "operation": "install",
      "package": "requests"
    }
  }
}
```

استخدم هذه القدرات عندما تحتاج لتنفيذ تغييرات فعلية في النظام.
"""
    
    def _process_integration_requests(self, response_content: str) -> str:
        """معالجة طلبات التكامل في الاستجابة"""
        lines = response_content.split('\n')
        processed_lines = []
        integration_results = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # البحث عن طلبات التكامل
            if '```json' in line and i + 1 < len(lines):
                json_content = ""
                i += 1
                
                # جمع محتوى JSON
                while i < len(lines) and '```' not in lines[i]:
                    json_content += lines[i] + '\n'
                    i += 1
                
                # محاولة معالجة طلب التكامل
                try:
                    request_data = json.loads(json_content.strip())
                    if 'integration_request' in request_data:
                        result = self._execute_integration_request(request_data['integration_request'])
                        integration_results.append(result)
                        
                        # إضافة نتيجة التنفيذ للاستجابة
                        processed_lines.append(f"✅ **تم تنفيذ العملية:** {result['message'] if result['success'] else result['error']}")
                    else:
                        processed_lines.append('```json')
                        processed_lines.append(json_content.strip())
                        processed_lines.append('```')
                except json.JSONDecodeError:
                    processed_lines.append('```json')
                    processed_lines.append(json_content.strip())
                    processed_lines.append('```')
                except Exception as e:
                    processed_lines.append(f"❌ **خطأ في التنفيذ:** {str(e)}")
            else:
                processed_lines.append(line)
            
            i += 1
        
        # إضافة ملخص العمليات المنفذة
        if integration_results:
            processed_lines.append("\n## ملخص العمليات المنفذة:")
            for i, result in enumerate(integration_results, 1):
                status = "✅" if result['success'] else "❌"
                processed_lines.append(f"{i}. {status} {result.get('message', result.get('error', 'عملية غير محددة'))}")
        
        return '\n'.join(processed_lines)
    
    def _execute_integration_request(self, request: dict) -> dict:
        """تنفيذ طلب التكامل"""
        request_type = request.get('type')
        parameters = request.get('parameters', {})
        
        logger.info(f"تنفيذ طلب تكامل: {request_type}")
        
        return self.system_integrator.execute_ai_request(request_type, parameters)
    
    def process_topic_enhanced(self, topic: str, enable_integration: bool = False):
        """معالجة موضوع مع التكامل المحسن"""
        logger.info(f"بدء المعالجة المحسنة للموضوع: {topic}")
        
        try:
            user_template = self._load_template('user_prompt_template.md')
            base_prompt = user_template.render(topic=topic)
            logger.info("تم تحميل قالب المستخدم بنجاح")
        except Exception as e:
            logger.error(f"خطأ في تحميل قالب المستخدم: {e}")
            return None

        outputs = {
            'metadata': {
                'topic': topic,
                'timestamp': datetime.now().isoformat(),
                'total_phases': len(self.phases),
                'integration_enabled': enable_integration
            },
            'phases': {},
            'integration_log': []
        }
        
        successful_phases = 0
        
        for phase_code, phase_name, integration_allowed in self.phases:
            logger.info(f"معالجة {phase_code}: {phase_name}")
            
            try:
                task_tpl = self._load_template('task_prompt.md')
                prompt_text = task_tpl.render(
                    phase_name=f'{phase_code}: {phase_name}',
                    task_name='Main Task',
                    context=topic,
                    task_description=f'Define the main goals and requirements for {phase_name} given the topic: {topic}'
                )
                
                # تفعيل التكامل للمراحل المسموحة
                phase_integration = enable_integration and integration_allowed
                
                result = self.call_model_with_integration(prompt_text, phase_integration)
                
                outputs['phases'][phase_code] = {
                    'phase': phase_name,
                    'prompt': prompt_text,
                    'response': result,
                    'status': 'success',
                    'integration_enabled': phase_integration,
                    'timestamp': datetime.now().isoformat()
                }
                
                successful_phases += 1
                logger.info(f"تم إنجاز {phase_code} بنجاح")
                
            except Exception as e:
                logger.error(f"خطأ في معالجة {phase_code}: {e}")
                outputs['phases'][phase_code] = {
                    'phase': phase_name,
                    'error': str(e),
                    'status': 'failed',
                    'timestamp': datetime.now().isoformat()
                }
        
        outputs['metadata']['successful_phases'] = successful_phases
        outputs['metadata']['success_rate'] = f"{(successful_phases/len(self.phases)*100):.1f}%"
        
        # إضافة سجل التكامل
        outputs['integration_log'] = self.system_integrator.get_execution_history()
        
        return outputs
    
    def _load_template(self, name):
        """تحميل قالب من مجلد prompts"""
        try:
            env = Environment(loader=FileSystemLoader('prompts'))
            return env.get_template(name)
        except Exception as e:
            logger.error(f"خطأ في تحميل القالب {name}: {e}")
            raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enhanced AI Orchestrator with direct system integration')
    parser.add_argument('--input', required=True, help='موضوع المشروع')
    parser.add_argument('--output', default='examples/enhanced_run.json', help='ملف الإخراج')
    parser.add_argument('--enable-integration', action='store_true', help='تفعيل التكامل المباشر')
    parser.add_argument('--verbose', '-v', action='store_true', help='تفعيل الوضع المفصل')
    args = parser.parse_args()

    # تعديل مستوى التسجيل حسب الطلب
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # إنشاء مجلد examples إذا لم يكن موجوداً
    os.makedirs('examples', exist_ok=True)

    # إنشاء المحرك المحسن
    orchestrator = EnhancedOrchestrator()
    
    # معالجة الموضوع
    results = orchestrator.process_topic_enhanced(args.input, args.enable_integration)
    
    if results:
        # حفظ النتائج
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"تم حفظ النتائج في: {args.output}")
        print(f"\n✅ تم إنجاز المعالجة المحسنة بنجاح!")
        print(f"📊 معدل النجاح: {results['metadata']['success_rate']}")
        print(f"📈 المراحل الناجحة: {results['metadata']['successful_phases']}/{results['metadata']['total_phases']}")
        print(f"🔧 التكامل المباشر: {'مفعل' if args.enable_integration else 'معطل'}")
        print(f"📁 النتائج محفوظة في: {args.output}")
        
        # عرض سجل التكامل إذا كان مفعلاً
        if args.enable_integration and results['integration_log']:
            print(f"\n🔗 عمليات التكامل المنفذة: {len(results['integration_log'])}")
            for i, log_entry in enumerate(results['integration_log'], 1):
                status = "✅" if log_entry['result']['success'] else "❌"
                print(f"  {i}. {status} {log_entry['request_type']}")
    else:
        logger.error("فشل في معالجة الموضوع")
        exit(1)