"""
Test script to verify all API endpoints work correctly
Run this after the server is started
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_response(response, title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def main():
    print("\n" + "="*60)
    print("TESTING FASTAPI AUTH & PROMPTS API")
    print("="*60)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    response = requests.get("http://localhost:8000/health")
    print_response(response, "Health Check")
    
    # Test 2: Signup
    print("\n2. Testing user signup...")
    signup_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/signup", json=signup_data)
    print_response(response, "User Signup")
    
    # Test 3: Login
    print("\n3. Testing user login...")
    login_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print_response(response, "User Login")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 4: Get Profile
        print("\n4. Testing get profile...")
        response = requests.get(f"{BASE_URL}/profile", headers=headers)
        print_response(response, "Get Profile")
        
        # Test 5: Create Prompt
        print("\n5. Testing create prompt...")
        prompt_data = {
            "title": "Test Prompt",
            "content": "This is a test prompt content",
            "description": "Testing prompt creation"
        }
        response = requests.post(f"{BASE_URL}/prompts/", json=prompt_data, headers=headers)
        print_response(response, "Create Prompt")
        
        if response.status_code == 201:
            prompt_id = response.json()["id"]
            
            # Test 6: Get All Prompts
            print("\n6. Testing get all prompts...")
            response = requests.get(f"{BASE_URL}/prompts/", headers=headers)
            print_response(response, "Get All Prompts")
            
            # Test 7: Get Single Prompt
            print(f"\n7. Testing get single prompt (ID: {prompt_id})...")
            response = requests.get(f"{BASE_URL}/prompts/{prompt_id}", headers=headers)
            print_response(response, "Get Single Prompt")
            
            # Test 8: Update Prompt
            print(f"\n8. Testing update prompt (ID: {prompt_id})...")
            update_data = {
                "title": "Updated Test Prompt",
                "content": "This content has been updated"
            }
            response = requests.put(f"{BASE_URL}/prompts/{prompt_id}", json=update_data, headers=headers)
            print_response(response, "Update Prompt")
            
            # Test 9: Delete Prompt
            print(f"\n9. Testing delete prompt (ID: {prompt_id})...")
            response = requests.delete(f"{BASE_URL}/prompts/{prompt_id}", headers=headers)
            print_response(response, "Delete Prompt")
            
            # Test 10: Verify Deletion
            print(f"\n10. Verifying prompt was deleted...")
            response = requests.get(f"{BASE_URL}/prompts/{prompt_id}", headers=headers)
            print_response(response, "Verify Deletion (Should be 404)")
    
    print("\n" + "="*60)
    print("TESTING COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main()
