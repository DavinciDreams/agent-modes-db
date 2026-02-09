"""
Test markdown parsing when there are no tools or skills sections.
"""

from parsers import MarkdownParser

# Test 1: Markdown without tools or skills section
markdown_no_tools = """---
name: Test Agent
description: A test agent without tools
---

# Test Agent

This is a test agent to verify that parsing works correctly when there are no tools or skills sections.

## Instructions

You are a helpful AI assistant.
"""

# Test 2: Markdown with only tools section
markdown_with_tools = """---
name: Test Agent With Tools
description: A test agent with tools
---

# Test Agent With Tools

## Instructions

You are a helpful AI assistant.

## Tools

- Read
- Write
- Bash
"""

# Test 3: Markdown with only skills section
markdown_with_skills = """---
name: Test Agent With Skills
description: A test agent with skills
---

# Test Agent With Skills

## Instructions

You are a helpful AI assistant.

## Skills

- coding
- debugging
"""

def test_markdown_parsing():
    parser = MarkdownParser()

    print("=" * 60)
    print("TEST 1: Markdown WITHOUT tools or skills")
    print("=" * 60)
    data1 = parser.parse(markdown_no_tools)
    print(f"Name: {data1.get('name')}")
    print(f"Description: {data1.get('description')}")
    print(f"Tools: {data1.get('tools')}")  # Should be empty list []
    print(f"Skills: {data1.get('skills')}")  # Should be empty list []

    assert 'tools' in data1, "Missing 'tools' key in parsed data"
    assert 'skills' in data1, "Missing 'skills' key in parsed data"
    assert data1['tools'] == [], f"Expected empty tools list, got: {data1['tools']}"
    assert data1['skills'] == [], f"Expected empty skills list, got: {data1['skills']}"
    print("[PASS] TEST 1 PASSED\n")

    print("=" * 60)
    print("TEST 2: Markdown WITH tools section")
    print("=" * 60)
    data2 = parser.parse(markdown_with_tools)
    print(f"Name: {data2.get('name')}")
    print(f"Description: {data2.get('description')}")
    print(f"Tools: {data2.get('tools')}")  # Should be ['Read', 'Write', 'Bash']
    print(f"Skills: {data2.get('skills')}")  # Should be empty list []

    assert 'tools' in data2, "Missing 'tools' key in parsed data"
    assert 'skills' in data2, "Missing 'skills' key in parsed data"
    assert len(data2['tools']) == 3, f"Expected 3 tools, got: {len(data2['tools'])}"
    assert data2['skills'] == [], f"Expected empty skills list, got: {data2['skills']}"
    print("[PASS] TEST 2 PASSED\n")

    print("=" * 60)
    print("TEST 3: Markdown WITH skills section")
    print("=" * 60)
    data3 = parser.parse(markdown_with_skills)
    print(f"Name: {data3.get('name')}")
    print(f"Description: {data3.get('description')}")
    print(f"Tools: {data3.get('tools')}")  # Should be empty list []
    print(f"Skills: {data3.get('skills')}")  # Should be ['coding', 'debugging']

    assert 'tools' in data3, "Missing 'tools' key in parsed data"
    assert 'skills' in data3, "Missing 'skills' key in parsed data"
    assert data3['tools'] == [], f"Expected empty tools list, got: {data3['tools']}"
    assert len(data3['skills']) == 2, f"Expected 2 skills, got: {len(data3['skills'])}"
    print("[PASS] TEST 3 PASSED\n")

    print("=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\nThe markdown parser now correctly handles missing tools/skills sections by setting them to empty lists.")

if __name__ == '__main__':
    test_markdown_parsing()
