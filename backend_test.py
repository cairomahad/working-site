#!/usr/bin/env python3
"""
Backend Testing Script for Reorganized Admin Panel
Testing the integration of lesson management into courses panel
"""

import requests
import json
import uuid
from datetime import datetime
import sys
import os

# Get backend URL from environment
BACKEND_URL = "https://b13f8f66-31dd-42be-a080-4ea955b19065.preview.emergentagent.com/api"

# Admin credentials for testing
ADMIN_EMAIL = "admin@uroki-islama.ru"
ADMIN_PASSWORD = "admin123"

class AdminPanelTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_course_id = None
        self.test_lesson_id = None
        
    def authenticate_admin(self):
        """Test admin authentication with email/password"""
        print("🔐 Testing admin authentication...")
        
        try:
            # Test unified login endpoint
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("user_type") == "admin":
                    self.admin_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    print(f"✅ Admin authentication successful")
                    print(f"   User: {data['user']['name']} ({data['user']['email']})")
                    print(f"   Role: {data['user']['role']}")
                    return True
                else:
                    print(f"❌ Authentication failed: Not admin user")
                    return False
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_admin_courses_endpoint(self):
        """Test GET /api/admin/courses - get courses list"""
        print("\n📚 Testing admin courses endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/courses")
            
            if response.status_code == 200:
                courses = response.json()
                print(f"✅ GET /api/admin/courses successful")
                print(f"   Found {len(courses)} courses")
                
                if courses:
                    # Store first course ID for lesson testing
                    self.test_course_id = courses[0]["id"]
                    print(f"   Sample course: {courses[0]['title']} (ID: {self.test_course_id})")
                    
                    # Show course statuses
                    statuses = {}
                    for course in courses:
                        status = course.get("status", "unknown")
                        statuses[status] = statuses.get(status, 0) + 1
                    print(f"   Course statuses: {statuses}")
                
                return True
            else:
                print(f"❌ GET /api/admin/courses failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin courses endpoint error: {str(e)}")
            return False
    
    def test_course_lessons_endpoint(self):
        """Test GET /api/admin/courses/{course_id}/lessons - get course lessons"""
        print("\n📖 Testing course lessons endpoint...")
        
        if not self.test_course_id:
            print("❌ No test course ID available")
            return False
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/courses/{self.test_course_id}/lessons")
            
            if response.status_code == 200:
                lessons = response.json()
                print(f"✅ GET /api/admin/courses/{self.test_course_id}/lessons successful")
                print(f"   Found {len(lessons)} lessons in course")
                
                if lessons:
                    # Store first lesson ID for testing
                    self.test_lesson_id = lessons[0]["id"]
                    print(f"   Sample lesson: {lessons[0]['title']} (ID: {self.test_lesson_id})")
                    
                    # Show lesson types
                    types = {}
                    for lesson in lessons:
                        lesson_type = lesson.get("lesson_type", "unknown")
                        types[lesson_type] = types.get(lesson_type, 0) + 1
                    print(f"   Lesson types: {types}")
                
                return True
            else:
                print(f"❌ GET /api/admin/courses/{self.test_course_id}/lessons failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Course lessons endpoint error: {str(e)}")
            return False
    
    def test_create_lesson_endpoint(self):
        """Test POST /api/admin/lessons - create new lesson"""
        print("\n➕ Testing create lesson endpoint...")
        
        if not self.test_course_id:
            print("❌ No test course ID available")
            return False
        
        try:
            # Create test lesson data
            lesson_data = {
                "title": f"Тестовый урок {datetime.now().strftime('%H:%M:%S')}",
                "description": "Урок создан для тестирования реорганизованной админки",
                "content": "Это тестовый контент урока для проверки интеграции управления уроками в панель курсов.",
                "course_id": self.test_course_id,
                "lesson_type": "text",
                "order": 999,
                "is_published": False,
                "video_url": "",
                "attachments": []
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/lessons", json=lesson_data)
            
            if response.status_code == 200:
                created_lesson = response.json()
                self.test_lesson_id = created_lesson["id"]
                print(f"✅ POST /api/admin/lessons successful")
                print(f"   Created lesson: {created_lesson['title']}")
                print(f"   Lesson ID: {self.test_lesson_id}")
                print(f"   Course ID: {created_lesson['course_id']}")
                return True
            else:
                print(f"❌ POST /api/admin/lessons failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Create lesson endpoint error: {str(e)}")
            return False
    
    def test_update_lesson_endpoint(self):
        """Test PUT /api/admin/lessons/{lesson_id} - edit lesson"""
        print("\n✏️ Testing update lesson endpoint...")
        
        if not self.test_lesson_id:
            print("❌ No test lesson ID available")
            return False
        
        try:
            # Update lesson data
            update_data = {
                "title": f"Обновленный тестовый урок {datetime.now().strftime('%H:%M:%S')}",
                "description": "Урок обновлен для тестирования функции редактирования",
                "content": "Обновленный контент урока. Тестируем интеграцию управления уроками в панель курсов.",
                "is_published": True
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/lessons/{self.test_lesson_id}", json=update_data)
            
            if response.status_code == 200:
                updated_lesson = response.json()
                print(f"✅ PUT /api/admin/lessons/{self.test_lesson_id} successful")
                print(f"   Updated lesson: {updated_lesson['title']}")
                print(f"   Published: {updated_lesson['is_published']}")
                print(f"   Updated at: {updated_lesson.get('updated_at', 'N/A')}")
                return True
            else:
                print(f"❌ PUT /api/admin/lessons/{self.test_lesson_id} failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Update lesson endpoint error: {str(e)}")
            return False
    
    def test_delete_lesson_endpoint(self):
        """Test DELETE /api/admin/lessons/{lesson_id} - delete lesson"""
        print("\n🗑️ Testing delete lesson endpoint...")
        
        if not self.test_lesson_id:
            print("❌ No test lesson ID available")
            return False
        
        try:
            response = self.session.delete(f"{BACKEND_URL}/admin/lessons/{self.test_lesson_id}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ DELETE /api/admin/lessons/{self.test_lesson_id} successful")
                print(f"   Message: {result.get('message', 'Lesson deleted')}")
                
                # Verify lesson is deleted by trying to get it
                verify_response = self.session.get(f"{BACKEND_URL}/admin/lessons/{self.test_lesson_id}")
                if verify_response.status_code == 404:
                    print(f"✅ Lesson deletion verified - lesson no longer exists")
                else:
                    print(f"⚠️ Lesson may still exist after deletion")
                
                return True
            else:
                print(f"❌ DELETE /api/admin/lessons/{self.test_lesson_id} failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Delete lesson endpoint error: {str(e)}")
            return False
    
    def test_lesson_course_relationship(self):
        """Test the relationship between courses and lessons"""
        print("\n🔗 Testing course-lesson relationship...")
        
        if not self.test_course_id:
            print("❌ No test course ID available")
            return False
        
        try:
            # Get course details
            course_response = self.session.get(f"{BACKEND_URL}/courses/{self.test_course_id}")
            if course_response.status_code != 200:
                print(f"❌ Could not get course details: {course_response.status_code}")
                return False
            
            course = course_response.json()
            print(f"✅ Course details retrieved: {course['title']}")
            
            # Get lessons for this course
            lessons_response = self.session.get(f"{BACKEND_URL}/admin/courses/{self.test_course_id}/lessons")
            if lessons_response.status_code != 200:
                print(f"❌ Could not get course lessons: {lessons_response.status_code}")
                return False
            
            lessons = lessons_response.json()
            print(f"✅ Course has {len(lessons)} lessons")
            
            # Verify all lessons belong to this course
            valid_relationships = 0
            for lesson in lessons:
                if lesson.get("course_id") == self.test_course_id:
                    valid_relationships += 1
                else:
                    print(f"⚠️ Lesson {lesson['id']} has incorrect course_id: {lesson.get('course_id')}")
            
            print(f"✅ {valid_relationships}/{len(lessons)} lessons have correct course relationship")
            return valid_relationships == len(lessons)
            
        except Exception as e:
            print(f"❌ Course-lesson relationship test error: {str(e)}")
            return False
    
    def test_supabase_connection(self):
        """Test Supabase connection stability"""
        print("\n🔌 Testing Supabase connection stability...")
        
        try:
            # Test multiple endpoints to verify connection
            endpoints_to_test = [
                "/admin/dashboard",
                "/courses",
                "/team",
                "/qa/stats"
            ]
            
            successful_connections = 0
            for endpoint in endpoints_to_test:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    if response.status_code in [200, 401]:  # 401 is OK for protected endpoints
                        successful_connections += 1
                        print(f"   ✅ {endpoint}: Connection OK")
                    else:
                        print(f"   ❌ {endpoint}: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ {endpoint}: {str(e)}")
            
            connection_rate = (successful_connections / len(endpoints_to_test)) * 100
            print(f"✅ Supabase connection stability: {connection_rate:.1f}% ({successful_connections}/{len(endpoints_to_test)})")
            
            return connection_rate >= 75  # Consider stable if 75%+ endpoints work
            
        except Exception as e:
            print(f"❌ Supabase connection test error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all admin panel reorganization tests"""
        print("🚀 Starting Admin Panel Reorganization Tests")
        print("=" * 60)
        
        test_results = {}
        
        # Test 1: Admin Authentication
        test_results["admin_auth"] = self.authenticate_admin()
        
        if not test_results["admin_auth"]:
            print("\n❌ Cannot proceed without admin authentication")
            return test_results
        
        # Test 2: Admin Courses Endpoint
        test_results["admin_courses"] = self.test_admin_courses_endpoint()
        
        # Test 3: Course Lessons Endpoint
        test_results["course_lessons"] = self.test_course_lessons_endpoint()
        
        # Test 4: Create Lesson
        test_results["create_lesson"] = self.test_create_lesson_endpoint()
        
        # Test 5: Update Lesson
        test_results["update_lesson"] = self.test_update_lesson_endpoint()
        
        # Test 6: Delete Lesson
        test_results["delete_lesson"] = self.test_delete_lesson_endpoint()
        
        # Test 7: Course-Lesson Relationship
        test_results["course_lesson_relationship"] = self.test_lesson_course_relationship()
        
        # Test 8: Supabase Connection
        test_results["supabase_connection"] = self.test_supabase_connection()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! Admin panel reorganization is working correctly.")
        elif passed >= total * 0.8:
            print("⚠️ Most tests passed. Minor issues detected.")
        else:
            print("❌ Multiple test failures. Admin panel reorganization needs attention.")
        
        return test_results

def main():
    """Main test execution"""
    tester = AdminPanelTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    if passed == total:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()