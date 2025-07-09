"""
نظام التكامل المباشر للذكاء الاصطناعي
يمنح نموذج GPT القدرة على التعديل المباشر في الأنظمة
"""
import os
import json
import subprocess
import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import tempfile
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemIntegrator:
    """فئة التكامل المباشر مع الأنظمة"""
    
    def __init__(self, config):
        self.config = config
        self.enabled_integrations = self._load_enabled_integrations()
        self.execution_log = []
    
    def _load_enabled_integrations(self) -> Dict[str, bool]:
        """تحميل التكاملات المفعلة"""
        return {
            'file_system': True,
            'git_operations': True,
            'package_management': True,
            'database_operations': True,
            'api_calls': True,
            'deployment': True,
            'system_commands': True,
            'environment_variables': True
        }
    
    def execute_ai_request(self, request_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ طلب من الذكاء الاصطناعي"""
        if not self.enabled_integrations.get(request_type, False):
            return {
                'success': False,
                'error': f'التكامل {request_type} غير مفعل',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            result = self._route_request(request_type, parameters)
            self._log_execution(request_type, parameters, result)
            return result
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self._log_execution(request_type, parameters, error_result)
            return error_result
    
    def _route_request(self, request_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """توجيه الطلب للمعالج المناسب"""
        handlers = {
            'file_system': self._handle_file_operations,
            'git_operations': self._handle_git_operations,
            'package_management': self._handle_package_operations,
            'database_operations': self._handle_database_operations,
            'api_calls': self._handle_api_calls,
            'deployment': self._handle_deployment,
            'system_commands': self._handle_system_commands,
            'environment_variables': self._handle_env_operations
        }
        
        handler = handlers.get(request_type)
        if not handler:
            raise ValueError(f'معالج غير معروف: {request_type}')
        
        return handler(parameters)
    
    def _handle_file_operations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة عمليات الملفات"""
        operation = params.get('operation')
        
        if operation == 'create_file':
            return self._create_file(params['path'], params['content'])
        elif operation == 'modify_file':
            return self._modify_file(params['path'], params['changes'])
        elif operation == 'delete_file':
            return self._delete_file(params['path'])
        elif operation == 'create_directory':
            return self._create_directory(params['path'])
        else:
            raise ValueError(f'عملية ملف غير معروفة: {operation}')
    
    def _handle_git_operations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة عمليات Git"""
        operation = params.get('operation')
        
        if operation == 'commit':
            return self._git_commit(params.get('message', 'AI automated commit'))
        elif operation == 'push':
            return self._git_push(params.get('branch', 'main'))
        elif operation == 'create_branch':
            return self._git_create_branch(params['branch_name'])
        else:
            raise ValueError(f'عملية Git غير معروفة: {operation}')
    
    def _handle_package_operations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة عمليات الحزم"""
        operation = params.get('operation')
        
        if operation == 'install':
            return self._install_package(params['package'])
        elif operation == 'uninstall':
            return self._uninstall_package(params['package'])
        elif operation == 'update':
            return self._update_packages()
        else:
            raise ValueError(f'عملية حزمة غير معروفة: {operation}')
    
    def _handle_database_operations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة عمليات قاعدة البيانات"""
        operation = params.get('operation')
        
        if operation == 'execute_query':
            return self._execute_database_query(params['query'])
        elif operation == 'backup':
            return self._backup_database()
        elif operation == 'migrate':
            return self._run_migrations()
        else:
            raise ValueError(f'عملية قاعدة بيانات غير معروفة: {operation}')
    
    def _handle_api_calls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة استدعاءات API"""
        method = params.get('method', 'GET')
        url = params['url']
        headers = params.get('headers', {})
        data = params.get('data')
        
        response = requests.request(method, url, headers=headers, json=data)
        
        return {
            'success': True,
            'status_code': response.status_code,
            'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            'timestamp': datetime.now().isoformat()
        }
    
    def _handle_deployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة عمليات النشر"""
        platform = params.get('platform', 'heroku')
        
        if platform == 'heroku':
            return self._deploy_to_heroku(params)
        elif platform == 'aws':
            return self._deploy_to_aws(params)
        elif platform == 'docker':
            return self._deploy_to_docker(params)
        else:
            raise ValueError(f'منصة نشر غير مدعومة: {platform}')
    
    def _handle_system_commands(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة أوامر النظام"""
        command = params['command']
        working_dir = params.get('working_dir', '.')
        
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True
        )
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode,
            'timestamp': datetime.now().isoformat()
        }
    
    def _handle_env_operations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة متغيرات البيئة"""
        operation = params.get('operation')
        
        if operation == 'set':
            return self._set_env_variable(params['key'], params['value'])
        elif operation == 'get':
            return self._get_env_variable(params['key'])
        elif operation == 'delete':
            return self._delete_env_variable(params['key'])
        else:
            raise ValueError(f'عملية متغير بيئة غير معروفة: {operation}')
    
    # تنفيذ العمليات الفعلية
    def _create_file(self, path: str, content: str) -> Dict[str, Any]:
        """إنشاء ملف جديد"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                'success': True,
                'message': f'تم إنشاء الملف: {path}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f'فشل في إنشاء الملف {path}: {str(e)}')
    
    def _modify_file(self, path: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """تعديل ملف موجود"""
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f'الملف غير موجود: {path}')
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # تطبيق التغييرات
            if 'replace' in changes:
                for old, new in changes['replace'].items():
                    content = content.replace(old, new)
            
            if 'append' in changes:
                content += changes['append']
            
            if 'prepend' in changes:
                content = changes['prepend'] + content
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'message': f'تم تعديل الملف: {path}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f'فشل في تعديل الملف {path}: {str(e)}')
    
    def _install_package(self, package: str) -> Dict[str, Any]:
        """تثبيت حزمة"""
        result = subprocess.run(
            f'pip install {package}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        return {
            'success': result.returncode == 0,
            'message': f'تثبيت الحزمة: {package}',
            'output': result.stdout,
            'error': result.stderr,
            'timestamp': datetime.now().isoformat()
        }
    
    def _set_env_variable(self, key: str, value: str) -> Dict[str, Any]:
        """تعيين متغير بيئة"""
        env_file = '.env'
        
        # قراءة الملف الحالي
        env_vars = {}
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        k, v = line.strip().split('=', 1)
                        env_vars[k] = v
        
        # تحديث المتغير
        env_vars[key] = value
        
        # كتابة الملف
        with open(env_file, 'w') as f:
            for k, v in env_vars.items():
                f.write(f'{k}={v}\n')
        
        return {
            'success': True,
            'message': f'تم تعيين متغير البيئة: {key}',
            'timestamp': datetime.now().isoformat()
        }
    
    def _log_execution(self, request_type: str, parameters: Dict[str, Any], result: Dict[str, Any]):
        """تسجيل العملية المنفذة"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'request_type': request_type,
            'parameters': parameters,
            'result': result
        }
        
        self.execution_log.append(log_entry)
        
        # حفظ في ملف السجل
        log_file = 'logs/ai_integrations.log'
        os.makedirs('logs', exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """الحصول على تاريخ التنفيذ"""
        return self.execution_log
    
    def enable_integration(self, integration_type: str):
        """تفعيل تكامل معين"""
        self.enabled_integrations[integration_type] = True
    
    def disable_integration(self, integration_type: str):
        """إلغاء تفعيل تكامل معين"""
        self.enabled_integrations[integration_type] = False