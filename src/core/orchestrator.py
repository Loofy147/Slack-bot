"""
AI Orchestrator for project planning and execution.
"""
import argparse
import json
import logging
import os
import sys

from dotenv import load_dotenv

from base_orchestrator import BaseOrchestrator
from config import Config

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
        logger.error("متغيرات البيئة المفقودة: %s", ', '.join(missing_vars))
        logger.error("يرجى إنشاء ملف .env وإضافة المتغيرات المطلوبة")
        return False
    return True


class Orchestrator(BaseOrchestrator):
    """Orchestrator for project planning and execution."""

    def __init__(self, config):
        super().__init__(config)
        self.phases = [
            ('Phase 0', 'Ideation'),
            ('Phase 1', 'Research'),
            ('Phase 2', 'Design'),
            ('Phase 3', 'Development Plan'),
            ('Phase 4', 'Execution'),
            ('Phase 5', 'Review & Optimize'),
        ]


def main():
    """Main function to run the orchestrator from the command line."""
    # التحقق من متغيرات البيئة
    if not validate_environment():
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description='AI Orchestrator for project planning')
    parser.add_argument('--input', required=True, help='موضوع المشروع')
    parser.add_argument('--output', default='examples/sample_run.json',
                        help='ملف الإخراج')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='تفعيل الوضع المفصل')
    args = parser.parse_args()

    # تعديل مستوى التسجيل حسب الطلب
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # إنشاء مجلد examples إذا لم يكن موجوداً
    os.makedirs('examples', exist_ok=True)

    # معالجة الموضوع
    config = Config()
    orchestrator = Orchestrator(config)
    results = orchestrator.process_topic(args.input)

    if results:
        # حفظ النتائج
        with open(args.output, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=2)

        logger.info("تم حفظ النتائج في: %s", args.output)
        print("\n✅ تم إنجاز المعالجة بنجاح!")
        print(f"📊 معدل النجاح: {results['metadata']['success_rate']}")
        print(
            f"📈 المراحل الناجحة: {results['metadata']['successful_phases']}/"
            f"{results['metadata']['total_phases']}")
        print(f"📁 النتائج محفوظة في: {args.output}")
    else:
        logger.error("فشل في معالجة الموضوع")
        sys.exit(1)


if __name__ == '__main__':
    main()