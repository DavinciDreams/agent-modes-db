"""
Test script for format conversions.

This script tests all format conversions between Claude, Roo, and Custom formats.
"""

import json
from converters import UniversalConverter, AgentIR
from parsers import ClaudeParser, RooParser, CustomParser
from serializers import ClaudeSerializer, RooSerializer, CustomSerializer


def test_clude_to_roo():
    """Test conversion from Claude to Roo format."""
    print("\n=== Test: Claude to Roo ===")
    
    source_data = {
        'name': 'Code Analyzer',
        'description': 'Analyzes code structure and patterns',
        'capabilities': ['code-analysis', 'pattern-matching', 'security-scan'],
        'tools': ['file-read', 'regex', 'ast-parser'],
        'system_prompt': 'You are a code analyzer. Analyze the provided code structure and identify patterns.'
    }
    
    try:
        target_data, warnings = UniversalConverter.convert(
            source_data=source_data,
            source_format='claude',
            target_format='roo'
        )
        
        print("OK Conversion successful")
        print(f"Source: {source_data['name']}")
        print(f"Target: {target_data['name']}")
        print(f"Mode: {target_data.get('mode')}")
        print(f"Warnings: {warnings}")
        
        # Verify fields
        assert target_data['name'] == source_data['name'], "Name mismatch"
        assert target_data['description'] == source_data['description'], "Description mismatch"
        assert 'mode' in target_data, "Missing mode field"
        assert 'icon' in target_data, "Missing icon field"
        assert 'category' in target_data, "Missing category field"
        assert 'tags' in target_data, "Missing tags field"
        
        print("OK All assertions passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_roo_to_claude():
    """Test conversion from Roo to Claude format."""
    print("\n=== Test: Roo to Claude ===")
    
    source_data = {
        'mode': 'code-analyzer',
        'name': 'Code Analyzer',
        'description': 'Analyzes code structure and patterns',
        'category': 'development',
        'capabilities': ['code-analysis', 'pattern-matching'],
        'tools': ['file-read', 'regex'],
        'system_prompt': 'You are a code analyzer.',
        'icon': 'fa-code',
        'tags': ['code', 'analysis']
    }
    
    try:
        target_data, warnings = UniversalConverter.convert(
            source_data=source_data,
            source_format='roo',
            target_format='claude'
        )
        
        print("OK Conversion successful")
        print(f"Source: {source_data['name']}")
        print(f"Target: {target_data['name']}")
        print(f"Warnings: {warnings}")
        
        # Verify fields
        assert target_data['name'] == source_data['name'], "Name mismatch"
        assert target_data['description'] == source_data['description'], "Description mismatch"
        assert 'mode' not in target_data, "Mode field should not be present in Claude format"
        
        print("OK All assertions passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_custom_to_roo():
    """Test conversion from Custom to Roo format."""
    print("\n=== Test: Custom to Roo ===")
    
    source_data = {
        'name': 'Security Scanner',
        'description': 'Scans code for security vulnerabilities',
        'capabilities': ['security-scan', 'vulnerability-detection'],
        'tools': ['sast', 'dast'],
        'system_prompt': 'You are a security scanner.',
        'config_schema': {
            'scan_depth': 3,
            'severity_levels': ['low', 'medium', 'high', 'critical']
        }
    }
    
    try:
        target_data, warnings = UniversalConverter.convert(
            source_data=source_data,
            source_format='custom',
            target_format='roo'
        )
        
        print("OK Conversion successful")
        print(f"Source: {source_data['name']}")
        print(f"Target: {target_data['name']}")
        print(f"Warnings: {warnings}")
        
        # Verify fields
        assert target_data['name'] == source_data['name'], "Name mismatch"
        assert 'mode' in target_data, "Missing mode field"
        assert 'icon' in target_data, "Missing icon field"
        assert 'category' in target_data, "Missing category field"
        
        print("OK All assertions passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_claude_to_custom():
    """Test conversion from Claude to Custom format."""
    print("\n=== Test: Claude to Custom ===")
    
    source_data = {
        'name': 'Documentation Generator',
        'description': 'Generates documentation from code',
        'capabilities': ['doc-generation', 'markdown', 'api-docs'],
        'tools': ['file-read', 'template-engine'],
        'system_prompt': 'You are a documentation generator.'
    }
    
    try:
        target_data, warnings = UniversalConverter.convert(
            source_data=source_data,
            source_format='claude',
            target_format='custom'
        )
        
        print("OK Conversion successful")
        print(f"Source: {source_data['name']}")
        print(f"Target: {target_data['name']}")
        print(f"Warnings: {warnings}")
        
        # Verify fields
        assert target_data['name'] == source_data['name'], "Name mismatch"
        assert target_data['description'] == source_data['description'], "Description mismatch"
        assert 'capabilities' in target_data, "Missing capabilities field"
        assert 'tools' in target_data, "Missing tools field"
        assert 'system_prompt' in target_data, "Missing system_prompt field"
        
        print("OK All assertions passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_agent_ir():
    """Test AgentIR class."""
    print("\n=== Test: AgentIR ===")
    
    # Create AgentIR from dict
    ir = AgentIR.from_dict({
        'name': 'Test Agent',
        'description': 'Test description',
        'capabilities': ['cap1', 'cap2'],
        'tools': ['tool1', 'tool2'],
        'system_prompt': 'Test prompt',
        'category': 'Testing',
        'version': '2.0.0'
    })
    
    # Validate
    is_valid, errors = ir.validate()
    assert is_valid, f"Validation failed: {errors}"
    
    # Convert to dict
    ir_dict = ir.to_dict()
    assert ir_dict['name'] == 'Test Agent', "Name mismatch"
    assert ir_dict['capabilities'] == ['cap1', 'cap2'], "Capabilities mismatch"
    
    # Test merge methods
    ir.merge_capabilities(['cap3'])
    assert 'cap3' in ir.capabilities, "Merge capabilities failed"
    
    ir.merge_tools(['tool3'])
    assert 'tool3' in ir.tools, "Merge tools failed"
    
    ir.add_tag('test-tag')
    assert 'test-tag' in ir.tags, "Add tag failed"
    
    ir.set_metadata('test-key', 'test-value')
    assert ir.get_metadata('test-key') == 'test-value', "Set/get metadata failed"
    
    print("OK AgentIR tests passed")
    return True


def test_parser_validation():
    """Test parser validation."""
    print("\n=== Test: Parser Validation ===")
    
    # Test Claude parser validation
    claude_parser = ClaudeParser()
    
    # Valid data
    valid_data = {
        'name': 'Test',
        'description': 'Test description',
        'system_prompt': 'Test prompt'
    }
    is_valid, errors = claude_parser.validate(valid_data)
    assert is_valid, f"Valid data rejected: {errors}"
    
    # Invalid data (missing required fields)
    invalid_data = {'name': 'Test'}
    is_valid, errors = claude_parser.validate(invalid_data)
    assert not is_valid, "Invalid data accepted"
    assert any('description' in error for error in errors), "Missing description not detected"
    
    # Test Roo parser validation
    roo_parser = RooParser()
    
    # Valid data
    valid_roo = {
        'mode': 'test-mode',
        'name': 'Test',
        'description': 'Test description',
        'system_prompt': 'Test prompt'
    }
    is_valid, errors = roo_parser.validate(valid_roo)
    assert is_valid, f"Valid Roo data rejected: {errors}"
    
    # Invalid data (missing mode and name)
    invalid_roo = {'description': 'Test description'}
    is_valid, errors = roo_parser.validate(invalid_roo)
    assert not is_valid, "Invalid Roo data accepted"
    assert len(errors) > 0, "Expected validation errors"
    
    print("OK Parser validation tests passed")
    return True


def test_serializer_methods():
    """Test serializer methods."""
    print("\n=== Test: Serializer Methods ===")
    
    # Create test IR
    ir = AgentIR()
    ir.name = 'Test Agent'
    ir.description = 'Test description'
    ir.capabilities = ['test-cap']
    ir.tools = ['test-tool']
    ir.system_prompt = 'Test prompt'
    
    # Test Claude serializer
    claude_serializer = ClaudeSerializer()
    claude_data = claude_serializer.serialize(ir)
    assert claude_data['name'] == 'Test Agent', "Claude serialization failed"
    assert claude_data['description'] == 'Test description', "Claude serialization failed"
    
    # Test Roo serializer
    roo_serializer = RooSerializer()
    roo_data = roo_serializer.serialize(ir)
    assert roo_data['name'] == 'Test Agent', "Roo serialization failed"
    assert 'mode' in roo_data, "Roo serialization missing mode"
    assert roo_data['mode'] == 'test-agent', "Roo mode generation failed"
    
    # Test Custom serializer
    custom_serializer = CustomSerializer()
    custom_data = custom_serializer.serialize(ir)
    assert custom_data['name'] == 'Test Agent', "Custom serialization failed"
    assert 'capabilities' in custom_data, "Custom serialization missing capabilities"
    assert 'tools' in custom_data, "Custom serialization missing tools"
    
    print("OK Serializer method tests passed")
    return True


def test_universal_converter_validation():
    """Test UniversalConverter validation."""
    print("\n=== Test: UniversalConverter Validation ===")
    
    # Test valid conversion
    is_valid, errors = UniversalConverter.validate_conversion('claude', 'roo')
    assert is_valid, f"Valid conversion rejected: {errors}"
    
    # Test invalid conversion
    is_valid, errors = UniversalConverter.validate_conversion('invalid', 'roo')
    assert not is_valid, "Invalid source format accepted"
    assert 'invalid' in str(errors), "Error message incorrect"
    
    # Test same format conversion
    is_valid, errors = UniversalConverter.validate_conversion('claude', 'claude')
    assert not is_valid, "Same format conversion accepted"
    
    # Test supported formats
    formats = UniversalConverter.get_supported_formats()
    assert 'claude' in formats, "Claude format not in supported formats"
    assert 'roo' in formats, "Roo format not in supported formats"
    assert 'custom' in formats, "Custom format not in supported formats"
    
    print("OK UniversalConverter validation tests passed")
    return True


def run_all_tests():
    """Run all format conversion tests."""
    print("\n" + "="*60)
    print("FORMAT CONVERSION TESTS")
    print("="*60)
    
    tests = [
        ("Claude to Roo", test_clude_to_roo),
        ("Roo to Claude", test_roo_to_claude),
        ("Custom to Roo", test_custom_to_roo),
        ("Claude to Custom", test_claude_to_custom),
        ("AgentIR", test_agent_ir),
        ("Parser Validation", test_parser_validation),
        ("Serializer Methods", test_serializer_methods),
        ("UniversalConverter Validation", test_universal_converter_validation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "PASSED" if success else "FAILED"))
        except Exception as e:
            print(f"\n✗ {test_name} test failed with exception: {e}")
            results.append((test_name, "FAILED"))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, status in results:
        symbol = "OK" if status == "PASSED" else "FAIL"
        print(f"{symbol} {test_name}: {status}")
    
    passed = sum(1 for _, status in results if status == "PASSED")
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n*** All tests passed! ***")
        return True
    else:
        print(f"\n*** {total - passed} test(s) failed ***")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)