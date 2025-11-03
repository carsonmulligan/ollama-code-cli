#!/usr/bin/env python3
"""
Standalone test for parsing logic without dependencies
"""

import re

def parse_args(args_str: str) -> tuple:
    """Parse tool arguments with improved handling for complex content"""
    args = []
    current_arg = ""
    in_quotes = False
    quote_char = None
    paren_depth = 0
    i = 0

    while i < len(args_str):
        char = args_str[i]

        # Handle escape sequences - preserve them as-is including the backslash
        if char == '\\' and i + 1 < len(args_str) and in_quotes:
            # Keep escape sequences intact
            current_arg += char
            i += 1
            if i < len(args_str):
                current_arg += args_str[i]
            i += 1
            continue

        # Handle quotes
        if char in ['"', "'"] and paren_depth == 0:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
            else:
                current_arg += char
            i += 1
            continue

        # Track parentheses depth
        if not in_quotes:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1

        # Split on comma only if not in quotes and at depth 0
        if char == ',' and not in_quotes and paren_depth == 0:
            args.append(current_arg.strip())
            current_arg = ""
        else:
            current_arg += char

        i += 1

    # Add final argument
    if current_arg.strip():
        args.append(current_arg.strip())

    return tuple(args)

def extract_tool_calls(text: str) -> list:
    """Extract tool calls from agent response"""
    # Pattern: TOOL[tool_name](args)
    # Find all TOOL[ positions first, then parse each one
    tool_calls = []
    pattern = r'TOOL\[(\w+)\]'

    # Find all TOOL[name] occurrences
    for match in re.finditer(pattern, text):
        tool_name = match.group(1)
        start_pos = match.end()  # Position after TOOL[name]

        # Find the matching parentheses
        if start_pos < len(text) and text[start_pos] == '(':
            # Count parentheses to find the closing one
            paren_count = 0
            in_quotes = False
            quote_char = None
            end_pos = start_pos

            for i in range(start_pos, len(text)):
                char = text[i]

                # Handle quotes
                if char in ['"', "'"] and (i == 0 or text[i-1] != '\\'):
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None

                # Count parentheses only outside quotes
                if not in_quotes:
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                        if paren_count == 0:
                            end_pos = i
                            break

            # Extract the arguments
            if end_pos > start_pos:
                args_str = text[start_pos+1:end_pos]  # +1 to skip opening (
                tool_calls.append({
                    'tool': tool_name,
                    'args': args_str.strip()
                })

    return tool_calls

def test_all():
    print("Testing Argument Parsing...")
    print("=" * 60)

    tests = [
        ("main.py", ("main.py",), "Single argument"),
        ('"test.txt", "Hello world"', ("test.txt", "Hello world"), "Two simple arguments"),
        ('"config.py", "x = 1, y = 2, z = 3"', ("config.py", "x = 1, y = 2, z = 3"), "Content with commas"),
        ('"app.py", "def hello():\\n    print(\'Hi\')"', ("app.py", "def hello():\\n    print('Hi')"), "Multi-line content"),
        ('"test.py", "old text", "new text"', ("test.py", "old text", "new text"), "Three arguments"),
        ('"file.js", "const x = {a: 1, b: 2};"', ("file.js", "const x = {a: 1, b: 2};"), "Object with commas"),
    ]

    passed = 0
    failed = 0

    for test_input, expected, description in tests:
        result = parse_args(test_input)
        if result == expected:
            print(f"✓ {description}")
            print(f"  Input: {test_input[:60]}...")
            print(f"  Got: {result}")
            passed += 1
        else:
            print(f"✗ {description}")
            print(f"  Input: {test_input}")
            print(f"  Expected: {expected}")
            print(f"  Got: {result}")
            failed += 1
        print()

    print("=" * 60)
    print("\nTesting Tool Call Extraction...")
    print("=" * 60)

    extraction_tests = [
        ('Let me read that.\n\nTOOL[read_file](main.py)\n\nNow analyzing...', 1, "Single tool call"),
        ('TOOL[write_file]("test.txt", "Hello!")', 1, "Tool with quoted args"),
        ('First:\nTOOL[read_file](a.py)\nThen:\nTOOL[edit_file]("a.py", "old", "new")', 2, "Multiple tools"),
    ]

    for test_input, expected_count, description in extraction_tests:
        calls = extract_tool_calls(test_input)
        if len(calls) == expected_count:
            print(f"✓ {description}")
            print(f"  Found {len(calls)} call(s)")
            for call in calls:
                print(f"    - {call['tool']}: {call['args'][:50]}...")
            passed += 1
        else:
            print(f"✗ {description}")
            print(f"  Expected {expected_count} calls, got {len(calls)}")
            failed += 1
        print()

    print("=" * 60)
    print(f"\nResults: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("\nThe parsing logic is working correctly!")
        return True
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        return False

if __name__ == "__main__":
    import sys
    success = test_all()
    sys.exit(0 if success else 1)
