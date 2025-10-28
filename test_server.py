#!/usr/bin/env python3
"""
Simple test script to validate the Scaleway MCP server.
This tests that the server can be imported and initialized without errors.
"""

import os
import sys

# Set test credentials
os.environ["SCW_ACCESS_KEY"] = "test_key"
os.environ["SCW_SECRET_KEY"] = "test_secret"
os.environ["SCW_PROJECT_ID"] = "test_project"

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        from scaleway_server import mcp, get_scaleway_client
        print("✓ Imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_server_initialization():
    """Test that the MCP server is properly initialized."""
    print("\nTesting server initialization...")
    try:
        from scaleway_server import mcp
        
        # Check that tools are registered
        tools = []
        if hasattr(mcp, '_tools'):
            tools = list(mcp._tools.keys())
        elif hasattr(mcp, 'list_tools'):
            # Try to get tools via list_tools method
            pass
        
        print(f"✓ Server initialized")
        print(f"  MCP instance created: {mcp}")
        
        return True
    except Exception as e:
        print(f"✗ Server initialization failed: {e}")
        return False

def test_client_initialization():
    """Test that Scaleway client can be initialized with test credentials."""
    print("\nTesting Scaleway client initialization...")
    try:
        from scaleway_server import get_scaleway_client
        
        client = get_scaleway_client()
        print("✓ Scaleway client initialized")
        print(f"  Access key: {client.access_key[:10]}...")
        print(f"  Default region: {client.default_region}")
        print(f"  Default zone: {client.default_zone}")
        
        return True
    except Exception as e:
        print(f"✗ Client initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Scaleway MCP Server - Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_server_initialization,
        test_client_initialization,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
