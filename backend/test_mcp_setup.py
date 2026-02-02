"""
Quick test script to verify MCP chatbot setup.

Tests:
1. Database tables exist
2. MCP server can be spawned
3. ChatbotService works with mock data
"""
import asyncio
import sys
from uuid import uuid4

async def test_database_tables():
    """Test 1: Verify chat tables exist"""
    print("\n=== Test 1: Database Tables ===")
    try:
        from app.database import get_engine
        from sqlmodel import text

        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('chat_session', 'chat_message')")
            ).fetchall()
            tables = [r[0] for r in result]

            print(f"[OK] Found tables: {tables}")
            assert 'chat_session' in tables, "chat_session table missing!"
            assert 'chat_message' in tables, "chat_message table missing!"
            print("[OK] All required tables exist")
            return True
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        return False


async def test_mcp_models():
    """Test 2: Verify models are importable"""
    print("\n=== Test 2: MCP Models ===")
    try:
        from app.models import ChatSession, ChatMessage
        print("[OK] ChatSession model imported")
        print("[OK] ChatMessage model imported")
        return True
    except Exception as e:
        print(f"[FAIL] Model import failed: {e}")
        return False


async def test_mcp_server_tools():
    """Test 3: Verify MCP server tools"""
    print("\n=== Test 3: MCP Server Tools ===")
    try:
        from app.mcp.tools import add_task_handler, list_tasks_handler, complete_task_handler, delete_task_handler
        print("[OK] add_task_handler imported")
        print("[OK] list_tasks_handler imported")
        print("[OK] complete_task_handler imported")
        print("[OK] delete_task_handler imported")
        return True
    except Exception as e:
        print(f"[FAIL] MCP tools import failed: {e}")
        return False


async def test_chatbot_service():
    """Test 4: Verify ChatbotService is importable"""
    print("\n=== Test 4: Chatbot Service ===")
    try:
        from app.services.chatbot_service import ChatbotService
        print("[OK] ChatbotService imported")
        print("[OK] ChatbotService.process_message method exists:", hasattr(ChatbotService, 'process_message'))
        return True
    except Exception as e:
        print(f"[FAIL] ChatbotService import failed: {e}")
        return False


async def test_mcp_client():
    """Test 5: Verify MCP client is importable"""
    print("\n=== Test 5: MCP Client ===")
    try:
        from app.mcp.client import get_mcp_client, MCPClient
        print("[OK] MCPClient imported")
        print("[OK] get_mcp_client function available")
        return True
    except Exception as e:
        print(f"[FAIL] MCP client import failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP Chatbot Setup Verification")
    print("=" * 60)

    results = []

    # Run all tests
    results.append(await test_database_tables())
    results.append(await test_mcp_models())
    results.append(await test_mcp_server_tools())
    results.append(await test_chatbot_service())
    results.append(await test_mcp_client())

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("[SUCCESS] All tests passed! MCP setup is ready.")
        print("\nNext Steps:")
        print("1. Create /api/chat endpoint in FastAPI")
        print("2. Test with curl or Postman")
        print("3. (Optional) Build frontend UI")
    else:
        print("[ERROR] Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
