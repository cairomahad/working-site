#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Протестировать созданный урок "Как правильно совершать намаз" со следующими компонентами:

  1. **Основной урок:**
     - ID: 9a7c2518-da14-49f6-ad25-7d89b152dc65
     - Курс: "Очищение и молитва" (ID: 947f1ddb-5e52-4605-810a-9db25d94ba79)
     - Тип: mixed (с видео и текстом)
     - YouTube видео: https://www.youtube.com/embed/T4auGhmeBlw

  2. **Тест к уроку:**
     - ID: 42665711-d8a7-41ae-80e8-a14eaf526ad2
     - 10 вопросов по теме намаза
     - Время: 15 минут, проходной балл 70%

  3. **Приложение:**
     - Текстовый конспект намаза (namaz_konspekt.txt)

  **Тестируемые эндпоинты:**
  - GET /api/lessons/{lesson_id} - получение урока
  - GET /api/lessons/{lesson_id}/tests - тесты к уроку  
  - GET /api/courses/{course_id}/lessons - все уроки курса
  - POST /api/tests/{test_id}/start-session - начало теста (проверить рандомизацию)
  - GET /api/admin/lessons/{lesson_id} - админский просмотр урока

  **Проверить:**
  - Урок отображается корректно
  - Видео URL работает
  - Тест связан с уроком
  - Система рандомизации вопросов функционирует
  - Файл-приложение доступен
  - Админские функции работают

  Используй админские данные: username=admin, password=admin123

backend:
  - task: "Enhanced Test Import System"
    implemented: true
    working: true
    file: "server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Starting implementation of JSON/CSV test import with random selection"
      - working: true
        agent: "main"
        comment: "Implemented JSON/CSV test import API at /admin/tests/import"
      - working: true
        agent: "testing"
        comment: "Verified that the test import API is working correctly. Successfully tested the endpoint."

  - task: "Random Question Selection API"
    implemented: true
    working: false
    file: "server.py"
    stuck_count: 1
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Need to implement random selection of 10 questions from available pool"
      - working: true
        agent: "main"
        comment: "Implemented /tests/{test_id}/start-session with random selection of 10 questions"
      - working: false
        agent: "testing"
        comment: "The API returns a 400 error with message 'Test has no questions'. The test exists but doesn't have any questions added to it. Need to add questions to the test before testing randomization."

  - task: "Answer Shuffling System"
    implemented: true
    working: false
    file: "server.py"
    stuck_count: 1
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implement answer shuffling for each test attempt"
      - working: true
        agent: "main"
        comment: "Implemented answer shuffling with Fisher-Yates algorithm in test sessions"
      - working: false
        agent: "testing"
        comment: "Cannot verify answer shuffling because the test has no questions. Need to add questions to the test first."

  - task: "Enhanced File Upload"
    implemented: true
    working: true
    file: "server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Improve file upload for larger PDF/DOCX files"
      - working: true
        agent: "main"
        comment: "Implemented enhanced file upload with chunked reading and larger size limits"
      - working: true
        agent: "testing"
        comment: "Verified that file upload is working. The lesson has a text attachment (namaz_konspekt.txt) that was successfully uploaded and is accessible."

  - task: "Admin Lesson View API"
    implemented: false
    working: false
    file: "server.py"
    stuck_count: 1
    priority: "high"
    needs_retesting: false
    status_history:
      - working: false
        agent: "testing"
        comment: "The GET /api/admin/lessons/{lesson_id} endpoint returns a 405 Method Not Allowed error. This endpoint needs to be implemented."

frontend:
  - task: "Admin Test Import Interface"
    implemented: true
    working: true
    file: "MaterialUploadPanel.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Create interface for importing tests from JSON/CSV"
      - working: true
        agent: "main"
        comment: "Created MaterialUploadPanel with drag&drop test import interface"

  - task: "Student Lesson Interface"
    implemented: false
    working: "NA"
    file: "LessonView.js"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Create lesson interface matching islam.school design"

  - task: "Enhanced Admin Upload Interface"
    implemented: true
    working: true
    file: "MaterialUploadPanel.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: true
        agent: "main"
        comment: "Created comprehensive upload interface with drag&drop, YouTube integration, document upload, and batch operations"

  - task: "Fix AdminProvider Context Error"
    implemented: true
    working: true
    file: "AdminLessonsTests.js, AdminComponents.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: false
        agent: "main"
        comment: "ERROR: useAdmin must be used within AdminProvider - context conflict"
      - working: true
        agent: "main"
        comment: "FIXED: Replaced all useAdmin with useCompleteAdmin in AdminLessonsTests.js and AdminComponents.js"

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Random Question Selection API"
    - "Answer Shuffling System"
    - "Admin Lesson View API"
  stuck_tasks:
    - "Random Question Selection API"
    - "Answer Shuffling System"
    - "Admin Lesson View API"
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Starting backend implementation for advanced test management system with random question selection and answer shuffling"
  - agent: "main"
    message: "Backend Phase 1 COMPLETED: All major API endpoints implemented - test import, random selection, shuffling, enhanced file upload. Ready for backend testing."
  - agent: "main"
    message: "Frontend Phase 1 COMPLETED: Created MaterialUploadPanel with drag&drop interface for YouTube videos, PDF/DOCX documents, JSON/CSV test import, and batch operations. Added new 'Загрузка материалов' section to admin panel."
  - agent: "main"
    message: "CRITICAL BUG FIXED: Resolved useAdmin context conflict by replacing all useAdmin hooks with useCompleteAdmin in AdminLessonsTests.js and AdminComponents.js. Admin panel should now work without errors."
  - agent: "testing"
    message: "Backend testing completed. Found issues with the Random Question Selection API, Answer Shuffling System, and Admin Lesson View API. The test has no questions, so we can't verify randomization or shuffling. The admin lesson view endpoint is not implemented (405 Method Not Allowed). The lesson itself and file upload are working correctly."