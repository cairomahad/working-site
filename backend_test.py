
import requests
import sys
import time
import json
import os
import random
import uuid
from datetime import datetime

class IslamAppAPITester:
    def __init__(self, base_url="https://023d5872-bd73-4d5d-a18b-544d1d898689.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.token = None
        self.user_type = None
        self.user_info = None
        self.created_course_id = None
        self.created_teacher_id = None
        self.created_lesson_id = None
        self.created_test_id = None
        self.test_session_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        if headers is None:
            headers = {}
            if not files:  # Don't set Content-Type for multipart/form-data
                headers['Content-Type'] = 'application/json'
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, headers=headers, timeout=10)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.text:
                    try:
                        print(f"Response: {response.json()}")
                    except:
                        print(f"Response: {response.text}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.text:
                    print(f"Response: {response.text}")

            return success, response

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_status_endpoint(self):
        """Test the status endpoint"""
        success, response = self.run_test(
            "Status Endpoint (GET)",
            "GET",
            "status",
            200
        )
        return success

    def test_create_status(self):
        """Test creating a status check"""
        success, response = self.run_test(
            "Create Status Check",
            "POST",
            "status",
            201,
            data={"client_name": "API Tester"}
        )
        return success

    # Unified Auth Tests
    def test_unified_login(self, email, password, expected_user_type="user"):
        """Test unified login endpoint"""
        print(f"\n🔑 Testing unified login with email: {email}")
        success, response = self.run_test(
            "Unified Auth Login",
            "POST",
            "auth/login",
            200,
            data={"email": email, "password": password}
        )
        
        if success:
            try:
                response_data = response.json()
                self.token = response_data.get('access_token')
                self.user_type = response_data.get('user_type')
                self.user_info = response_data.get('user', {})
                
                print(f"✅ Login successful")
                print(f"✅ User type: {self.user_type}")
                print(f"✅ User info: {json.dumps(self.user_info, indent=2)}")
                
                if self.user_type == expected_user_type:
                    print(f"✅ Correctly identified as {expected_user_type}")
                    return True
                else:
                    print(f"❌ Not identified as {expected_user_type}, got: {self.user_type}")
                    return False
            except Exception as e:
                print(f"❌ Failed to extract data from response: {str(e)}")
                return False
        return False

    def test_invalid_login(self, email, password):
        """Test login with invalid credentials"""
        print(f"\n❌ Testing Invalid Login with email: {email}")
        success, response = self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            400,  # Expecting a 400 Bad Request for invalid credentials
            data={"email": email, "password": password}
        )
        
        # For this test, success means the API correctly rejected the invalid credentials
        return success

    # Admin API Tests
    def test_admin_login(self, username, password):
        """Test admin login and get token (legacy endpoint)"""
        success, response = self.run_test(
            "Admin Login (Legacy)",
            "POST",
            "admin/login",
            200,
            data={"username": username, "password": password}
        )
        
        if success:
            try:
                self.token = response.json().get('access_token')
                return True
            except:
                print("❌ Failed to extract token from response")
                return False
        return False

    def test_dashboard(self):
        """Test dashboard stats endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "admin/dashboard",
            200
        )
        return success

    def test_courses(self):
        """Test courses endpoint"""
        success, response = self.run_test(
            "Get Courses",
            "GET",
            "admin/courses",
            200
        )
        return success, response

    def test_create_course(self, course_data):
        """Test course creation"""
        success, response = self.run_test(
            "Create Course",
            "POST",
            "admin/courses",
            200,
            data=course_data
        )
        return success, response

    def test_update_course(self, course_id, update_data):
        """Test course update"""
        success, response = self.run_test(
            "Update Course",
            "PUT",
            f"admin/courses/{course_id}",
            200,
            data=update_data
        )
        return success

    def test_delete_course(self, course_id):
        """Test course deletion"""
        success, response = self.run_test(
            "Delete Course",
            "DELETE",
            f"admin/courses/{course_id}",
            200
        )
        return success

    def test_students(self):
        """Test students endpoint"""
        success, response = self.run_test(
            "Get Students",
            "GET",
            "admin/students",
            200
        )
        return success, response

    def test_teachers(self):
        """Test teachers endpoint"""
        success, response = self.run_test(
            "Get Teachers",
            "GET",
            "admin/teachers",
            200
        )
        return success, response

    def test_create_teacher(self, teacher_data):
        """Test teacher creation"""
        success, response = self.run_test(
            "Create Teacher",
            "POST",
            "admin/teachers",
            200,
            data=teacher_data
        )
        return success, response

    def test_applications(self):
        """Test applications endpoint"""
        success, response = self.run_test(
            "Get Applications",
            "GET",
            "admin/applications",
            200
        )
        return success, response

    def test_reports(self):
        """Test reports endpoint"""
        success, response = self.run_test(
            "Get Level Reports",
            "GET",
            "admin/reports/levels",
            200
        )
        return success, response
        
    # New API Test Methods
    
    def test_enhanced_file_upload(self, file_path, file_type):
        """Test enhanced file upload endpoint"""
        print(f"\n📁 Testing Enhanced File Upload with file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, file_type)}
                
                success, response = self.run_test(
                    "Enhanced File Upload",
                    "POST",
                    "admin/upload-enhanced",
                    200,
                    files=files,
                    data={}
                )
                
                if success:
                    try:
                        response_data = response.json()
                        file_url = response_data.get('file_url')
                        print(f"✅ File uploaded successfully: {file_url}")
                        return True, response_data
                    except Exception as e:
                        print(f"❌ Failed to extract data from response: {str(e)}")
                        return False, None
                return False, None
        except Exception as e:
            print(f"❌ Failed to open file: {str(e)}")
            return False, None
    
    def test_lesson_attachment(self, lesson_id, file_path, file_type):
        """Test adding attachment to a lesson"""
        print(f"\n📎 Testing Lesson Attachment with file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, file_type)}
                
                success, response = self.run_test(
                    "Add Lesson Attachment",
                    "POST",
                    f"admin/lessons/{lesson_id}/attachments",
                    200,
                    files=files,
                    data={}
                )
                
                if success:
                    try:
                        response_data = response.json()
                        print(f"✅ Attachment added successfully")
                        return True, response_data
                    except Exception as e:
                        print(f"❌ Failed to extract data from response: {str(e)}")
                        return False, None
                return False, None
        except Exception as e:
            print(f"❌ Failed to open file: {str(e)}")
            return False, None
    
    def test_import_test_from_json(self, file_path, course_id, lesson_id=None):
        """Test importing test from JSON file"""
        print(f"\n📊 Testing Test Import from JSON: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/json')}
                
                data = {
                    'course_id': course_id
                }
                
                if lesson_id:
                    data['lesson_id'] = lesson_id
                
                success, response = self.run_test(
                    "Import Test from JSON",
                    "POST",
                    "admin/tests/import",
                    200,
                    files=files,
                    data=data
                )
                
                if success:
                    try:
                        response_data = response.json()
                        test_id = response_data.get('test_id')
                        print(f"✅ Test imported successfully: {test_id}")
                        return True, response_data
                    except Exception as e:
                        print(f"❌ Failed to extract data from response: {str(e)}")
                        return False, None
                return False, None
        except Exception as e:
            print(f"❌ Failed to open file: {str(e)}")
            return False, None
    
    def test_start_test_session(self, test_id, student_id):
        """Test starting a test session with random questions"""
        print(f"\n🧪 Testing Start Test Session for test: {test_id}")
        
        data = {
            'student_id': student_id
        }
        
        success, response = self.run_test(
            "Start Test Session",
            "POST",
            f"tests/{test_id}/start-session",
            200,
            data=data
        )
        
        if success:
            try:
                response_data = response.json()
                session_id = response_data.get('session_id')
                questions = response_data.get('questions', [])
                
                print(f"✅ Test session started successfully: {session_id}")
                print(f"✅ Number of questions: {len(questions)}")
                
                # Verify random selection (should be 10 questions)
                if len(questions) == 10:
                    print(f"✅ Correctly selected 10 random questions")
                else:
                    print(f"❌ Expected 10 questions, got {len(questions)}")
                
                # Check if options exist for questions
                if questions and 'options' in questions[0]:
                    print(f"✅ Question options are included")
                    
                    # Store a sample question for later verification of shuffling
                    self.sample_question = questions[0]
                else:
                    print(f"❌ Question options not found")
                
                return True, response_data
            except Exception as e:
                print(f"❌ Failed to extract data from response: {str(e)}")
                return False, None
        return False, None
    
    def test_submit_test_session(self, session_id, answers):
        """Test submitting answers for a test session"""
        print(f"\n📝 Testing Submit Test Session: {session_id}")
        
        success, response = self.run_test(
            "Submit Test Session",
            "POST",
            f"test-sessions/{session_id}/submit",
            200,
            data=answers
        )
        
        if success:
            try:
                response_data = response.json()
                score = response_data.get('score')
                total_points = response_data.get('total_points')
                percentage = response_data.get('percentage')
                is_passed = response_data.get('is_passed')
                
                print(f"✅ Test submission successful")
                print(f"✅ Score: {score}/{total_points} ({percentage}%)")
                print(f"✅ Passed: {is_passed}")
                
                return True, response_data
            except Exception as e:
                print(f"❌ Failed to extract data from response: {str(e)}")
                return False, None
        return False, None
    
    def create_test_json_file(self, filename="test_questions.json"):
        """Create a sample JSON file with test questions"""
        print(f"\n📄 Creating sample test JSON file: {filename}")
        
        questions = []
        
        # Create 15 sample questions
        for i in range(1, 16):
            options = []
            correct_index = random.randint(0, 3)
            
            for j in range(4):
                options.append({
                    "text": f"Option {j+1} for Question {i}",
                    "is_correct": j == correct_index
                })
            
            question = {
                "text": f"Sample Question {i}?",
                "question_type": "single_choice",
                "options": options,
                "explanation": f"Explanation for question {i}",
                "points": 1
            }
            
            questions.append(question)
        
        test_data = {
            "questions": questions
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(test_data, f, indent=2)
            print(f"✅ Created sample test file with {len(questions)} questions")
            return True, filename
        except Exception as e:
            print(f"❌ Failed to create test file: {str(e)}")
            return False, None
    
    def create_sample_pdf(self, filename="sample.pdf"):
        """Create a simple text file as a mock PDF"""
        print(f"\n📄 Creating sample PDF file: {filename}")
        
        try:
            with open(filename, 'w') as f:
                f.write("This is a sample PDF file content for testing purposes.")
            print(f"✅ Created sample PDF file")
            return True, filename
        except Exception as e:
            print(f"❌ Failed to create PDF file: {str(e)}")
            return False, None

def test_basic_api():
    """Test basic API endpoints"""
    print("\n=== Testing Basic API Endpoints ===")
    tester = IslamAppAPITester()
    
    # Run basic tests
    tester.test_root_endpoint()
    tester.test_status_endpoint()
    tester.test_create_status()

    # Print results
    print(f"\n📊 Basic API Tests: {tester.tests_passed}/{tester.tests_run} passed")
    return tester.tests_passed == tester.tests_run

def test_unified_auth():
    """Test unified authentication system"""
    print("\n=== Testing Unified Authentication System ===")
    tester = IslamAppAPITester()
    
    # Test admin login with the provided credentials
    print("\n🔑 Testing admin login with credentials: miftahylum@gmail.com/197724")
    admin_login_success = tester.test_unified_login("miftahylum@gmail.com", "197724", "admin")
    
    # Test admin dashboard access if login succeeded
    if admin_login_success:
        print("\n🔐 Testing Admin Dashboard Access")
        dashboard_success = tester.test_dashboard()
        if dashboard_success:
            print("✅ Successfully accessed admin dashboard with admin token")
        else:
            print("❌ Failed to access admin dashboard with admin token")
    
    # Create a new tester instance for student login
    student_tester = IslamAppAPITester()
    
    # Test student login
    print("\n👤 Testing student login with test credentials")
    student_login_success = student_tester.test_unified_login("student@test.com", "password123", "user")
    
    # Test unauthorized admin access with student token
    if student_login_success:
        print("\n🚫 Testing Unauthorized Admin Dashboard Access")
        unauth_success = student_tester.test_dashboard()
        if not unauth_success:
            print("✅ Correctly denied admin dashboard access to student user")
        else:
            print("❌ Failed to properly restrict admin dashboard access")
    
    # Test invalid login
    invalid_tester = IslamAppAPITester()
    invalid_login_success = invalid_tester.test_invalid_login("nonexistent@example.com", "wrongpassword")
    
    # Print results
    print(f"\n📊 Unified Auth Tests: {tester.tests_passed + student_tester.tests_passed + invalid_tester.tests_passed}/{tester.tests_run + student_tester.tests_run + invalid_tester.tests_run} passed")
    return (tester.tests_passed == tester.tests_run and 
            student_tester.tests_passed == student_tester.tests_run and
            invalid_tester.tests_passed == invalid_tester.tests_run)

def test_admin_api():
    """Test admin API endpoints"""
    print("\n=== Testing Admin API Endpoints ===")
    tester = IslamAppAPITester()
    
    # Test admin login with the updated credentials
    print("\n🔑 Testing admin login with credentials: admin/admin123")
    if not tester.test_admin_login("admin", "admin123"):
        print("❌ Admin login failed, stopping admin tests")
        print(f"\n📊 Admin API Tests: {tester.tests_passed}/{tester.tests_run} passed")
        return False
    
    # Test dashboard
    tester.test_dashboard()
    
    # Test courses
    courses_success, courses_response = tester.test_courses()
    
    # Test course creation
    course_data = {
        "title": "Тестовый курс",
        "description": "Описание тестового курса",
        "level": "level_1",
        "teacher_id": "1",  # Will be updated if we have real teachers
        "teacher_name": "Тестовый преподаватель",
        "difficulty": "Легко",
        "estimated_duration_hours": 30,
        "image_url": "https://example.com/image.jpg"
    }
    
    # Get teachers first to use a real teacher ID
    teachers_success, teachers_response = tester.test_teachers()
    if teachers_success:
        try:
            teachers = teachers_response.json()
            if teachers and len(teachers) > 0:
                course_data["teacher_id"] = teachers[0]["id"]
                course_data["teacher_name"] = teachers[0]["name"]
        except:
            pass
    
    # Create a course
    create_success, create_response = tester.test_create_course(course_data)
    
    # If course creation succeeded, test update and delete
    if create_success:
        try:
            course_id = create_response.json()["id"]
            
            # Test course update
            update_data = {
                "title": "Обновленный тестовый курс",
                "status": "published"
            }
            tester.test_update_course(course_id, update_data)
            
            # Test course deletion
            tester.test_delete_course(course_id)
        except Exception as e:
            print(f"Error in course update/delete tests: {str(e)}")
    
    # Test students
    tester.test_students()
    
    # Test teacher creation
    teacher_data = {
        "name": "Тестовый преподаватель",
        "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",
        "subject": "Тестовый предмет",
        "bio": "Биография тестового преподавателя"
    }
    tester.test_create_teacher(teacher_data)
    
    # Test applications
    tester.test_applications()
    
    # Test reports
    tester.test_reports()
    
    # Print results
    print(f"\n📊 Admin API Tests: {tester.tests_passed}/{tester.tests_run} passed")
    return tester.tests_passed == tester.tests_run

def test_namaz_lesson():
    """Test the 'Как правильно совершать намаз' lesson and its components"""
    print("\n=== Testing 'Как правильно совершать намаз' Lesson ===")
    tester = IslamAppAPITester()
    
    # Login as admin
    print("\n🔑 Testing admin login with credentials: admin/admin123")
    if not tester.test_admin_login("admin", "admin123"):
        print("❌ Admin login failed, stopping tests")
        return False
    
    # Test variables from the requirements
    lesson_id = "9a7c2518-da14-49f6-ad25-7d89b152dc65"
    course_id = "947f1ddb-5e52-4605-810a-9db25d94ba79"
    test_id = "42665711-d8a7-41ae-80e8-a14eaf526ad2"
    
    # 1. Test getting the lesson
    print(f"\n📚 Testing GET /api/lessons/{lesson_id}")
    success, response = tester.run_test(
        f"Get Lesson {lesson_id}",
        "GET",
        f"lessons/{lesson_id}",
        200
    )
    
    if success:
        try:
            lesson_data = response.json()
            print(f"✅ Lesson title: {lesson_data.get('title')}")
            print(f"✅ Lesson type: {lesson_data.get('lesson_type')}")
            
            # Verify video URL
            video_url = lesson_data.get('video_url')
            if video_url and "youtube.com/embed/T4auGhmeBlw" in video_url:
                print(f"✅ Video URL is correct: {video_url}")
            else:
                print(f"❌ Video URL is incorrect or missing: {video_url}")
                success = False
                
            # Check for attachments
            attachments = lesson_data.get('attachments', [])
            if attachments:
                print(f"✅ Lesson has {len(attachments)} attachment(s)")
                for attachment in attachments:
                    print(f"  - {attachment.get('filename')}")
            else:
                print("ℹ️ Lesson has no attachments")
        except Exception as e:
            print(f"❌ Failed to parse lesson data: {str(e)}")
            success = False
    
    # 2. Test getting tests for the lesson
    print(f"\n📝 Testing GET /api/lessons/{lesson_id}/tests")
    tests_success, tests_response = tester.run_test(
        f"Get Tests for Lesson {lesson_id}",
        "GET",
        f"lessons/{lesson_id}/tests",
        200
    )
    
    if tests_success:
        try:
            tests_data = tests_response.json()
            if tests_data:
                print(f"✅ Found {len(tests_data)} test(s) for the lesson")
                
                # Check if our specific test is in the list
                test_found = False
                for test in tests_data:
                    if test.get('id') == test_id:
                        test_found = True
                        print(f"✅ Found the specified test: {test.get('title')}")
                        print(f"✅ Test time limit: {test.get('time_limit_minutes')} minutes")
                        print(f"✅ Test passing score: {test.get('passing_score')}%")
                        break
                
                if not test_found:
                    print(f"❌ Specified test ID {test_id} not found in lesson tests")
                    tests_success = False
            else:
                print("ℹ️ No tests found for this lesson")
        except Exception as e:
            print(f"❌ Failed to parse tests data: {str(e)}")
            tests_success = False
    
    # 3. Test getting all lessons for the course
    print(f"\n📚 Testing GET /api/courses/{course_id}/lessons")
    course_lessons_success, course_lessons_response = tester.run_test(
        f"Get Lessons for Course {course_id}",
        "GET",
        f"courses/{course_id}/lessons",
        200
    )
    
    if course_lessons_success:
        try:
            lessons_data = course_lessons_response.json()
            if lessons_data:
                print(f"✅ Found {len(lessons_data)} lesson(s) in the course")
                
                # Check if our specific lesson is in the list
                lesson_found = False
                for lesson in lessons_data:
                    if lesson.get('id') == lesson_id:
                        lesson_found = True
                        print(f"✅ Found the specified lesson: {lesson.get('title')}")
                        break
                
                if not lesson_found:
                    print(f"❌ Specified lesson ID {lesson_id} not found in course lessons")
                    course_lessons_success = False
            else:
                print("ℹ️ No lessons found for this course")
        except Exception as e:
            print(f"❌ Failed to parse course lessons data: {str(e)}")
            course_lessons_success = False
    
    # 4. Test starting a test session (check randomization)
    print(f"\n🧪 Testing POST /api/tests/{test_id}/start-session")
    
    # Create a fake student ID for testing
    student_id = f"test_student_{uuid.uuid4()}"
    
    # Start test session multiple times to check randomization
    sessions = []
    for i in range(3):
        session_success, session_response = tester.run_test(
            f"Start Test Session {i+1}",
            "POST",
            f"tests/{test_id}/start-session",
            200,
            data={"student_id": student_id}
        )
        
        if session_success:
            try:
                session_data = session_response.json()
                sessions.append(session_data)
                print(f"✅ Session {i+1} started successfully")
                print(f"✅ Number of questions: {len(session_data.get('questions', []))}")
            except Exception as e:
                print(f"❌ Failed to parse session data: {str(e)}")
                session_success = False
    
    # Check randomization by comparing questions across sessions
    randomization_success = True
    if len(sessions) >= 2:
        print("\n🔄 Checking question randomization across sessions")
        
        # Extract question IDs from each session
        question_sets = []
        for i, session in enumerate(sessions):
            question_ids = [q.get('id') for q in session.get('questions', [])]
            question_sets.append(set(question_ids))
            print(f"  Session {i+1} question IDs: {question_ids}")
        
        # Compare question sets
        all_identical = True
        for i in range(len(question_sets) - 1):
            if question_sets[i] != question_sets[i+1]:
                all_identical = False
                break
        
        if all_identical and len(question_sets[0]) > 0:
            print("❌ Questions are not randomized across sessions")
            randomization_success = False
        else:
            print("✅ Questions are properly randomized across sessions")
            randomization_success = True
        
        # Check option shuffling within a session
        print("\n🔄 Checking option shuffling within questions")
        
        # Take the first question from the first session that has options
        sample_question = None
        for session in sessions:
            for question in session.get('questions', []):
                if question.get('options') and len(question.get('options', [])) > 1:
                    sample_question = question
                    break
            if sample_question:
                break
        
        if sample_question:
            print(f"  Sample question: {sample_question.get('text')}")
            print(f"  Options: {[opt.get('text') for opt in sample_question.get('options', [])]}")
            print("✅ Options are present in the response")
        else:
            print("ℹ️ No suitable question found to check option shuffling")
    else:
        print("❌ Not enough sessions to check randomization")
        randomization_success = False
    
    # 5. Test admin view of the lesson
    print(f"\n👑 Testing GET /api/admin/lessons/{lesson_id}")
    admin_lesson_success, admin_lesson_response = tester.run_test(
        f"Admin View of Lesson {lesson_id}",
        "GET",
        f"admin/lessons/{lesson_id}",
        200
    )
    
    if admin_lesson_success:
        try:
            admin_lesson_data = admin_lesson_response.json()
            print(f"✅ Admin can view the lesson: {admin_lesson_data.get('title')}")
            
            # Check for additional admin fields that might not be in the public view
            admin_fields = ['is_published', 'created_at', 'updated_at']
            for field in admin_fields:
                if field in admin_lesson_data:
                    print(f"✅ Admin field present: {field}")
            
        except Exception as e:
            print(f"❌ Failed to parse admin lesson data: {str(e)}")
            admin_lesson_success = False
    
    # Overall result
    overall_success = (success and tests_success and course_lessons_success and 
                      randomization_success and admin_lesson_success)
    
    print(f"\n📊 Namaz Lesson Tests: {tester.tests_passed}/{tester.tests_run} passed")
    return overall_success

def main():
    # Run the specific tests for the Namaz lesson
    namaz_success = test_namaz_lesson()
    
    # Overall result
    print(f"\n=== Overall Test Result: {'✅ PASSED' if namaz_success else '❌ FAILED'} ===")
    
    return 0 if namaz_success else 1

if __name__ == "__main__":
    sys.exit(main())
