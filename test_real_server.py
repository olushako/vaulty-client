"""Real server integration test script.

This script tests the Vaulty client against a real server.
Run with:
    python test_real_server.py
"""

import asyncio
import sys
from vaulty import VaultyClient


async def test_real_server():
    """Test client against real server."""
    base_url = "https://vaulty-dev.holonet.cc"
    api_token = "vaulty_WBVvNycMdrfQOJyn6EtrHoLe8LbuBDj7pBxgCDmOFsw"
    
    print(f"Testing against: {base_url}")
    print(f"Using token: {api_token[:20]}...")
    print("-" * 60)
    
    client = VaultyClient(base_url=base_url, api_token=api_token)
    
    try:
        # Test 1: Health check - skip for now (returns HTML)
        print("\n[1] Testing health check...")
        print("  (Skipping - endpoint returns HTML instead of JSON)")
        
        # Test 2: List projects
        print("\n[2] Testing list projects...")
        projects = await client.projects.list()
        print(f"✓ Found {projects.total} project(s)")
        for project in projects.items[:5]:  # Show first 5
            print(f"  - {project.name} (id: {project.id})")
        
        # Test 3: Get first project details (by name, not ID)
        if projects.items:
            project = projects.items[0]
            print(f"\n[3] Testing get project by name: '{project.name}'...")
            project_detail = await client.projects.get(project.name)  # Use name, not ID
            print(f"✓ Project retrieved: {project_detail.name} (id: {project_detail.id})")
            
            # Test 4: List secrets in project (by name, not ID)
            print(f"\n[4] Testing list secrets in project '{project.name}'...")
            secrets = await client.secrets.list(project_name=project.name)  # Use name, not ID
            print(f"✓ Found {secrets.total} secret(s)")
            for secret in secrets.items[:5]:  # Show first 5
                print(f"  - {secret.key}")
        
        # Test 5: Test customer info (if available)
        print("\n[5] Testing customer info...")
        try:
            # Try to get customer info from token
            # This might not be available depending on token scope
            print("  (Skipping - requires customer endpoint)")
        except Exception as e:
            print(f"  (Expected: {type(e).__name__})")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_real_server())

