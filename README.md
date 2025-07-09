# Meta Orchestrator AI

هذا المستودع يحوي قالبًا عامًا لتصميم نموذج Orchestrator-Architect وفق إطار "AI Orchestrator-Architect".

## الهيكلية
- **.env**: يحتوي على متغيرات البيئة (سرّيّة).
- **.gitignore**: يتجاهل الملفات الحساسة.
- **orchestrator.py**: سكريبت رئيسي يدير تدفق البرومبتس إلى نماذج متعددة ويجمع النتائج.
- **slack_app.py**: تطبيق Slack Bolt الذي يستدعي Orchestrator.
- **prompts/**: يحتوي على قوالب البرومبتات:
  - `system_prompt.md`: التعليمات العامة للنظام.
  - `user_prompt_template.md`: قالب برومبت لاستقبال المدخلات الديناميكية.
  - `task_prompt.md`: قوالب البرومبت لكل مهمة فرعية.
- **examples/**: مثال تشغيل وحفظ النتائج في JSON.
- **requirements.txt**: تبعيات Python.

## حماية السرّية
تأكد أن ملف `.env` مدرج في `.gitignore` حتى لا يُنشر لحسابات عامة.

## خطوات الاستخدام

### 1. إعداد البيئة
```bash
# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate     # على Windows

# تثبيت التبعيات
pip install -r requirements.txt
```

### 2. إعداد متغيرات البيئة
انسخ ملف `.env.example` إلى `.env` وعدّل القيم:

```bash
cp .env.example .env
```

ثم عدّل ملف `.env` مع قيمك الفعلية:
```env
# مطلوب
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
OPENAI_MODEL=gpt-4

# اختياري - فقط للتكامل مع Slack
SLACK_BOT_TOKEN=xoxb-your-actual-bot-token
SLACK_SIGNING_SECRET=your-actual-signing-secret
SLACK_APP_TOKEN=xapp-your-actual-app-token

### 3. الاستخدام المباشر
```bash
# الاستخدام الأساسي
python orchestrator.py --input "موضوعك هنا"

# مع تحديد ملف الإخراج
python orchestrator.py --input "موضوعك هنا" --output "my_results.json"

# مع الوضع المفصل
python orchestrator.py --input "موضوعك هنا" --verbose
```

### 4. تكامل مع Slack
```bash
python slack_app.py
```

في Slack، يمكنك استخدام:
- `/orchestrate موضوعك` - لتحليل موضوع
- `/orchestrate help` - للحصول على المساعدة
- `@AI Orchestrator موضوعك` - للتفاعل المباشر

## الأوامر والخيارات

### orchestrator.py
```bash
python orchestrator.py --help
```

**الخيارات:**
- `--input`: موضوع المشروع (مطلوب)
- `--output`: ملف الإخراج (افتراضي: examples/sample_run.json)
- `--verbose`: تفعيل الوضع المفصل

### slack_app.py
**أوامر Slack:**
- `/orchestrate موضوع` - تحليل موضوع جديد
- `/orchestrate help` - عرض المساعدة
- `@AI Orchestrator موضوع` - تفاعل مباشر

## الميزات المحسّنة
- ✅ معالجة أفضل للأخطاء
- ✅ تسجيل مفصل للعمليات
- ✅ تحديث لاستخدام OpenAI API الحديث
- ✅ تحسينات أمنية
- ✅ دعم كامل لـ Slack Bolt
- ✅ تنسيق محسّن للمخرجات
- ✅ معالجة غير متزامنة في Slack
- ✅ نظام إعادة المحاولة مع Exponential Backoff
- ✅ التحقق من صحة المدخلات
- ✅ ملف إعدادات مركزي
- ✅ وظائف مساعدة منظمة

## هيكل المشروع المحدث
```
meta-orchestrator/
├── .env.example       # مثال على متغيرات البيئة
├── .env              # متغيرات البيئة (مخفي)
├── .gitignore        # ملفات مستبعدة من Git
├── README.md         # دليل الاستخدام
├── config.py         # إعدادات التطبيق المركزية
├── utils.py          # وظائف مساعدة مشتركة
├── orchestrator.py   # السكريبت الرئيسي
├── slack_app.py      # تطبيق Slack
├── requirements.txt  # تبعيات Python
├── prompts/          # قوالب البرومبتات
│   ├── system_prompt.md
│   ├── user_prompt_template.md
│   └── task_prompt.md
├── examples/         # أمثلة المخرجات
│   └── sample_run_template.json
└── logs/            # ملفات السجلات (تُنشأ تلقائياً)
```
## استكشاف الأخطاء

### مشاكل شائعة وحلولها:

1. **خطأ في مفتاح API:**
   ```
   خطأ: مفتاح OPENAI_API_KEY غير موجود
   ```
   **الحل:** تأكد من وجود ملف `.env` مع مفتاح API صحيح

2. **خطأ في الاتصال:**
   ```
   خطأ: فشل في استدعاء النموذج
   ```
   **الحل:** تحقق من اتصال الإنترنت ومن صحة مفتاح API

3. **خطأ في Slack:**
   ```
   خطأ: متغيرات البيئة المفقودة
   ```
   **الحل:** تأكد من إعداد `SLACK_BOT_TOKEN` و `SLACK_SIGNING_SECRET`

4. **مشكلة في الأذونات:**
   ```
   خطأ: لا يمكن إنشاء الملف
   ```
   **الحل:** تأكد من أذونات الكتابة في مجلد المشروع

### فحص السجلات:
```bash
# عرض السجلات الحديثة
tail -f logs/app_$(date +%Y%m%d).log

# البحث عن أخطاء محددة
grep "ERROR" logs/app_*.log
```

### اختبار الإعداد:
```bash
# اختبار سريع
python orchestrator.py --input "اختبار" --verbose

# اختبار Slack (إذا كان مُعداً)
python -c "from slack_app import validate_slack_environment; print('✅ Slack configured' if validate_slack_environment() else '❌ Slack not configured')"
```