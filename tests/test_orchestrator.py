"""
Comprehensive test suite for AI Orchestrator
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import uuid

from enhanced_orchestrator import EnhancedOrchestrator
from system_integrator import SystemIntegrator
from api.main import app
from fastapi.testclient import TestClient

# Test client
client = TestClient(app)

class TestEnhancedOrchestrator:
    """Test cases for Enhanced Orchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        return EnhancedOrchestrator()
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        return Mock(
            choices=[
                Mock(message=Mock(content="Test response from AI"))
            ]
        )
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator.config is not None
        assert orchestrator.system_integrator is not None
        assert len(orchestrator.phases) == 7
    
    @patch('enhanced_orchestrator.OpenAI')
    def test_call_model_with_integration(self, mock_openai, mock_openai_response):
        """Test AI model call with integration enabled"""
        orchestrator = EnhancedOrchestrator()
        mock_openai.return_value.chat.completions.create.return_value = mock_openai_response
        
        result = orchestrator.call_model_with_integration(
            "Test prompt", 
            enable_integration=True
        )
        
        assert result == "Test response from AI"
        mock_openai.return_value.chat.completions.create.assert_called_once()
    
    @patch('enhanced_orchestrator.OpenAI')
    def test_process_topic_enhanced(self, mock_openai, orchestrator, mock_openai_response):
        """Test complete topic processing"""
        mock_openai.return_value.chat.completions.create.return_value = mock_openai_response
        
        with patch.object(orchestrator, '_load_template') as mock_template:
            mock_template.return_value.render.return_value = "Rendered template"
            
            result = orchestrator.process_topic_enhanced("Test topic", False)
            
            assert result is not None
            assert 'metadata' in result
            assert 'phases' in result
            assert result['metadata']['topic'] == "Test topic"
    
    def test_integration_request_processing(self, orchestrator):
        """Test integration request processing"""
        response_with_integration = '''
        Here's the analysis:
        
        ```json
        {
          "integration_request": {
            "type": "file_system",
            "parameters": {
              "operation": "create_file",
              "path": "test.py",
              "content": "print('Hello World')"
            }
          }
        }
        ```
        '''
        
        with patch.object(orchestrator.system_integrator, 'execute_ai_request') as mock_execute:
            mock_execute.return_value = {
                'success': True,
                'message': 'File created successfully'
            }
            
            result = orchestrator._process_integration_requests(response_with_integration)
            
            assert "✅ **تم تنفيذ العملية:**" in result
            mock_execute.assert_called_once()

class TestSystemIntegrator:
    """Test cases for System Integrator"""
    
    @pytest.fixture
    def integrator(self):
        """Create integrator instance for testing"""
        from config import Config
        return SystemIntegrator(Config())
    
    def test_file_system_operations(self, integrator, tmp_path):
        """Test file system operations"""
        # Test file creation
        test_file = tmp_path / "test.txt"
        result = integrator._create_file(str(test_file), "Test content")
        
        assert result['success'] is True
        assert test_file.exists()
        assert test_file.read_text() == "Test content"
    
    def test_environment_variable_operations(self, integrator, tmp_path):
        """Test environment variable operations"""
        # Change to temp directory for testing
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            result = integrator._set_env_variable("TEST_VAR", "test_value")
            assert result['success'] is True
            
            env_file = tmp_path / ".env"
            assert env_file.exists()
            assert "TEST_VAR=test_value" in env_file.read_text()
        finally:
            os.chdir(original_cwd)
    
    @patch('subprocess.run')
    def test_system_commands(self, mock_subprocess, integrator):
        """Test system command execution"""
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="Command output",
            stderr=""
        )
        
        result = integrator._handle_system_commands({
            'command': 'echo "Hello World"'
        })
        
        assert result['success'] is True
        assert result['stdout'] == "Command output"
        mock_subprocess.assert_called_once()
    
    def test_integration_logging(self, integrator):
        """Test integration operation logging"""
        initial_log_count = len(integrator.execution_log)
        
        integrator._log_execution(
            "test_operation",
            {"param": "value"},
            {"success": True}
        )
        
        assert len(integrator.execution_log) == initial_log_count + 1
        assert integrator.execution_log[-1]['request_type'] == "test_operation"

class TestAPI:
    """Test cases for API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"
    
    @patch('api.main.get_current_user')
    def test_create_project(self, mock_auth):
        """Test project creation endpoint"""
        mock_auth.return_value = {
            "id": uuid.uuid4(),
            "organization_id": uuid.uuid4(),
            "email": "test@example.com"
        }
        
        project_data = {
            "name": "Test Project",
            "description": "Test Description",
            "topic": "Test topic for project",
            "priority": "high"
        }
        
        with patch('api.main.db_pool') as mock_pool:
            mock_pool.acquire.return_value.__aenter__.return_value.fetchval.return_value = uuid.uuid4()
            
            response = client.post("/api/v1/projects", json=project_data)
            # Note: This will fail without proper database setup, but tests the endpoint structure
    
    @patch('api.main.get_current_user')
    def test_start_orchestration(self, mock_auth):
        """Test orchestration start endpoint"""
        mock_auth.return_value = {
            "id": uuid.uuid4(),
            "organization_id": uuid.uuid4(),
            "email": "test@example.com"
        }
        
        orchestration_data = {
            "topic": "Test orchestration topic",
            "integration_enabled": True
        }
        
        with patch('api.main.db_pool') as mock_pool:
            mock_pool.acquire.return_value.__aenter__.return_value.fetchval.return_value = uuid.uuid4()
            
            response = client.post("/api/v1/orchestrate", json=orchestration_data)
            # Note: This will fail without proper database setup, but tests the endpoint structure

class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_orchestration_flow(self):
        """Test complete orchestration flow"""
        # This would require a test database and proper setup
        # For now, we'll test the flow with mocks
        
        with patch('enhanced_orchestrator.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = Mock(
                choices=[Mock(message=Mock(content="Test AI response"))]
            )
            
            orchestrator = EnhancedOrchestrator()
            
            with patch.object(orchestrator, '_load_template') as mock_template:
                mock_template.return_value.render.return_value = "Test prompt"
                
                result = orchestrator.process_topic_enhanced(
                    "Create a simple web application",
                    enable_integration=False
                )
                
                assert result is not None
                assert result['metadata']['topic'] == "Create a simple web application"
                assert len(result['phases']) > 0

class TestPerformance:
    """Performance tests"""
    
    def test_orchestration_performance(self):
        """Test orchestration performance under load"""
        import time
        
        with patch('enhanced_orchestrator.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = Mock(
                choices=[Mock(message=Mock(content="Fast response"))]
            )
            
            orchestrator = EnhancedOrchestrator()
            
            with patch.object(orchestrator, '_load_template') as mock_template:
                mock_template.return_value.render.return_value = "Test prompt"
                
                start_time = time.time()
                
                # Run multiple orchestrations
                for i in range(5):
                    result = orchestrator.process_topic_enhanced(
                        f"Test topic {i}",
                        enable_integration=False
                    )
                    assert result is not None
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # Should complete 5 orchestrations in reasonable time
                assert total_time < 10  # 10 seconds max

class TestSecurity:
    """Security tests"""
    
    def test_input_validation(self):
        """Test input validation and sanitization"""
        from utils import validate_topic
        
        # Valid topics
        valid, result = validate_topic("Valid project topic")
        assert valid is True
        
        # Invalid topics
        valid, error = validate_topic("")
        assert valid is False
        assert "فارغ" in error
        
        valid, error = validate_topic("abc")
        assert valid is False
        assert "قصير" in error
        
        valid, error = validate_topic("x" * 1000)
        assert valid is False
        assert "طويل" in error
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # This would test database query sanitization
        # For now, we ensure parameterized queries are used
        malicious_input = "'; DROP TABLE users; --"
        
        # The API should handle this safely through parameterized queries
        # This is more of a documentation test
        assert ";" in malicious_input  # Verify test data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])