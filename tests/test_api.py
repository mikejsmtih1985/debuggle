import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check_success(self):
        """Test health check returns correct response."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "Debuggle Core"
        assert data["version"] == "1.0.0"


class TestTiersEndpoint:
    def test_get_tiers_success(self):
        """Test tiers endpoint returns all available tiers."""
        response = client.get("/api/v1/tiers")
        assert response.status_code == 200
        
        data = response.json()
        assert "tiers" in data
        assert len(data["tiers"]) == 5
        
        # Check first tier (Core)
        core_tier = data["tiers"][0]
        assert core_tier["name"] == "Core"
        assert len(core_tier["icon"]) > 0  # Should have an icon
        assert "Debuggle logs" in core_tier["features"]


class TestBeautifyEndpoint:
    def test_beautify_python_error_success(self):
        """Test beautifying a Python IndexError."""
        payload = {
            "log_input": 'Traceback (most recent call last):\n  File "app.py", line 14, in <module>\n    main()\nIndexError: list index out of range',
            "language": "python",
            "options": {
                "highlight": True,
                "summarize": True,
                "tags": True
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "cleaned_log" in data
        assert "summary" in data
        assert "tags" in data
        assert "metadata" in data
        
        # Check summary was generated
        assert data["summary"] is not None
        assert "index" in data["summary"].lower() or "bounds" in data["summary"].lower()
        
        # Check tags include meaningful content
        assert "Python Error" in data["tags"] or "Critical Error" in data["tags"]
        
        # Check metadata
        assert data["metadata"]["language_detected"] == "python"
        assert data["metadata"]["lines"] > 0
    
    def test_beautify_auto_language_detection(self):
        """Test automatic language detection."""
        payload = {
            "log_input": 'Traceback (most recent call last):\n  File "test.py", line 1\n    print "hello"\n          ^\nSyntaxError: Missing parentheses',
            "language": "auto"
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["metadata"]["language_detected"] == "python"
    
    def test_beautify_with_options_disabled(self):
        """Test beautification with all options disabled."""
        payload = {
            "log_input": "Simple error message",
            "options": {
                "highlight": False,
                "summarize": False,
                "tags": False
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["summary"] is None
        assert len(data["tags"]) == 0
    
    def test_beautify_empty_input_error(self):
        """Test error handling for empty input."""
        payload = {
            "log_input": "",
            "language": "python"
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_beautify_max_lines_limit(self):
        """Test max_lines parameter enforcement."""
        # Create a large log input
        large_log = "\n".join([f"Line {i}: Some error message" for i in range(100)])
        
        payload = {
            "log_input": large_log,
            "options": {
                "max_lines": 50
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["metadata"]["lines"] == 50
        assert data["metadata"]["truncated"] == True
    
    def test_beautify_max_lines_too_large_error(self):
        """Test error when max_lines exceeds limit."""
        payload = {
            "log_input": "test error",
            "options": {
                "max_lines": 10000  # Exceeds limit of 5000
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 422
        
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert "less than or equal to 5000" in str(data["detail"])


class TestRootEndpoint:
    def test_root_endpoint(self):
        """Test root endpoint serves HTML frontend."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "Debuggle" in response.text
        assert "drag" in response.text.lower()
        
    def test_api_info_endpoint(self):
        """Test API info endpoint returns service information."""
        response = client.get("/api/v1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "Debuggle Core"
        assert data["status"] == "running"
        assert "endpoints" in data


class TestErrorHandling:
    def test_invalid_json_error(self):
        """Test handling of malformed JSON."""
        response = client.post(
            "/api/v1/beautify",
            content="invalid json",  # Not JSON
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_field_error(self):
        """Test handling of missing required fields."""
        payload = {
            # Missing log_input
            "language": "python"
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 422
    
    def test_invalid_language_enum_error(self):
        """Test handling of invalid language enum."""
        payload = {
            "log_input": "test error",
            "language": "invalid_language"
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 422


class TestStackTraceIntegration:
    """Integration tests for enhanced stack trace processing."""
    
    def test_beautify_complex_java_stack_trace(self):
        """Test processing complex Java stack trace with multiple caused by."""
        complex_java_stack = """Fatal Error: NullReferenceException: Object reference not set to an instance of an object
   at com.megacorp.chaosengine.core.UnstableQuantumProcessorImpl.invokeParadoxLoop(UnstableQuantumProcessorImpl.java:472)
   at com.megacorp.chaosengine.async.ThreadWeaver$QuantumTask.run(ThreadWeaver.java:198)
   at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)

Caused by: IllegalStateException: Flux capacitor destabilized during async recursion
   at org.quarkus.runtime.TemporalDistortionHandler.processTimeWarp(TemporalDistortionHandler.kt:89)
   at org.quarkus.runtime.TemporalDistortionHandler.lambda$initiateChaos$3(TemporalDistortionHandler.kt:42)

Caused by: ConcurrentModificationException: Race condition detected in fractal cache
   at java.util.HashMap$HashIterator.nextNode(HashMap.java:1441)
   at java.util.HashMap$KeyIterator.next(HashMap.java:1463)"""
        
        payload = {
            "log_input": complex_java_stack,
            "language": "java",
            "options": {
                "highlight": True,
                "summarize": True,
                "tags": True
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should have enhanced processing
        assert "🚨 **Main Problem**" in data["cleaned_log"]
        assert "📋 **What Happened**" in data["cleaned_log"]
        assert "🔍 **Key Code Locations**" in data["cleaned_log"]
        assert "💡 **Suggested Actions**" in data["cleaned_log"]
        
        # Should mention all three exceptions
        assert "NullReferenceException" in data["cleaned_log"]
        assert "IllegalStateException" in data["cleaned_log"]  
        assert "ConcurrentModificationException" in data["cleaned_log"]
        
        # Should have meaningful summary
        assert data["summary"] is not None
        assert "critical" in data["summary"].lower() or "error" in data["summary"].lower()
        
        # Should have specific tags
        assert "Critical Error" in data["tags"]
        assert "Java Error" in data["tags"]
        assert "Stack Trace" in data["tags"]
        assert any("Thread" in tag or "Concurrent" in tag for tag in data["tags"])
        
        # Should detect test/mock data
        assert "Test/Mock Data" in data["tags"]
        
        # Check metadata
        assert data["metadata"]["language_detected"] == "java"
    
    def test_beautify_python_stack_trace(self):
        """Test processing Python stack trace."""
        python_stack = """Traceback (most recent call last):
  File "/app/main.py", line 25, in process_data
    result = data[index]
  File "/app/handlers.py", line 15, in __getitem__
    return self.items[key]
IndexError: list index out of range"""
        
        payload = {
            "log_input": python_stack,
            "language": "python",
            "options": {
                "highlight": True,
                "summarize": True,
                "tags": True
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should have enhanced processing
        assert "🚨 **Main Problem**" in data["cleaned_log"]
        assert "IndexError" in data["cleaned_log"]
        
        # Should have proper tags
        assert "Python Error" in data["tags"] or "Python" in data["tags"]
        assert "Stack Trace" in data["tags"]
        assert "Critical Error" in data["tags"] or "Needs Developer Attention" in data["tags"]
        
        # Check metadata  
        assert data["metadata"]["language_detected"] == "python"
    
    def test_beautify_csharp_stack_trace(self):
        """Test processing C# stack trace."""
        csharp_stack = """System.ArgumentNullException: Value cannot be null. (Parameter 'input')
   at MyApp.DataProcessor.ProcessInput(String input) in C:\\MyApp\\DataProcessor.cs:line 25
   at MyApp.Controllers.ApiController.ProcessData(String data) in C:\\MyApp\\Controllers\\ApiController.cs:line 15
   at MyApp.Program.Main(String[] args) in C:\\MyApp\\Program.cs:line 10"""
        
        payload = {
            "log_input": csharp_stack,
            "language": "csharp",
            "options": {
                "highlight": True,
                "summarize": True,
                "tags": True
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should have enhanced processing
        assert "🚨 **Main Problem**" in data["cleaned_log"]
        assert "ArgumentNullException" in data["cleaned_log"]
        
        # Should have proper tags
        assert "Stack Trace" in data["tags"]
        # Should have some meaningful tags beyond just generic ones
        meaningful_tags = [tag for tag in data["tags"] if tag not in ["Error", "Exception"]]
        assert len(meaningful_tags) > 0
    
    def test_beautify_javascript_stack_trace(self):
        """Test processing JavaScript stack trace."""
        js_stack = """TypeError: Cannot read property 'length' of undefined
    at processArray (app.js:15:10)
    at validateInput (validation.js:8:5)
    at main (app.js:25:5)
    at Object.<anonymous> (app.js:30:1)
    at Module._compile (internal/modules/cjs/loader.js:778:30)"""
        
        payload = {
            "log_input": js_stack,
            "language": "javascript",
            "options": {
                "highlight": True,
                "summarize": True,
                "tags": True
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should have enhanced processing
        assert "🚨 **Main Problem**" in data["cleaned_log"]
        assert "TypeError" in data["cleaned_log"]
        
        # Should have proper tags  
        assert "Stack Trace" in data["tags"]
        # Should have some meaningful tags beyond just generic ones
        meaningful_tags = [tag for tag in data["tags"] if tag not in ["Error", "Exception"]]
        assert len(meaningful_tags) > 0


class TestFileUploadIntegration:
    """Integration tests for file upload with enhanced stack trace processing."""
    
    def test_upload_java_stack_trace_file(self):
        """Test uploading Java stack trace file."""
        # Create test file content
        java_content = """Exception in thread "main" java.lang.NullPointerException: Cannot invoke method on null object
	at com.example.service.DataService.processRequest(DataService.java:45)
	at com.example.controller.ApiController.handleRequest(ApiController.java:23)
	at com.example.Main.main(Main.java:10)

Caused by: java.lang.IllegalArgumentException: Invalid input parameter
	at com.example.validator.InputValidator.validate(InputValidator.java:15)
	at com.example.service.DataService.processRequest(DataService.java:40)
	... 2 more"""
        
        # Simulate file upload
        files = {"file": ("stacktrace.log", java_content, "text/plain")}
        data = {
            "language": "java",
            "highlight": "true",
            "summarize": "true", 
            "tags": "true",
            "max_lines": "1000"
        }
        
        response = client.post("/api/v1/upload-log", files=files, data=data)
        assert response.status_code == 200
        
        result = response.json()
        
        # Should have enhanced processing
        assert "🚨 **Main Problem**" in result["cleaned_log"]
        assert "📋 **What Happened**" in result["cleaned_log"]
        assert "🔍 **Key Code Locations**" in result["cleaned_log"]
        assert "💡 **Suggested Actions**" in result["cleaned_log"]
        
        # Should identify both exceptions
        assert "NullPointerException" in result["cleaned_log"]
        assert "IllegalArgumentException" in result["cleaned_log"]
        
        # Should have proper tags
        assert "Critical Error" in result["tags"]
        assert "Java Error" in result["tags"]
        assert "Stack Trace" in result["tags"]
        
        # Check file metadata
        assert result["metadata"]["filename"] == "stacktrace.log"
        assert result["metadata"]["file_size"] > 0
        assert result["metadata"]["language_detected"] == "java"
    
    def test_upload_empty_file_error(self):
        """Test error handling for empty file upload."""
        files = {"file": ("empty.log", "", "text/plain")}
        data = {"language": "auto"}
        
        response = client.post("/api/v1/upload-log", files=files, data=data)
        assert response.status_code == 400
        
        result = response.json()
        assert "detail" in result
        assert "empty" in result["detail"]["error"].lower()
    
    def test_upload_file_with_encoding_issues(self):
        """Test handling files with different encodings."""
        # Create content with special characters
        content_with_encoding = "Error: Spëcîål chäråctërs in løg\n   at com.example.Test.method(Test.java:1)"
        
        files = {"file": ("special.log", content_with_encoding.encode('utf-8'), "text/plain")}
        data = {"language": "java"}
        
        response = client.post("/api/v1/upload-log", files=files, data=data)
        assert response.status_code == 200
        
        result = response.json()
        assert "Spëcîål chäråctërs" in result["cleaned_log"]


class TestRegressionPrevention:
    """Specific regression tests to prevent the original issues from returning."""
    
    def test_regression_multiline_stack_trace_display(self):
        """Ensure multi-line stack traces are not reduced to single lines."""
        multiline_stack = """Fatal Error: NullReferenceException: Object reference not set
   at com.example.Class1.method1(Class1.java:10)
   at com.example.Class2.method2(Class2.java:20) 
   at com.example.Main.main(Main.java:30)

Caused by: IllegalArgumentException: Invalid parameter
   at com.example.Validator.validate(Validator.java:5)
   at com.example.Class1.method1(Class1.java:8)"""
        
        payload = {
            "log_input": multiline_stack,
            "language": "java",
            "options": {
                "highlight": True,
                "summarize": True,
                "tags": True
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should NOT be reduced to a single line
        lines = data["cleaned_log"].split('\n')
        assert len(lines) > 5  # Much more than a single line
        
        # Should have all the enhanced sections
        assert "📋 **What Happened**" in data["cleaned_log"]
        assert "🔍 **Key Code Locations**" in data["cleaned_log"]
        assert "💡 **Suggested Actions**" in data["cleaned_log"]
        
        # Should show both exceptions in detail
        assert "NullReferenceException" in data["cleaned_log"]
        assert "IllegalArgumentException" in data["cleaned_log"]
        
        # Should list multiple code locations
        location_section = data["cleaned_log"].split("🔍 **Key Code Locations**")[1].split("💡 **Suggested Actions**")[0]
        assert "Class1.method1" in location_section
        assert "Class2.method2" in location_section
        assert "Main.main" in location_section
    
    def test_regression_functional_meaningful_tags(self):
        """Ensure tags are specific and meaningful, not just generic."""
        specific_error_stack = """ConcurrentModificationException: Collection was modified during iteration
   at java.util.HashMap$HashIterator.nextNode(HashMap.java:1441)
   at java.util.HashMap$KeyIterator.next(HashMap.java:1463)
   at com.example.ThreadUnsafeProcessor.processItems(ThreadUnsafeProcessor.java:25)"""
        
        payload = {
            "log_input": specific_error_stack,
            "language": "java",
            "options": {
                "tags": True
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        tags = data["tags"]
        
        # Should have MORE than just generic tags
        generic_tags = {"Error", "Exception", "Java"}
        specific_tags = set(tags) - generic_tags
        assert len(specific_tags) > 0  # Should have non-generic tags
        
        # Should identify the specific problem type
        thread_related_tags = [tag for tag in tags if any(keyword in tag for keyword in ["Thread", "Concurrent", "Race", "Safety", "Modification"])]
        assert len(thread_related_tags) > 0  # Should identify threading issue
        
        # Should have actionable categories
        actionable_tags = [tag for tag in tags if any(keyword in tag for keyword in ["Needs", "Critical", "Serious", "Attention"])]
        assert len(actionable_tags) > 0  # Should suggest action needed
    
    def test_regression_auto_language_detection_with_stack_traces(self):
        """Ensure auto language detection works properly with enhanced stack traces.""" 
        # Test with various language stack traces using auto detection
        test_cases = [
            ("Traceback (most recent call last):\n  File \"test.py\", line 1\nValueError: invalid value", "python"),
            ("System.NullReferenceException: Object reference not set\n   at MyApp.Program.Main in Program.cs:line 10", "csharp"),  
            ("TypeError: Cannot read property 'x' of undefined\n    at app.js:15:10", "javascript"),
            ("Exception in thread \"main\" java.lang.NullPointerException\n\tat com.example.Main.main(Main.java:10)", "java")
        ]
        
        for stack_trace, expected_language in test_cases:
            payload = {
                "log_input": stack_trace,
                "language": "auto",
                "options": {
                    "highlight": True,
                    "summarize": True,
                    "tags": True
                }
            }
            
            response = client.post("/api/v1/beautify", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["metadata"]["language_detected"] == expected_language
            
            # Should still have enhanced processing
            assert "🚨 **Main Problem**" in data["cleaned_log"], f"Failed for {expected_language}"
            assert len(data["tags"]) > 1, f"No meaningful tags for {expected_language}"