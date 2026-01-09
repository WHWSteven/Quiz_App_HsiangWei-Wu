"""
Simple test script for Saga Orchestration Pattern
Run this to test your saga implementation
"""
import requests
import json
import time

# Service URLs
SAGA_ORCHESTRATOR_URL = 'http://localhost:5002'
GATEWAY_URL = 'http://localhost:8080'
USER_SERVICE_URL = 'http://localhost:5001'
QUIZ_SERVICE_URL = 'http://localhost:5000'

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health_checks():
    """Test all service health endpoints"""
    print_section("Testing Health Checks")
    
    services = {
        'Saga Orchestrator': f'{SAGA_ORCHESTRATOR_URL}/health',
        'User Service': f'{USER_SERVICE_URL}/health',
        'Quiz Service': f'{QUIZ_SERVICE_URL}/api/health',
    }
    
    all_ok = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK - {response.json()}")
            else:
                print(f"❌ {name}: Failed - Status {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")
            all_ok = False
    
    return all_ok

def test_registration_saga():
    """Test the registration saga via Gateway"""
    print_section("Testing Registration Saga via Gateway")
    
    # Test data
    user_data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpass123"
    }
    
    print(f"Registering user: {user_data['username']}")
    
    try:
        response = requests.post(
            f'{GATEWAY_URL}/auth/register',
            json=user_data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Registration Successful!")
            print(f"   User ID: {data.get('user', {}).get('id')}")
            print(f"   Saga ID: {data.get('saga_id')}")
            print(f"   Token: {data.get('token', '')[:50]}...")
            
            # Verify user was created
            user_id = data.get('user', {}).get('id')
            if user_id:
                verify_user_created(user_id)
            
            return True
        else:
            print(f"❌ Registration Failed!")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def verify_user_created(user_id):
    """Verify user and profile were created"""
    print_section(f"Verifying User {user_id} Creation")
    
    # Check User Service
    try:
        response = requests.get(f'{USER_SERVICE_URL}/users/{user_id}', timeout=5)
        if response.status_code == 200:
            print(f"✅ User exists in User Service: {response.json()}")
        else:
            print(f"❌ User not found in User Service: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking User Service: {str(e)}")
    
    # Check Quiz Service Profile
    try:
        response = requests.get(f'{QUIZ_SERVICE_URL}/api/users/{user_id}/profile', timeout=5)
        if response.status_code == 200:
            print(f"✅ User profile exists in Quiz Service: {response.json()}")
        else:
            print(f"❌ User profile not found in Quiz Service: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking Quiz Service: {str(e)}")

def test_saga_directly():
    """Test saga directly via Saga Orchestrator"""
    print_section("Testing Saga Directly via Orchestrator")
    
    user_data = {
        "username": f"directtest_{int(time.time())}",
        "email": f"direct_{int(time.time())}@example.com",
        "password": "testpass123"
    }
    
    print(f"Triggering saga for: {user_data['username']}")
    
    try:
        # Trigger saga
        response = requests.post(
            f'{SAGA_ORCHESTRATOR_URL}/saga/register',
            json=user_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 202:
            data = response.json()
            print("✅ Saga Triggered Successfully!")
            print(f"   Saga ID: {data.get('saga_id')}")
            print(f"   Task ID: {data.get('task_id')}")
            
            # Poll for completion
            task_id = data.get('task_id')
            if task_id:
                print("\n   Polling for saga completion...")
                poll_saga_status(task_id)
            
            return True
        else:
            print(f"❌ Failed to trigger saga!")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def poll_saga_status(task_id, max_attempts=30):
    """Poll saga status until completion"""
    for i in range(max_attempts):
        try:
            response = requests.get(
                f'{SAGA_ORCHESTRATOR_URL}/saga/status/{task_id}',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                if status == 'SUCCESS':
                    print(f"   ✅ Saga Completed Successfully!")
                    print(f"   Result: {json.dumps(data.get('result'), indent=6)}")
                    return True
                elif status == 'FAILURE':
                    print(f"   ❌ Saga Failed!")
                    print(f"   Error: {data.get('error')}")
                    return False
                elif status == 'PENDING':
                    print(f"   ⏳ Saga still processing... (attempt {i+1}/{max_attempts})")
                    time.sleep(1)
                else:
                    print(f"   Status: {status}")
                    time.sleep(1)
            else:
                print(f"   Error checking status: {response.status_code}")
                time.sleep(1)
                
        except Exception as e:
            print(f"   Error: {str(e)}")
            time.sleep(1)
    
    print(f"   ⏱️  Timeout waiting for saga completion")
    return False

def main():
    print("\n" + "="*60)
    print("  SAGA ORCHESTRATION PATTERN - TEST SUITE")
    print("="*60)
    
    # Test 1: Health Checks
    if not test_health_checks():
        print("\n❌ Some services are not healthy. Please check your services.")
        return
    
    # Test 2: Registration via Gateway (recommended)
    print("\n")
    test_registration_saga()
    
    # Test 3: Saga directly via Orchestrator
    print("\n")
    test_saga_directly()
    
    print("\n" + "="*60)
    print("  TESTING COMPLETE")
    print("="*60)
    print("\n💡 Tips:")
    print("   - Check Celery worker logs to see saga execution")
    print("   - Check service logs for detailed information")
    print("   - If saga fails, check compensation was executed")

if __name__ == '__main__':
    main()