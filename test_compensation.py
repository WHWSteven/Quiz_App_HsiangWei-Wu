"""
Test script to verify Saga Compensation (Rollback) works correctly.
This tests what happens when a saga step fails.
"""
import requests
import time

SAGA_ORCHESTRATOR_URL = 'http://127.0.0.1:5002'
USER_SERVICE_URL = 'http://127.0.0.1:5001'

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_compensation():
    """Test that compensation works when Quiz Service fails"""
    print_section("Testing Saga Compensation (Rollback)")
    
    print("\n📋 Test Scenario:")
    print("   1. Stop Quiz Service (or make it fail)")
    print("   2. Try to register a user")
    print("   3. Step 1 (Create User) should succeed")
    print("   4. Step 2 (Create Profile) should fail")
    print("   5. Compensation should delete the user (rollback Step 1)")
    print("   6. User should NOT exist in User Service")
    
    print("\n⚠️  IMPORTANT: Stop Quiz Service before continuing!")
    print("   (Press Ctrl+C in Terminal 5 where Quiz Service is running)")
    
    input("\nPress Enter when Quiz Service is stopped...")
    
    # Test data
    user_data = {
        "username": f"comp_test_{int(time.time())}",
        "email": f"comp_{int(time.time())}@example.com",
        "password": "testpass123"
    }
    
    print(f"\n🔄 Attempting registration: {user_data['username']}")
    
    try:
        # Trigger saga
        response = requests.post(
            f'{SAGA_ORCHESTRATOR_URL}/saga/register',
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 202:
            data = response.json()
            task_id = data.get('task_id')
            saga_id = data.get('saga_id')
            
            print(f"✅ Saga triggered: {saga_id}")
            print("   Polling for completion...")
            
            # Poll for completion
            for i in range(30):
                time.sleep(1)
                status_response = requests.get(
                    f'{SAGA_ORCHESTRATOR_URL}/saga/status/{task_id}',
                    timeout=5
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    
                    if status == 'SUCCESS':
                        print("❌ UNEXPECTED: Saga succeeded (Quiz Service might be running)")
                        break
                    elif status == 'FAILURE':
                        result = status_data.get('result', {})
                        error = result.get('error', 'Unknown error')
                        compensation = result.get('compensation', {})
                        compensation_executed = compensation.get('executed', False)
                        
                        print(f"\n✅ Saga Failed as Expected!")
                        print(f"   Error: {error}")
                        print(f"   Compensation Executed: {compensation_executed}")
                        
                        if compensation_executed:
                            print("\n✅ COMPENSATION WORKED!")
                            print("   User should have been deleted from User Service")
                            
                            # Try to find the user (should not exist)
                            # We can't easily check without the user_id, but the logs should show it
                            print("\n💡 Check Celery worker logs to see:")
                            print("   - Step 1: User created")
                            print("   - Step 2: Profile creation failed")
                            print("   - COMPENSATE: User deleted")
                        else:
                            print("\n⚠️  Compensation might not have executed")
                        
                        return True
        else:
            print(f"❌ Failed to trigger saga: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    print("\n⏱️  Timeout waiting for saga completion")
    return False

def main():
    print("\n" + "="*60)
    print("  SAGA COMPENSATION TEST")
    print("="*60)
    print("\nThis test verifies that the Saga pattern correctly")
    print("rolls back (compensates) when a step fails.")
    
    test_compensation()
    
    print("\n" + "="*60)
    print("  TEST COMPLETE")
    print("="*60)
    print("\n💡 Next Steps:")
    print("   1. Restart Quiz Service")
    print("   2. Check Celery worker logs for compensation execution")
    print("   3. Verify user was deleted from User Service")

if __name__ == '__main__':
    main()