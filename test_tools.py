#!/usr/bin/env python3
"""
Test script for enhanced_code_agent tool parsing
"""

import sys
from pathlib import Path

# Import the agent
from enhanced_code_agent import EnhancedCodeAgent

def test_parse_args():
    """Test the argument parsing function"""
    agent = EnhancedCodeAgent()

    print("Testing argument parsing...")
    print("=" * 50)

    # Test 1: Simple single argument
    test1 = "main.py"
    result1 = agent._parse_args(test1)
    print(f"Test 1 (single arg): {test1}")
    print(f"  Result: {result1}")
    assert result1 == ("main.py",), f"Expected ('main.py',), got {result1}"
    print("  ✓ PASSED\n")

    # Test 2: Two simple arguments
    test2 = '"test.txt", "Hello world"'
    result2 = agent._parse_args(test2)
    print(f"Test 2 (two args): {test2}")
    print(f"  Result: {result2}")
    assert result2 == ("test.txt", "Hello world"), f"Expected ('test.txt', 'Hello world'), got {result2}"
    print("  ✓ PASSED\n")

    # Test 3: Content with commas
    test3 = '"config.py", "x = 1, y = 2, z = 3"'
    result3 = agent._parse_args(test3)
    print(f"Test 3 (content with commas): {test3}")
    print(f"  Result: {result3}")
    assert result3 == ("config.py", "x = 1, y = 2, z = 3"), f"Expected ('config.py', 'x = 1, y = 2, z = 3'), got {result3}"
    print("  ✓ PASSED\n")

    # Test 4: Multi-line content
    test4 = '"app.py", "def hello():\\n    print(\'Hi\')\\n    return True"'
    result4 = agent._parse_args(test4)
    print(f"Test 4 (multi-line): {test4}")
    print(f"  Result: {result4}")
    assert result4 == ("app.py", "def hello():\\n    print('Hi')\\n    return True"), f"Expected multi-line content, got {result4}"
    print("  ✓ PASSED\n")

    # Test 5: Three arguments for edit_file
    test5 = '"test.py", "old text", "new text"'
    result5 = agent._parse_args(test5)
    print(f"Test 5 (three args): {test5}")
    print(f"  Result: {result5}")
    assert result5 == ("test.py", "old text", "new text"), f"Expected three args, got {result5}"
    print("  ✓ PASSED\n")

    print("=" * 50)
    print("All parsing tests passed! ✓\n")

def test_extract_tool_calls():
    """Test tool call extraction from response"""
    agent = EnhancedCodeAgent()

    print("Testing tool call extraction...")
    print("=" * 50)

    # Test 1: Single tool call
    response1 = "Let me read that file for you.\n\nTOOL[read_file](main.py)\n\nNow let me analyze it."
    calls1 = agent._extract_tool_calls(response1)
    print(f"Test 1: Single tool call")
    print(f"  Result: {calls1}")
    assert len(calls1) == 1, f"Expected 1 call, got {len(calls1)}"
    assert calls1[0]['tool'] == 'read_file', f"Expected 'read_file', got {calls1[0]['tool']}"
    print("  ✓ PASSED\n")

    # Test 2: Tool call with quoted content
    response2 = 'I\'ll create the file.\n\nTOOL[write_file]("test.txt", "Hello, world!")\n\nDone!'
    calls2 = agent._extract_tool_calls(response2)
    print(f"Test 2: Tool call with quotes")
    print(f"  Result: {calls2}")
    assert len(calls2) == 1, f"Expected 1 call, got {len(calls2)}"
    print("  ✓ PASSED\n")

    # Test 3: Multiple tool calls
    response3 = """Let me help with that.

TOOL[read_file](config.py)

Now I'll update it.

TOOL[edit_file]("config.py", "DEBUG = False", "DEBUG = True")

All done!"""
    calls3 = agent._extract_tool_calls(response3)
    print(f"Test 3: Multiple tool calls")
    print(f"  Result: Found {len(calls3)} calls")
    assert len(calls3) == 2, f"Expected 2 calls, got {len(calls3)}"
    print("  ✓ PASSED\n")

    print("=" * 50)
    print("All extraction tests passed! ✓\n")

def test_write_and_edit():
    """Test actual write and edit operations"""
    agent = EnhancedCodeAgent()

    print("Testing actual file operations...")
    print("=" * 50)

    # Test write_file
    test_file = Path("test_output.txt")
    test_content = "Hello, World!\nThis is a test.\nWith multiple lines."

    print("Test: write_file")
    result = agent._write_file(str(test_file), test_content)
    print(f"  Result: {result}")

    # Verify file was created
    assert test_file.exists(), "File was not created"
    actual_content = test_file.read_text()
    assert actual_content == test_content, f"Content mismatch"
    print("  ✓ PASSED\n")

    # Test edit_file
    print("Test: edit_file")
    result = agent._edit_file(str(test_file), "multiple lines", "many lines")
    print(f"  Result: {result}")

    # Verify edit was made
    edited_content = test_file.read_text()
    assert "many lines" in edited_content, "Edit was not applied"
    assert "multiple lines" not in edited_content, "Old text still present"
    print("  ✓ PASSED\n")

    # Clean up
    test_file.unlink()
    print("Test file cleaned up.")

    print("=" * 50)
    print("All file operation tests passed! ✓\n")

if __name__ == "__main__":
    try:
        test_parse_args()
        test_extract_tool_calls()
        test_write_and_edit()

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED! ✓✓✓")
        print("=" * 50)
        print("\nThe write_file and edit_file tools are working correctly!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
