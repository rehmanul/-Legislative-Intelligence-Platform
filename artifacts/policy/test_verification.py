"""
Verification script for policy artifacts integration.
Tests dashboard display, file access, and API endpoints.
"""

import sys
from pathlib import Path

# Add parent directories to path
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "monitoring"))

def test_policy_directory():
    """Test 1: Verify policy directory exists and has files."""
    print("=" * 80)
    print("TEST 1: Policy Directory Structure")
    print("=" * 80)
    
    POLICY_DIR = BASE_DIR / "artifacts" / "policy"
    
    if not POLICY_DIR.exists():
        print("[FAIL] Policy directory does not exist")
        return False
    
    print(f"[PASS] Policy directory exists: {POLICY_DIR}")
    
    # Check for documents
    policy_files = list(POLICY_DIR.glob("*.md"))
    policy_docs = [f for f in policy_files if f.name not in [
        "README.md", "INDEX.md", "QUICK_REFERENCE.md", 
        "REVIEW_CHECKLIST.md", "IMPLEMENTATION_SUMMARY.md", 
        "COMPLETION_SUMMARY.md", "AGENT_INTEGRATION_GUIDE.md",
        "INTEGRATION_COMPLETE.md"
    ]]
    
    print(f"[PASS] Policy documents found: {len(policy_docs)}")
    for doc in sorted(policy_docs)[:5]:
        print(f"   - {doc.name}")
    if len(policy_docs) > 5:
        print(f"   ... and {len(policy_docs) - 5} more")
    
    # Check for diagrams
    DIAGRAMS_DIR = POLICY_DIR / "diagrams"
    if DIAGRAMS_DIR.exists():
        diagrams = list(DIAGRAMS_DIR.glob("*.mmd"))
        print(f"[PASS] Policy diagrams found: {len(diagrams)}")
    else:
        print("[WARN] Diagrams directory not found")
    
    # Check for viewer
    viewer = POLICY_DIR / "viewer.html"
    if viewer.exists():
        print(f"[PASS] HTML viewer exists: {viewer.name}")
    else:
        print("[FAIL] HTML viewer not found")
        return False
    
    print()
    return True


def test_dashboard_integration():
    """Test 2: Verify dashboard can access policy artifacts."""
    print("=" * 80)
    print("TEST 2: Dashboard Integration")
    print("=" * 80)
    
    try:
        from monitoring.constants import BASE_DIR as MONITORING_BASE_DIR
        
        POLICY_DIR = MONITORING_BASE_DIR / "artifacts" / "policy"
        
        if not POLICY_DIR.exists():
            print("[FAIL] Dashboard cannot find policy directory")
            return False
        
        policy_files = list(POLICY_DIR.glob("*.md"))
        policy_docs = [f for f in policy_files if f.name not in [
            "README.md", "INDEX.md", "QUICK_REFERENCE.md", 
            "REVIEW_CHECKLIST.md", "IMPLEMENTATION_SUMMARY.md", 
            "COMPLETION_SUMMARY.md", "AGENT_INTEGRATION_GUIDE.md"
        ]]
        
        print(f"[PASS] Dashboard can access policy directory")
        print(f"[PASS] Dashboard finds {len(policy_docs)} policy documents")
        print()
        return True
        
    except Exception as e:
        print(f"[FAIL] Dashboard integration test error: {e}")
        print()
        return False


def test_viewer_file():
    """Test 3: Verify HTML viewer file is valid."""
    print("=" * 80)
    print("TEST 3: HTML Viewer File")
    print("=" * 80)
    
    viewer_path = BASE_DIR / "artifacts" / "policy" / "viewer.html"
    
    if not viewer_path.exists():
        print("[FAIL] viewer.html does not exist")
        return False
    
    content = viewer_path.read_text(encoding='utf-8')
    
    # Check for key elements
    checks = [
        ("DOCTYPE html", "HTML5 doctype"),
        ("Policy Artifacts Viewer", "Title"),
        ("READ-ONLY CONTEXT", "Status warning"),
        ("mermaid", "Mermaid library"),
        ("documents-list", "Documents container"),
        ("diagrams-list", "Diagrams container"),
    ]
    
    all_passed = True
    for check_str, check_name in checks:
        if check_str in content:
            print(f"[PASS] {check_name} found")
        else:
            print(f"[FAIL] {check_name} missing")
            all_passed = False
    
    print()
    return all_passed


def test_launch_script():
    """Test 4: Verify launch script exists."""
    print("=" * 80)
    print("TEST 4: Launch Script")
    print("=" * 80)
    
    launch_script = BASE_DIR / "artifacts" / "policy" / "LAUNCH_VIEWER.bat"
    
    if not launch_script.exists():
        print("[FAIL] LAUNCH_VIEWER.bat does not exist")
        return False
    
    content = launch_script.read_text(encoding='utf-8')
    
    if "viewer.html" in content:
        print("[PASS] Launch script references viewer.html")
    else:
        print("[FAIL] Launch script missing viewer.html reference")
        return False
    
    print(f"[PASS] Launch script exists: {launch_script.name}")
    print()
    return True


def test_api_routes():
    """Test 5: Verify API routes file exists."""
    print("=" * 80)
    print("TEST 5: API Routes")
    print("=" * 80)
    
    api_routes = BASE_DIR / "app" / "policy_routes.py"
    
    if not api_routes.exists():
        print("[FAIL] policy_routes.py does not exist")
        return False
    
    content = api_routes.read_text(encoding='utf-8')
    
    # Check for key endpoints
    endpoints = [
        ("/policy-artifacts", "List endpoint"),
        ("/policy-artifacts/{name}", "Get artifact endpoint"),
        ("/policy-artifacts/diagrams", "Diagrams endpoint"),
        ("/policy-artifacts/health", "Health endpoint"),
    ]
    
    all_passed = True
    for endpoint, desc in endpoints:
        if endpoint in content:
            print(f"[PASS] {desc} found")
        else:
            print(f"[FAIL] {desc} missing")
            all_passed = False
    
    # Check main.py integration
    main_py = BASE_DIR / "app" / "main.py"
    if main_py.exists():
        main_content = main_py.read_text(encoding='utf-8')
        if "policy_router" in main_content:
            print("[PASS] API routes integrated in main.py")
        else:
            print("[WARN] API routes not yet integrated in main.py")
            all_passed = False
    
    print()
    return all_passed


def main():
    """Run all verification tests."""
    print("\n" + "=" * 80)
    print("POLICY ARTIFACTS INTEGRATION VERIFICATION")
    print("=" * 80)
    print()
    
    tests = [
        ("Policy Directory", test_policy_directory),
        ("Dashboard Integration", test_dashboard_integration),
        ("HTML Viewer", test_viewer_file),
        ("Launch Script", test_launch_script),
        ("API Routes", test_api_routes),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[FAIL] {test_name} raised exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All verification tests passed!")
        return 0
    else:
        print(f"\n[WARN] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
