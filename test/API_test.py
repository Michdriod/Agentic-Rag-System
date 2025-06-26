import requests
import json
import asyncio
from typing import Dict, Any

# ===== API TESTING SCRIPT =====

BASE_URL = "http://localhost:8000"  # Adjust if your server runs on different port

def test_health_endpoint():
    """Test if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ Server is running")
            return True
        else:
            print(f"✗ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Make sure it's running on port 8000")
        return False

def test_suggestions_endpoint():
    """Test the /suggestions endpoint."""
    try:
        test_queries = [
            "I spend too much money on dining out",
            "How can I save more money?",
            "My spending is out of control",
            "Help me with my budget"
        ]
        
        print("\n=== Testing /suggestions endpoint ===")
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            
            payload = {"query": query}
            response = requests.post(
                f"{BASE_URL}/suggestions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get("suggestions", [])
                print(f"✓ Got {len(suggestions)} suggestions:")
                
                for i, suggestion in enumerate(suggestions, 1):
                    conf = suggestion.get("confidence", 0.0)
                    text = suggestion.get("suggestion", "N/A")
                    print(f"  {i}. {text} (confidence: {conf:.2f})")
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing suggestions endpoint: {e}")
        return False

def test_query_endpoint():
    """Test the /query endpoint."""
    try:
        test_queries = [
            "What should I do about my spending habits?",
            "How can I improve my financial situation?",
            "Give me advice on managing my money better",
            "What are the main issues with my finances?"
        ]
        
        print("\n=== Testing /query endpoint ===")
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            
            payload = {"query": query}
            response = requests.post(
                f"{BASE_URL}/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "N/A")
                sources = data.get("sources", [])
                
                print(f"✓ Answer received:")
                print(f"  Answer: {answer[:200]}..." if len(answer) > 200 else f"  Answer: {answer}")
                print(f"  Sources: {len(sources)} items")
                
                for i, source in enumerate(sources, 1):
                    title = source.get("title", "N/A")
                    conf = source.get("confidence", 0.0)
                    print(f"    {i}. {title[:60]}... (confidence: {conf:.2f})")
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing query endpoint: {e}")
        return False

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n=== Testing Edge Cases ===")
    
    test_cases = [
        {"query": ""},  # Empty query
        {"query": "a"},  # Very short query
        {"query": "x" * 1000},  # Very long query
        {"query": "completely unrelated random text that should not match anything in database"},  # No matches
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: {test_case['query'][:50]}...")
        
        # Test suggestions endpoint
        response = requests.post(f"{BASE_URL}/suggestions", json=test_case)
        if response.status_code == 200:
            suggestions = response.json().get("suggestions", [])
            print(f"  Suggestions: {len(suggestions)} items")
        else:
            print(f"  Suggestions error: {response.status_code}")
        
        # Test query endpoint
        response = requests.post(f"{BASE_URL}/query", json=test_case)
        if response.status_code == 200:
            answer = response.json().get("answer", "")
            print(f"  Query answer length: {len(answer)} chars")
        else:
            print(f"  Query error: {response.status_code}")

async def test_direct_system():
    """Test the system directly without API calls."""
    print("\n=== Testing System Directly ===")
    
    try:
        from agents.supervisor_instance import supervisor
        
        await supervisor.initialize()
        
        test_query = "I need help with my spending"
        
        # Test suggestions
        suggestions = await supervisor.get_top_suggestions(test_query)
        print(f"✓ Direct suggestions test: {len(suggestions)} suggestions")
        for i, s in enumerate(suggestions, 1):
            print(f"  {i}. {s.get('suggestion', 'N/A')}")
        
        # Test query
        result = await supervisor.answer_query(test_query)
        print(f"✓ Direct query test: Answer length {len(result.get('answer', ''))}")
        print(f"  Answer: {result.get('answer', 'N/A')[:100]}...")
        
        await supervisor.cleanup()
        return True
        
    except Exception as e:
        print(f"✗ Direct system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main testing function."""
    print("=== API ENDPOINT TESTING ===")
    
    # Test server connectivity
    # if not test_health_endpoint():