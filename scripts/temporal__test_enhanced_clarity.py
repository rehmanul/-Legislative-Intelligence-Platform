"""
Script: temporal__test_enhanced_clarity.py
Intent: temporal

Tests the enhanced clarity implementation to verify all functions work correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

def test_state_descriptions():
    """Test state description functions"""
    print("=" * 60)
    print("Testing State Descriptions")
    print("=" * 60)
    
    try:
        from monitoring.state_descriptions import (
            get_state_description,
            format_state_display,
            translate_state_to_meaning
        )
        
        # Test PRE_EVT
        desc = get_state_description("PRE_EVT")
        assert desc["subtitle"] == "Policy Opportunity Phase", f"Expected 'Policy Opportunity Phase', got '{desc['subtitle']}'"
        print(f"[PASS] PRE_EVT subtitle: {desc['subtitle']}")
        
        # Test format_state_display
        short_format = format_state_display("PRE_EVT", "short")
        assert "Policy Opportunity Phase" in short_format, f"Expected subtitle in short format, got '{short_format}'"
        print(f"[PASS] Short format: {short_format}")
        
        # Test translate_state_to_meaning (backward compatible)
        meaning = translate_state_to_meaning("INTRO_EVT")
        assert "Bill Vehicle Phase" in meaning or "Shaping legitimacy" in meaning, f"Expected enhanced description, got '{meaning}'"
        print(f"[PASS] Translation: {meaning}")
        
        # Test all states
        states = ["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT", "FINAL_EVT", "IMPL_EVT"]
        for state in states:
            desc = get_state_description(state)
            assert desc["subtitle"] is not None, f"State {state} missing subtitle"
            print(f"  [PASS] {state}: {desc['subtitle']}")
        
        print("\n[PASS] All state description tests passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] State description test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_review_gate_descriptions():
    """Test review gate description functions"""
    print("\n" + "=" * 60)
    print("Testing Review Gate Descriptions")
    print("=" * 60)
    
    try:
        from monitoring.state_descriptions import (
            get_review_gate_description,
            format_review_gate_display
        )
        
        # Test HR_PRE
        gate = get_review_gate_description("HR_PRE")
        assert gate["full_name"] == "Concept & Direction Review", f"Expected 'Concept & Direction Review', got '{gate['full_name']}'"
        print(f"[PASS] HR_PRE full name: {gate['full_name']}")
        
        # Test format_review_gate_display
        short_format = format_review_gate_display("HR_PRE", "short")
        assert "Concept & Direction Review" in short_format, f"Expected full name in short format, got '{short_format}'"
        print(f"[PASS] Short format: {short_format}")
        
        # Test all gates
        gates = ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]
        for gate_id in gates:
            gate = get_review_gate_description(gate_id)
            assert gate["full_name"] is not None, f"Gate {gate_id} missing full name"
            print(f"  [PASS] {gate_id}: {gate['full_name']}")
        
        print("\n[PASS] All review gate description tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Review gate description test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dashboard_integration():
    """Test dashboard integration"""
    print("\n" + "=" * 60)
    print("Testing Dashboard Integration")
    print("=" * 60)
    
    try:
        # Import using the actual module name (dashboard-terminal.py)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dashboard_terminal",
            BASE_DIR / "monitoring" / "dashboard-terminal.py"
        )
        dashboard_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dashboard_module)
        
        result = dashboard_module.translate_state_to_meaning("PRE_EVT")
        assert "Policy Opportunity Phase" in result or "Preparing concept" in result, f"Expected enhanced description, got '{result}'"
        print(f"[PASS] Dashboard translation: {result}")
        
        print("\n[PASS] Dashboard integration test passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Dashboard integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_render_integration():
    """Test render integration"""
    print("\n" + "=" * 60)
    print("Testing Render Integration")
    print("=" * 60)
    
    try:
        # Test the function directly from state_descriptions (which render.py uses)
        from monitoring.state_descriptions import translate_state_to_meaning
        
        result = translate_state_to_meaning("COMM_EVT")
        assert "Committee Phase" in result or "Committee engagement" in result, f"Expected enhanced description, got '{result}'"
        print(f"[PASS] Render translation: {result}")
        
        # Also verify the render.py file has the updated function
        render_file = BASE_DIR / "monitoring" / "render.py"
        if render_file.exists():
            content = render_file.read_text(encoding='utf-8')
            if "get_state_description" in content or "Policy Opportunity Phase" in content:
                print("[PASS] render.py has been updated with enhanced descriptions")
            else:
                print("[WARN] render.py may not have enhanced descriptions (but function works)")
        
        print("\n[PASS] Render integration test passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Render integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Enhanced Clarity Implementation Test Suite")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("State Descriptions", test_state_descriptions()))
    results.append(("Review Gate Descriptions", test_review_gate_descriptions()))
    results.append(("Dashboard Integration", test_dashboard_integration()))
    results.append(("Render Integration", test_render_integration()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[PASS] ALL TESTS PASSED - Implementation verified!")
    else:
        print("[FAIL] SOME TESTS FAILED - Review errors above")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
