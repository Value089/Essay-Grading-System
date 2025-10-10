#!/usr/bin/env python3
"""
Test script to verify the essay grading system is working correctly
"""

import requests
import json

def test_backend():
    """Test backend API endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    print("Testing Essay Grading System Backend...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health Check: {data['status']}")
            print(f"✓ Models Loaded: {data['models_loaded']}")
        else:
            print(f"✗ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to backend: {e}")
        return False
    
    # Test grading endpoint
    test_essay = """
    Technology has revolutionized the way we communicate and learn. In today's digital age, 
    students have access to vast amounts of information at their fingertips. Online learning 
    platforms have made education more accessible than ever before. However, this technological 
    advancement also brings challenges such as digital divide and the need for digital literacy.
    
    The impact of technology on education is profound. Interactive learning tools, virtual 
    classrooms, and educational apps have transformed traditional teaching methods. Teachers 
    can now use multimedia presentations, online quizzes, and collaborative platforms to 
    engage students more effectively.
    
    Despite these benefits, we must also consider the potential drawbacks. Excessive screen 
    time can affect students' health, and the lack of face-to-face interaction may impact 
    social skills development. Therefore, it is crucial to find a balance between traditional 
    and digital learning methods.
    
    In conclusion, while technology has greatly enhanced educational opportunities, we must 
    use it wisely and ensure that it complements rather than replaces human interaction in 
    the learning process.
    """
    
    try:
        payload = {
            "essay": test_essay.strip(),
            "essay_set": 1
        }
        
        response = requests.post(
            f"{base_url}/api/grade",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Essay Grading Test Successful!")
            print(f"  Score: {data['score']}/{data['maxScore']}")
            print(f"  Word Count: {data['features']['word_count']}")
            print(f"  Sentences: {data['features']['sentence_count']}")
            print(f"  Vocabulary Level: {data['feedback']['vocabulary']}")
            
            if data['feedback']['strengths']:
                print(f"  Strengths: {len(data['feedback']['strengths'])} identified")
            if data['feedback']['improvements']:
                print(f"  Improvements: {len(data['feedback']['improvements'])} suggested")
                
            return True
        else:
            print(f"✗ Grading Test Failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Grading Test Error: {e}")
        return False

if __name__ == "__main__":
    success = test_backend()
    
    if success:
        print("\n" + "=" * 50)
        print("✓ All tests passed! The system is working correctly.")
        print("\nTo use the system:")
        print("1. Keep the backend running: python backend/app.py")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print("\n" + "=" * 50)
        print("✗ Tests failed. Please check the backend server.")
        print("\nTo start the backend:")
        print("1. cd backend")
        print("2. python app.py")