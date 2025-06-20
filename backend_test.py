
import requests
import sys
import time
import json
from datetime import datetime

class IslamAppAPITester:
    def __init__(self, base_url="https://3ce10c44-8cb6-4d17-a211-5a46485f7d39.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.token = None
        self.user_type = None
        self.user_info = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
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
            "Get Course Reports",
            "GET",
            "admin/reports/courses",
            200
        )
        return success, response

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
        "teacher_id": "1",  # Will be updated if we have real teachers
        "teacher_name": "Тестовый преподаватель",
        "difficulty": "Легко",
        "duration_minutes": 30,
        "questions_count": 10,
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

def main():
    # Run basic API tests
    basic_success = test_basic_api()
    
    # Run admin API tests
    admin_success = test_admin_api()
    
    # Overall result
    overall_success = basic_success and admin_success
    print(f"\n=== Overall Test Result: {'✅ PASSED' if overall_success else '❌ FAILED'} ===")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
