#!/usr/bin/env python3
"""
Backend Testing Script for Supabase Connection Testing
Testing Supabase database connection and basic API endpoints
"""

import requests
import json
import uuid
from datetime import datetime
import sys
import os

# Get backend URL from environment
BACKEND_URL = "https://471881a1-d8ba-40f7-8bb3-c2bc817a49be.preview.emergentagent.com/api"

# Admin credentials for testing
ADMIN_EMAIL = "admin@uroki-islama.ru"
ADMIN_PASSWORD = "admin123"

class TestScoringTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_id = None
        self.test_user_id = str(uuid.uuid4())
        self.test_user_name = "Ахмед Тестовый"
        
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
    
    def find_available_test(self):
        """Find available test with questions"""
        print("\n🔍 Using test with questions...")
        
        try:
            # Use the test that we know has questions
            self.test_id = "adee81b5-028c-46df-8ba1-a83ee040b56f"  # Тест по намазу
            
            # Get test details to verify questions
            test_response = self.session.get(f"{BACKEND_URL}/tests/{self.test_id}")
            if test_response.status_code == 200:
                test_details = test_response.json()
                questions_count = len(test_details.get("questions", []))
                print(f"✅ Using test: {test_details.get('title', 'Unknown')} (ID: {self.test_id})")
                print(f"   Test has {questions_count} questions")
                
                if questions_count > 0:
                    return True
                else:
                    print("❌ Test has no questions")
                    return False
            else:
                print(f"❌ Could not get test details: {test_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error finding test: {str(e)}")
            return False
    
    def test_first_attempt_scoring(self):
        """Test first attempt scoring: should give 5 + correct answers points"""
        print("\n🎯 Testing first attempt scoring...")
        
        if not self.test_id:
            print("❌ No test ID available")
            return False
        
        try:
            # Get test details first to understand the questions
            test_response = self.session.get(f"{BACKEND_URL}/tests/{self.test_id}")
            if test_response.status_code != 200:
                print(f"❌ Could not get test details: {test_response.status_code}")
                return False
            
            test_data = test_response.json()
            questions = test_data.get("questions", [])
            
            if not questions:
                print("❌ Test has no questions")
                return False
            
            print(f"   Test has {len(questions)} questions")
            
            # Prepare answers - answer first 3 questions correctly, rest incorrectly
            answers = {}
            correct_answers = 0
            
            for i, question in enumerate(questions):
                question_id = f"q{i}"
                if i < 3:  # Answer first 3 correctly
                    answers[question_id] = question.get("correct", 0)
                    correct_answers += 1
                else:  # Answer rest incorrectly
                    # Choose wrong answer (if correct is 0, choose 1, etc.)
                    correct_option = question.get("correct", 0)
                    wrong_option = (correct_option + 1) % 4
                    answers[question_id] = wrong_option
            
            print(f"   Submitting answers with {correct_answers} correct out of {len(questions)}")
            
            # Submit test
            submission_data = {
                "user_id": self.test_user_id,
                "user_name": self.test_user_name,
                "answers": answers
            }
            
            response = self.session.post(f"{BACKEND_URL}/tests/{self.test_id}/submit", json=submission_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ First attempt submission successful")
                print(f"   Score: {result['score']}/{result['total_questions']} ({result['percentage']:.1f}%)")
                print(f"   Points earned: {result['points_earned']}")
                print(f"   Is retake: {result.get('is_retake', 'N/A')}")
                print(f"   Message: {result.get('message', 'N/A')}")
                
                # Verify scoring logic: should be 5 + correct_answers
                expected_points = 5 + correct_answers
                if result['points_earned'] == expected_points:
                    print(f"✅ Scoring logic correct: {expected_points} points (5 completion + {correct_answers} correct)")
                    return True
                else:
                    print(f"❌ Scoring logic incorrect: got {result['points_earned']}, expected {expected_points}")
                    return False
            else:
                print(f"❌ First attempt submission failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ First attempt test error: {str(e)}")
            return False
    
    def test_retake_scoring(self):
        """Test retake scoring: should give 0 points"""
        print("\n🔄 Testing retake scoring...")
        
        if not self.test_id:
            print("❌ No test ID available")
            return False
        
        try:
            # Get test details
            test_response = self.session.get(f"{BACKEND_URL}/tests/{self.test_id}")
            if test_response.status_code != 200:
                print(f"❌ Could not get test details: {test_response.status_code}")
                return False
            
            test_data = test_response.json()
            questions = test_data.get("questions", [])
            
            # Prepare different answers for retake - answer all correctly this time
            answers = {}
            for i, question in enumerate(questions):
                question_id = f"q{i}"
                answers[question_id] = question.get("correct", 0)
            
            print(f"   Submitting retake with all {len(questions)} answers correct")
            
            # Submit test again (retake)
            submission_data = {
                "user_id": self.test_user_id,
                "user_name": self.test_user_name,
                "answers": answers
            }
            
            response = self.session.post(f"{BACKEND_URL}/tests/{self.test_id}/submit", json=submission_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Retake submission successful")
                print(f"   Score: {result['score']}/{result['total_questions']} ({result['percentage']:.1f}%)")
                print(f"   Points earned: {result['points_earned']}")
                print(f"   Is retake: {result.get('is_retake', 'N/A')}")
                print(f"   Message: {result.get('message', 'N/A')}")
                
                # Verify retake logic: should be 0 points
                if result['points_earned'] == 0 and result.get('is_retake') == True:
                    print(f"✅ Retake logic correct: 0 points earned, is_retake=True")
                    return True
                else:
                    print(f"❌ Retake logic incorrect: got {result['points_earned']} points, is_retake={result.get('is_retake')}")
                    return False
            else:
                print(f"❌ Retake submission failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Retake test error: {str(e)}")
            return False
    
    def test_leaderboard_api(self):
        """Test leaderboard API to ensure points display correctly"""
        print("\n🏆 Testing leaderboard API...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/leaderboard")
            
            if response.status_code == 200:
                leaderboard = response.json()
                print(f"✅ Leaderboard API successful")
                print(f"   Found {len(leaderboard)} users on leaderboard")
                
                if leaderboard:
                    print("   Top 3 users:")
                    for i, user in enumerate(leaderboard[:3], 1):
                        print(f"   {i}. {user['user_name']}: {user['total_points']} points ({user['tests_completed']} tests)")
                    
                    # Check if our test user is in the leaderboard
                    test_user_found = False
                    for user in leaderboard:
                        if user['user_name'] == self.test_user_name:
                            test_user_found = True
                            print(f"   ✅ Test user found: {user['user_name']} with {user['total_points']} points")
                            break
                    
                    if not test_user_found:
                        print(f"   ⚠️ Test user {self.test_user_name} not found in leaderboard")
                else:
                    print("   Leaderboard is empty")
                
                return True
            else:
                print(f"❌ Leaderboard API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Leaderboard test error: {str(e)}")
            return False
    
    def test_api_response_fields(self):
        """Test that API response contains required fields"""
        print("\n📋 Testing API response fields...")
        
        if not self.test_id:
            print("❌ No test ID available")
            return False
        
        try:
            # Create a new user for this test
            new_user_id = str(uuid.uuid4())
            new_user_name = "Фатима Проверочная"
            
            # Get test details
            test_response = self.session.get(f"{BACKEND_URL}/tests/{self.test_id}")
            if test_response.status_code != 200:
                print(f"❌ Could not get test details: {test_response.status_code}")
                return False
            
            test_data = test_response.json()
            questions = test_data.get("questions", [])
            
            # Prepare answers
            answers = {}
            for i, question in enumerate(questions):
                question_id = f"q{i}"
                answers[question_id] = question.get("correct", 0)
            
            # Submit test
            submission_data = {
                "user_id": new_user_id,
                "user_name": new_user_name,
                "answers": answers
            }
            
            response = self.session.post(f"{BACKEND_URL}/tests/{self.test_id}/submit", json=submission_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API response received")
                
                # Check required fields
                required_fields = ['score', 'total_questions', 'percentage', 'points_earned', 'message', 'is_retake']
                missing_fields = []
                
                for field in required_fields:
                    if field not in result:
                        missing_fields.append(field)
                    else:
                        print(f"   ✅ {field}: {result[field]}")
                
                if not missing_fields:
                    print(f"✅ All required fields present in API response")
                    return True
                else:
                    print(f"❌ Missing fields in API response: {missing_fields}")
                    return False
            else:
                print(f"❌ API response test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API response test error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all scoring system tests"""
        print("🚀 Starting Test Scoring System Tests")
        print("=" * 60)
        
        test_results = {}
        
        # Test 1: Admin Authentication
        test_results["admin_auth"] = self.authenticate_admin()
        
        if not test_results["admin_auth"]:
            print("\n❌ Cannot proceed without admin authentication")
            return test_results
        
        # Test 2: Find Available Test
        test_results["find_test"] = self.find_available_test()
        
        if not test_results["find_test"]:
            print("\n❌ Cannot proceed without available test")
            return test_results
        
        # Test 3: First Attempt Scoring
        test_results["first_attempt"] = self.test_first_attempt_scoring()
        
        # Test 4: Retake Scoring
        test_results["retake_scoring"] = self.test_retake_scoring()
        
        # Test 5: Leaderboard API
        test_results["leaderboard"] = self.test_leaderboard_api()
        
        # Test 6: API Response Fields
        test_results["api_fields"] = self.test_api_response_fields()
        
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
            print("🎉 All tests passed! Test scoring system is working correctly.")
        elif passed >= total * 0.8:
            print("⚠️ Most tests passed. Minor issues detected.")
        else:
            print("❌ Multiple test failures. Test scoring system needs attention.")
        
        return test_results

def main():
    """Main test execution"""
    tester = TestScoringTester()
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