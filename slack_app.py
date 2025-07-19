"""
Slack bot for interacting with the AI Orchestrator.
"""
import json
import logging
import os
import sys
import threading
from datetime import datetime

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from orchestrator import Orchestrator
from config import Config

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slack_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def validate_slack_environment():
    """التحقق من متغيرات البيئة المطلوبة لـ Slack"""
    required_vars = ['SLACK_BOT_TOKEN',
                     'SLACK_SIGNING_SECRET', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error("متغيرات البيئة المفقودة: %s", ', '.join(missing_vars))
        return False
    return True


def process_topic_async(topic, respond, user_id):
    """معالجة الموضوع بشكل غير متزامن"""
    try:
        logger.info("بدء المعالجة غير المتزامنة للموضوع: %s", topic)
        config = Config()
        orchestrator = Orchestrator(config)
        results = orchestrator.process_topic(topic)

        if results:
            # تنسيق وإرسال النتائج
            blocks = format_response_blocks(results)

            # حفظ النتائج في ملف
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"examples/slack_run_{user_id}_{timestamp}.json"
            os.makedirs('examples', exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            # إضافة معلومات الملف المحفوظ
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📁 تم حفظ النتائج في: `{filename}`"
                    }
                ]
            })

            respond({
                "response_type": "in_channel",
                "blocks": blocks
            })

            logger.info("تم إرسال النتائج بنجاح للمستخدم %s", user_id)

        else:
            respond({
                "response_type": "ephemeral",
                "text": "❌ حدث خطأ أثناء معالجة الموضوع. يرجى المحاولة مرة أخرى."
            })
            logger.error("فشل في معالجة الموضوع للمستخدم %s", user_id)

    except (IOError, json.JSONDecodeError) as e:
        logger.error("خطأ في المعالجة غير المتزامنة: %s", e)
        respond({
            "response_type": "ephemeral",
            "text": f"❌ حدث خطأ غير متوقع: {str(e)}"
        })

# تهيئة Bolt App
app = App(
    token=os.getenv('SLACK_BOT_TOKEN'),
    signing_secret=os.getenv('SLACK_SIGNING_SECRET')
)


def format_response_blocks(results):
    """تنسيق النتائج لعرضها في Slack"""
    blocks = []

    # معلومات عامة
    metadata = results.get('metadata', {})
    blocks.extend([
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚀 نتائج تحليل: {metadata.get('topic', 'غير محدد')}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"📊 *معدل النجاح:* {metadata.get('success_rate', 'غير محدد')}\n⏰ *وقت المعالجة:* {metadata.get('timestamp', 'غير محدد')}"
            }
        },
        {"type": "divider"}
    ])

    # النتائج لكل مرحلة
    phases = results.get('phases', {})
    config = Config()
    orchestrator = Orchestrator(config)
    for phase_code, phase_name in orchestrator.phases:
        phase_data = phases.get(phase_code, {})

        if phase_data.get('status') == 'success':
            # مرحلة ناجحة
            response_text = phase_data.get('response', 'لا توجد استجابة')
            # تقصير النص إذا كان طويلاً
            if len(response_text) > 1000:
                response_text = response_text[:1000] + "..."

            blocks.extend([
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"✅ {phase_code} - {phase_name}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": response_text
                    }
                }
            ])
        else:
            # مرحلة فاشلة
            error_msg = phase_data.get('error', 'خطأ غير محدد')
            blocks.extend([
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"❌ {phase_code} - {phase_name}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*خطأ:* {error_msg}"
                    }
                }
            ])

        blocks.append({"type": "divider"})

    return blocks

# Listener لأمر Slash /orchestrate


@app.command('/orchestrate')
def handle_orchestrate(ack, respond, command):
    """معالج أمر /orchestrate"""
    ack()

    topic = command.get('text', '').strip()
    user_id = command.get('user_id')

    logger.info("تم استلام أمر /orchestrate من المستخدم %s للموضوع: %s", user_id, topic)

    if not topic:
        respond({
            "response_type": "ephemeral",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "⚠️ *يرجى إدخال موضوع بعد الأمر*\n\n*مثال:*\n"
                        "`/orchestrate تطوير تطبيق جوال للتجارة الإلكترونية`\n\n"
                        "*أو للحصول على المساعدة:*\n`/orchestrate help`"
                    }
                }
            ]
        })
        return

    # التحقق من طلب المساعدة
    if topic.lower() in ['help', 'مساعدة', '?']:
        respond({
            "response_type": "ephemeral",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🤖 AI Orchestrator - دليل الاستخدام"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*الأوامر المتاحة:*\n"
                        "• `/orchestrate موضوع المشروع` - لتحليل ومعالجة موضوع\n"
                        "• `/orchestrate help` - لعرض هذه المساعدة\n"
                        "• `@AI Orchestrator موضوع` - للتفاعل المباشر\n\n"
                        "*أمثلة:*\n"
                        "• `/orchestrate تطوير منصة تعليمية تفاعلية`\n"
                        "• `/orchestrate إنشاء متجر إلكتروني متكامل`\n"
                        "• `/orchestrate تصميم تطبيق إدارة المهام`"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*المراحل التي يغطيها التحليل:*\n"
                        "1️⃣ توليد الأفكار (Ideation)\n"
                        "2️⃣ البحث (Research)\n"
                        "3️⃣ التصميم (Design)\n"
                        "4️⃣ خطة التطوير (Development Plan)\n"
                        "5️⃣ التنفيذ (Execution)\n"
                        "6️⃣ المراجعة والتحسين (Review & Optimize)"
                    }
                }
            ]
        })
        return

    # رسالة تأكيد فورية
    respond({
        "response_type": "in_channel",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🔄 *جارٍ تحليل ومعالجة الموضوع:*\n> {topic}\n\n"
                    "⏳ هذا قد يستغرق بضع دقائق... يرجى الانتظار"
                }
            }
        ]
    })

    # تشغيل المعالجة في thread منفصل لتجنب timeout
    thread = threading.Thread(
        target=process_topic_async,
        args=(topic, respond, user_id)
    )
    thread.daemon = True
    thread.start()

# Listener للإشارات (@mention)
@app.event("app_mention")
def handle_mention(event, say):
    """معالج الإشارات للبوت"""
    text = event.get('text', '').strip()

    # إزالة إشارة البوت من النص
    mention_text = text.split('>', 1)[-1].strip() if '>' in text else text

    if not mention_text or mention_text.lower() in ['help', 'مساعدة']:
        say({
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🤖 AI Orchestrator Bot"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "👋 *مرحباً! أنا AI Orchestrator Bot*\n\n"
                        "*كيفية الاستخدام:*\n"
                        "• `/orchestrate موضوع المشروع` - لتحليل ومعالجة موضوع\n"
                        "• `@AI Orchestrator موضوع` - للتفاعل المباشر\n"
                        "• `@AI Orchestrator help` - لعرض هذه المساعدة\n\n"
                        "*مثال:*\n"
                        "`/orchestrate تطوير منصة تعليمية تفاعلية`"
                    }
                }
            ]
        })
    else:
        # معالجة الموضوع المذكور
        say({
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🔄 *جارٍ معالجة:* {mention_text}\n⏳ يرجى الانتظار..."
                    }
                }
            ]
        })

        try:
            config = Config()
            orchestrator = Orchestrator(config)
            results = orchestrator.process_topic(mention_text)
            if results:
                blocks = format_response_blocks(results)
                say({"blocks": blocks})
            else:
                say({
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "❌ *حدث خطأ أثناء المعالجة*\n"
                                "يرجى المحاولة مرة أخرى أو التحقق من السجلات."
                            }
                        }
                    ]
                })
        except (IOError, json.JSONDecodeError) as e:
            logger.error("خطأ في معالجة الإشارة: %s", e)
            say({
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"❌ *حدث خطأ:* {str(e)}"
                        }
                    }
                ]
            })

# معالج الأخطاء العامة


@app.error
def global_error_handler(error, app_logger, body=None):
    """Global error handler for the app."""
    app_logger.exception("خطأ عام في التطبيق: %s", error)
    return f"حدث خطأ غير متوقع: {error}"


def main():
    """Main function to run the slack bot."""
    # التحقق من متغيرات البيئة
    if not validate_slack_environment():
        print("❌ يرجى إعداد متغيرات البيئة المطلوبة في ملف .env")
        print("💡 يمكنك نسخ .env.example إلى .env وتعديل القيم")
        sys.exit(1)

    logger.info("🚀 بدء تشغيل Slack Bot...")

    try:
        # للتشغيل محلياً مع Socket Mode
        if os.getenv('SLACK_APP_TOKEN'):
            logger.info("استخدام Socket Mode للتشغيل المحلي")
            handler = SocketModeHandler(app, os.getenv('SLACK_APP_TOKEN'))
            handler.start()
        else:
            # للتشغيل على خادم
            logger.info("تشغيل الخادم على المنفذ %s", os.environ.get('PORT', 3000))
            app.start(port=int(os.environ.get('PORT', 3000)))
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت بواسطة المستخدم")
    except (IOError, json.JSONDecodeError) as e:
        logger.error("خطأ في تشغيل البوت: %s", e)
        sys.exit(1)


if __name__ == '__main__':
    main()