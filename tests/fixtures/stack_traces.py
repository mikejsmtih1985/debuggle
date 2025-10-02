"""
Test fixtures for stack trace testing.
Contains various real-world stack trace examples in different languages and scenarios.
"""

# Java Stack Traces
JAVA_SIMPLE_NPE = """Exception in thread "main" java.lang.NullPointerException
	at com.example.service.UserService.getUser(UserService.java:45)
	at com.example.controller.UserController.handleGetUser(UserController.java:23) 
	at com.example.Main.main(Main.java:10)"""

JAVA_COMPLEX_MULTI_CAUSE = """Fatal Error: NullReferenceException: Object reference not set to an instance of an object
   at com.megacorp.chaosengine.core.UnstableQuantumProcessorImpl.invokeParadoxLoop(UnstableQuantumProcessorImpl.java:472)
   at com.megacorp.chaosengine.async.ThreadWeaver$QuantumTask.run(ThreadWeaver.java:198)
   at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
   at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
   at java.lang.Thread.run(Thread.java:748)

Caused by: IllegalStateException: Flux capacitor destabilized during async recursion
   at org.quarkus.runtime.TemporalDistortionHandler.processTimeWarp(TemporalDistortionHandler.kt:89)
   at org.quarkus.runtime.TemporalDistortionHandler.lambda$initiateChaos$3(TemporalDistortionHandler.kt:42)
   at io.reactivex.internal.observers.LambdaObserver.onNext(LambdaObserver.java:67)
   at com.megacorp.chaosengine.data.MemLeakGenerator.spillRandomBytes(MemLeakGenerator.java:305)
   at com.megacorp.chaosengine.data.MemLeakGenerator$$FastClassBySpringCGLIB$$a7b9f2.invoke(<generated>)
   at org.springframework.cglib.proxy.MethodProxy.invoke(MethodProxy.java:218)
   ... 12 more

Caused by: ConcurrentModificationException: Race condition detected in fractal cache
   at java.util.HashMap$HashIterator.nextNode(HashMap.java:1441)
   at java.util.HashMap$KeyIterator.next(HashMap.java:1463)
   at com.megacorp.chaosengine.cache.FractalCacheMutator.scrambleEntries(FractalCacheMutator.java:93)
   at com.megacorp.chaosengine.cache.FractalCacheMutator$$Lambda$45/0x0000000800c6f840.apply(Unknown Source)
   at java.util.stream.ReferencePipeline$3$1.accept(ReferencePipeline.java:193)
   at java.util.ArrayList$ArrayListSpliterator.forEachRemaining(ArrayList.java:1382)
   ... 28 more"""

JAVA_CONCURRENT_MODIFICATION = """ConcurrentModificationException: Collection was modified during iteration
   at java.util.HashMap$HashIterator.nextNode(HashMap.java:1441)
   at java.util.HashMap$KeyIterator.next(HashMap.java:1463)
   at com.example.processor.DataProcessor.processItems(DataProcessor.java:87)
   at com.example.service.BatchService.processBatch(BatchService.java:45)
   at com.example.controller.BatchController.startProcessing(BatchController.java:23)"""

JAVA_SPRING_BOOT_ERROR = """org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'userService': Injection of autowired dependencies failed; nested exception is org.springframework.beans.factory.BeanCreationException: Could not autowire field: private com.example.repository.UserRepository com.example.service.UserService.userRepository; nested exception is org.springframework.beans.factory.NoSuchBeanDefinitionException: No qualifying bean of type [com.example.repository.UserRepository] found for dependency: expected at least 1 bean which qualifies as autowire candidate for this dependency. Dependency annotations: {@org.springframework.beans.factory.annotation.Autowired(required=true)}
	at org.springframework.beans.factory.annotation.AutowiredAnnotationBeanPostProcessor.postProcessPropertyValues(AutowiredAnnotationBeanPostProcessor.java:334)
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.populateBean(AbstractAutowireCapableBeanFactory.java:1214)
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:543)
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:482)
	at org.springframework.beans.factory.support.AbstractBeanFactory$1.getObject(AbstractBeanFactory.java:306)"""

# Python Stack Traces  
PYTHON_SIMPLE_INDEX_ERROR = """Traceback (most recent call last):
  File "app.py", line 14, in <module>
    main()
  File "app.py", line 10, in main
    result = data[999] 
IndexError: list index out of range"""

PYTHON_COMPLEX_CHAIN = """Traceback (most recent call last):
  File "/usr/local/lib/python3.9/site-packages/django/core/handlers/exception.py", line 47, in inner
    response = get_response(request)
  File "/usr/local/lib/python3.9/site-packages/django/core/handlers/base.py", line 181, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/app/views.py", line 25, in user_detail
    user = User.objects.get(id=user_id)
  File "/usr/local/lib/python3.9/site-packages/django/db/models/manager.py", line 85, in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
  File "/usr/local/lib/python3.9/site-packages/django/db/models/query.py", line 496, in get
    raise self.model.DoesNotExist(
User.DoesNotExist: User matching query does not exist."""

PYTHON_IMPORT_ERROR = """Traceback (most recent call last):
  File "main.py", line 1, in <module>
    from mypackage.utils import helper_function
  File "/app/mypackage/utils.py", line 5, in <module>
    import missing_library
ModuleNotFoundError: No module named 'missing_library'"""

PYTHON_TYPE_ERROR = """Traceback (most recent call last):
  File "calculator.py", line 15, in <module>
    result = add_numbers("5", "10")
  File "calculator.py", line 8, in add_numbers
    return a + b
  File "calculator.py", line 3, in __add__
    return int(self.value) + int(other.value)
TypeError: unsupported operand type(s) for +: 'str' and 'str'"""

# C# Stack Traces
CSHARP_NULL_REFERENCE = """System.NullReferenceException: Object reference not set to an instance of an object.
   at MyApp.Services.UserService.GetUser(Int32 userId) in C:\\MyApp\\Services\\UserService.cs:line 25
   at MyApp.Controllers.UserController.GetUserDetails(Int32 id) in C:\\MyApp\\Controllers\\UserController.cs:line 15
   at MyApp.Program.Main(String[] args) in C:\\MyApp\\Program.cs:line 10"""

CSHARP_ARGUMENT_EXCEPTION = """System.ArgumentNullException: Value cannot be null. (Parameter 'connectionString')
   at MyApp.Data.DatabaseContext..ctor(String connectionString) in C:\\MyApp\\Data\\DatabaseContext.cs:line 12
   at MyApp.Services.UserService..ctor(String connectionString) in C:\\MyApp\\Services\\UserService.cs:line 8
   at MyApp.Controllers.UserController..ctor(UserService userService) in C:\\MyApp\\Controllers\\UserController.cs:line 5
   at MyApp.Program.Main(String[] args) in C:\\MyApp\\Program.cs:line 15"""

CSHARP_ASYNC_EXCEPTION = """System.AggregateException: One or more errors occurred. ---> System.InvalidOperationException: Operation is not valid due to the current state of the object.
   at MyApp.Services.AsyncService.<ProcessDataAsync>d__1.MoveNext() in C:\\MyApp\\Services\\AsyncService.cs:line 25
--- End of stack trace from previous location where exception was thrown ---
   at System.Runtime.ExceptionServices.ExceptionDispatchInfo.Throw()
   at System.Runtime.CompilerServices.TaskAwaiter.HandleNonSuccessAndDebuggerNotification(Task task)
   at MyApp.Controllers.DataController.<ProcessAsync>d__0.MoveNext() in C:\\MyApp\\Controllers\\DataController.cs:line 15
   --- End of inner exception stack trace ---
   at System.Threading.Tasks.Task.ThrowIfExceptional(Boolean includeTaskCanceledExceptions)
   at System.Threading.Tasks.Task.Wait(Int32 millisecondsTimeout, CancellationToken cancellationToken)
   at MyApp.Program.Main(String[] args) in C:\\MyApp\\Program.cs:line 20"""

# JavaScript Stack Traces
JAVASCRIPT_TYPE_ERROR = """TypeError: Cannot read property 'length' of undefined
    at processArray (app.js:15:10)
    at validateInput (validation.js:8:5)
    at main (app.js:25:5)
    at Object.<anonymous> (app.js:30:1)
    at Module._compile (internal/modules/cjs/loader.js:778:30)
    at Object.Module._extensions..js (internal/modules/cjs/loader.js:789:10)
    at Module.load (internal/modules/cjs/loader.js:653:32)
    at Function.Module._load (internal/modules/cjs/loader.js:593:12)"""

JAVASCRIPT_REFERENCE_ERROR = """ReferenceError: myUndefinedVariable is not defined
    at calculateTotal (calculator.js:42:5)
    at processOrder (order.js:18:12)
    at Object.submitOrder (main.js:65:8)
    at HTMLButtonElement.<anonymous> (main.js:120:25)
    at HTMLButtonElement.dispatch (jquery-3.6.0.min.js:2:43064)
    at HTMLButtonElement.v.handle (jquery-3.6.0.min.js:2:41048)"""

JAVASCRIPT_ASYNC_ERROR = """UnhandledPromiseRejectionWarning: Error: Database connection failed
    at DatabaseManager.connect (/app/database.js:25:15)
    at processTicksAndRejections (internal/process/task_queues.js:97:5)
    at async UserService.getUserById (/app/services/userService.js:15:20)
    at async UserController.getUser (/app/controllers/userController.js:10:25)
    at async /app/routes/users.js:8:5"""

JAVASCRIPT_NODE_MODULE_ERROR = """Error: Cannot find module 'missing-package'
Require stack:
- /app/node_modules/some-package/index.js
- /app/services/dataService.js
- /app/app.js
    at Function.Module._resolveFilename (internal/modules/cjs/loader.js:815:15)
    at Function.Module._load (internal/modules/cjs/loader.js:667:27)
    at Module.require (internal/modules/cjs/loader.js:887:19)
    at require (internal/modules/cjs/helpers.js:74:18)
    at Object.<anonymous> (/app/node_modules/some-package/index.js:1:15)"""

# Edge Cases and Special Scenarios
MIXED_LANGUAGE_STACK = """Error in Kotlin coroutine:
kotlinx.coroutines.CancellationException: Job was cancelled
	at kotlinx.coroutines.JobSupport.cancel$kotlinx_coroutines_core(JobSupport.kt:1485)
	at com.example.service.AsyncProcessor.processData(AsyncProcessor.kt:45)
	
Caused by Java exception:
java.sql.SQLException: Database connection timeout
	at com.example.database.ConnectionManager.getConnection(ConnectionManager.java:78)
	at com.example.repository.UserRepository.findById(UserRepository.java:25)"""

VERY_LONG_STACK_TRACE = """Exception in thread "main" java.lang.StackOverflowError
""" + "\n".join([f"\tat com.example.RecursiveClass.infiniteLoop(RecursiveClass.java:{15 + i})" for i in range(100)])

STACK_WITH_SUPPRESSED = """Exception in thread "main" java.lang.RuntimeException: Primary exception
	at com.example.Main.main(Main.java:10)
	Suppressed: java.io.IOException: Resource cleanup failed
		at com.example.ResourceManager.cleanup(ResourceManager.java:45)
		at com.example.Main.main(Main.java:8)
	Suppressed: java.sql.SQLException: Connection close failed  
		at com.example.DatabaseManager.close(DatabaseManager.java:67)
		at com.example.Main.main(Main.java:9)"""

STACK_WITH_THREAD_DUMP = """Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
	at java.util.Arrays.copyOf(Arrays.java:3210)
	at java.util.ArrayList.grow(ArrayList.java:267)
	at com.example.MemoryHog.consumeMemory(MemoryHog.java:15)

Thread Dump:
"main" #1 prio=5 os_prio=0 tid=0x00007f8b4c00a800 nid=0x1234 runnable [0x00007f8b55321000]
   java.lang.Thread.State: RUNNABLE
	at com.example.MemoryHog.consumeMemory(MemoryHog.java:15)
	at com.example.Main.main(Main.java:10)

"GC task thread#0 (ParallelGC)" os_prio=0 tid=0x00007f8b4c01f000 nid=0x1235 runnable

"GC task thread#1 (ParallelGC)" os_prio=0 tid=0x00007f8b4c021000 nid=0x1236 runnable"""

# Test/Mock Data Examples (should be detected)
MOCK_DATA_STACK = """Exception: flux capacitor destabilized 
   at com.acme.rocket.NuclearReactor.meltdown(NuclearReactor.java:999)
   at com.acme.rocket.RocketShip.explode(RocketShip.java:42)
   at com.acme.test.ChaosMonkey.wreckHavoc(ChaosMonkey.java:1)"""

HUMOROUS_STACK = """FatalError: Coffee machine is empty
   at com.developer.productivity.CoffeeService.brewCoffee(CoffeeService.java:404)
   at com.developer.workflow.MorningRoutine.startDay(MorningRoutine.java:1)
   at com.developer.lifecycle.Developer.beProductive(Developer.java:0)"""

# Regular log messages (should NOT be detected as stack traces)
REGULAR_LOG_MESSAGES = """2024-10-01 10:00:00 INFO Starting application
2024-10-01 10:00:01 DEBUG Connecting to database
2024-10-01 10:00:02 WARN Database connection slow (2.5s)
2024-10-01 10:00:03 ERROR Failed to process user request: Invalid input
2024-10-01 10:00:04 INFO Application started successfully"""

NGINX_ACCESS_LOG = """192.168.1.100 - - [01/Oct/2024:10:00:00 +0000] "GET /api/users/123 HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [01/Oct/2024:10:00:01 +0000] "POST /api/login HTTP/1.1" 401 89 "-" "curl/7.68.0"
192.168.1.102 - - [01/Oct/2024:10:00:02 +0000] "GET /api/products HTTP/1.1" 500 512 "-" "APIClient/1.0"""

SIMPLE_ERROR_MESSAGE = "Error: User not found"

# Test Data Categories
STACK_TRACE_SAMPLES = {
    "java": {
        "simple": JAVA_SIMPLE_NPE,
        "complex": JAVA_COMPLEX_MULTI_CAUSE,
        "concurrent": JAVA_CONCURRENT_MODIFICATION,
        "spring": JAVA_SPRING_BOOT_ERROR,
        "suppressed": STACK_WITH_SUPPRESSED,
        "thread_dump": STACK_WITH_THREAD_DUMP,
        "very_long": VERY_LONG_STACK_TRACE
    },
    "python": {
        "simple": PYTHON_SIMPLE_INDEX_ERROR,
        "complex": PYTHON_COMPLEX_CHAIN,
        "import_error": PYTHON_IMPORT_ERROR,
        "type_error": PYTHON_TYPE_ERROR
    },
    "csharp": {
        "null_reference": CSHARP_NULL_REFERENCE,
        "argument": CSHARP_ARGUMENT_EXCEPTION,
        "async": CSHARP_ASYNC_EXCEPTION
    },
    "javascript": {
        "type_error": JAVASCRIPT_TYPE_ERROR,
        "reference_error": JAVASCRIPT_REFERENCE_ERROR,
        "async": JAVASCRIPT_ASYNC_ERROR,
        "module": JAVASCRIPT_NODE_MODULE_ERROR
    },
    "mixed": {
        "kotlin_java": MIXED_LANGUAGE_STACK
    },
    "mock_data": {
        "flux_capacitor": MOCK_DATA_STACK,
        "coffee": HUMOROUS_STACK
    }
}

NON_STACK_TRACE_SAMPLES = {
    "regular_logs": REGULAR_LOG_MESSAGES,
    "access_logs": NGINX_ACCESS_LOG,
    "simple_error": SIMPLE_ERROR_MESSAGE
}

# Expected outcomes for testing
EXPECTED_OUTCOMES = {
    JAVA_SIMPLE_NPE: {
        "language": "java",
        "is_stack_trace": True,
        "exception_count": 1,
        "main_exception": "NullPointerException",
        "tags_should_contain": ["Java Error", "Stack Trace", "Critical Error"],
        "tags_should_not_contain": ["Test/Mock Data"]
    },
    JAVA_COMPLEX_MULTI_CAUSE: {
        "language": "java", 
        "is_stack_trace": True,
        "exception_count": 3,
        "main_exception": "NullReferenceException",
        "tags_should_contain": ["Java Error", "Stack Trace", "Critical Error", "Test/Mock Data", "Thread Safety Issue"],
        "should_have_sections": ["🚨 **Main Problem**", "📋 **What Happened**", "🔍 **Key Code Locations**", "💡 **Suggested Actions**"]
    },
    PYTHON_SIMPLE_INDEX_ERROR: {
        "language": "python",
        "is_stack_trace": True,
        "exception_count": 1,
        "main_exception": "IndexError",
        "tags_should_contain": ["Python", "IndexError", "Stack Trace"],
        "suggestions_should_contain": ["check the length", "bounds"]
    },
    REGULAR_LOG_MESSAGES: {
        "language": "text",
        "is_stack_trace": False,
        "exception_count": 0
    }
}