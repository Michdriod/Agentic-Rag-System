import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


async def test_system():
    """Test script to verify the system works end-to-end"""
    from agents.supervisor_instance import supervisor
    
    try:
        print("Testing system initialization...")
        await supervisor.initialize()
        
        test_query = "What are my spending patterns?"
        
        print(f"\nTesting suggestions endpoint with query: '{test_query}'")
        suggestions = await supervisor.get_top_suggestions(test_query)
        print("Suggestions received:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion.get('suggestion', 'N/A')} (confidence: {suggestion.get('confidence', 0.0):.2f})")
        
        print(f"\nTesting query endpoint with query: '{test_query}'")
        answer_result = await supervisor.answer_query(test_query)
        print("Answer received:")
        print(f"Answer: {answer_result.get('answer', 'N/A')}")
        print(f"Sources: {len(answer_result.get('sources', []))}")
        
        await supervisor.cleanup()
        print("\nSystem test completed successfully!")
        
    except Exception as e:
        print(f"System test failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_system())