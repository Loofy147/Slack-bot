import os
import json
import logging
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
import argparse
from datetime import datetime
from dotenv import load_dotenv
import time

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def validate_environment():
    """التحقق من متغيرات البيئة المطلوبة"""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"متغيرات البيئة المفقودة: {', '.join(missing_vars)}")
        logger.error("يرجى إنشاء ملف .env وإضافة المتغيرات المطلوبة")
        return False
    return True

def load_template(name):
    """تحميل قالب من مجلد prompts"""
    try:
        env = Environment(loader=FileSystemLoader('prompts'))
        return env.get_template(name)
    except Exception as e:
        logger.error(f"خطأ في تحميل القالب {name}: {e}")
        raise

# المراحل الأساسية للمشروع
PHASES = [
    ('Phase 0', 'Ideation'),
    ('Phase 1', 'Research'),
    ('Phase 2', 'Design'),
    ('Phase 3', 'Development Plan'),
    ('Phase 4', 'Execution'),
    ('Phase 5', 'Review & Optimize'),
]

def call_model(prompt, max_retries=3):
    """استدعاء نموذج OpenAI مع إعادة المحاولة"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    for attempt in range(max_retries):
        try:
            # قراءة system prompt
            with open('prompts/system_prompt.md', 'r', encoding='utf-8') as f:
                system_content = f.read()
            
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4'),
                messages=[
                    {'role': 'system', 'content': system_content},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.warning(f"المحاولة {attempt + 1} فشلت: {e}")
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + 1  # Exponential backoff
                logger.info(f"انتظار {wait_time} ثانية قبل المحاولة التالية...")
                time.sleep(wait_time)
            if attempt == max_retries - 1:
                logger.error(f"فشل في استدعاء النموذج بعد {max_retries} محاولات")
                return f"خطأ: لم يتمكن من الحصول على استجابة من النموذج. {str(e)}"

def process_topic(topic):
    """معالجة موضوع عبر جميع المراحل"""
    logger.info(f"بدء معالجة الموضوع: {topic}")
    
    try:
        user_template = load_template('user_prompt_template.md')
        base_prompt = user_template.render(topic=topic)
        logger.info("تم تحميل قالب المستخدم بنجاح")
    except Exception as e:
        logger.error(f"خطأ في تحميل قالب المستخدم: {e}")
        return None

    outputs = {
        'metadata': {
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'total_phases': len(PHASES)
        },
        'phases': {}
    }
    
    successful_phases = 0
    
    for phase_code, phase_name in PHASES:
        logger.info(f"معالجة {phase_code}: {phase_name}")
        
        try:
            task_tpl = load_template('task_prompt.md')
            prompt_text = task_tpl.render(
                phase_name=f'{phase_code}: {phase_name}',
                task_name='Main Task',
                context=topic,
                task_description=f'Define the main goals and requirements for {phase_name} given the topic: {topic}'
            )
            
            result = call_model(prompt_text)
            
            outputs['phases'][phase_code] = {
                'phase': phase_name,
                'prompt': prompt_text,
                'response': result,
                'status': 'success',
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
    outputs['metadata']['success_rate'] = f"{(successful_phases/len(PHASES)*100):.1f}%"
    
    return outputs

if __name__ == '__main__':
    # التحقق من متغيرات البيئة
    if not validate_environment():
        exit(1)

    parser = argparse.ArgumentParser(description='AI Orchestrator for project planning')
    parser.add_argument('--input', required=True, help='موضوع المشروع')
    parser.add_argument('--output', default='examples/sample_run.json', help='ملف الإخراج')
    parser.add_argument('--verbose', '-v', action='store_true', help='تفعيل الوضع المفصل')
    args = parser.parse_args()

    # تعديل مستوى التسجيل حسب الطلب
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # إنشاء مجلد examples إذا لم يكن موجوداً
    os.makedirs('examples', exist_ok=True)

    # معالجة الموضوع
    results = process_topic(args.input)
    
    if results:
        # حفظ النتائج
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"تم حفظ النتائج في: {args.output}")
        print(f"\n✅ تم إنجاز المعالجة بنجاح!")
        print(f"📊 معدل النجاح: {results['metadata']['success_rate']}")
        print(f"📈 المراحل الناجحة: {results['metadata']['successful_phases']}/{results['metadata']['total_phases']}")
        print(f"📁 النتائج محفوظة في: {args.output}")
    else:
        logger.error("فشل في معالجة الموضوع")
        exit(1)