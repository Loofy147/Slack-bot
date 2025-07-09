"""
وظائف مساعدة مشتركة
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

def setup_logging(log_level: str = 'INFO', log_dir: str = 'logs') -> logging.Logger:
    """إعداد نظام التسجيل"""
    # إنشاء مجلد السجلات
    os.makedirs(log_dir, exist_ok=True)
    
    # تحديد مستوى التسجيل
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # إعداد التنسيق
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # إعداد معالج الملف
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log'),
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # إعداد معالج وحدة التحكم
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # إعداد المسجل الرئيسي
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def save_results(data: Dict[Any, Any], filepath: str) -> bool:
    """حفظ النتائج في ملف JSON"""
    try:
        # إنشاء المجلد إذا لم يكن موجوداً
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        logging.error(f"خطأ في حفظ الملف {filepath}: {e}")
        return False

def load_results(filepath: str) -> Optional[Dict[Any, Any]]:
    """تحميل النتائج من ملف JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"خطأ في تحميل الملف {filepath}: {e}")
        return None

def format_timestamp(timestamp: Optional[str] = None) -> str:
    """تنسيق الطابع الزمني"""
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """تقصير النص إذا كان طويلاً"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def validate_topic(topic: str) -> tuple[bool, str]:
    """التحقق من صحة الموضوع المدخل"""
    if not topic or not topic.strip():
        return False, "الموضوع فارغ"
    
    topic = topic.strip()
    
    if len(topic) < 5:
        return False, "الموضوع قصير جداً (أقل من 5 أحرف)"
    
    if len(topic) > 500:
        return False, "الموضوع طويل جداً (أكثر من 500 حرف)"
    
    return True, topic

def calculate_success_rate(successful: int, total: int) -> str:
    """حساب معدل النجاح"""
    if total == 0:
        return "0.0%"
    return f"{(successful / total * 100):.1f}%"

def create_progress_indicator(current: int, total: int) -> str:
    """إنشاء مؤشر التقدم"""
    percentage = (current / total) * 100 if total > 0 else 0
    filled = int(percentage // 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"[{bar}] {percentage:.1f}% ({current}/{total})"