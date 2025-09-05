#!/usr/bin/env python3
"""
SpaceCracker V2 - Module Test Script
Test the enhanced GGB, Git, and JS scanner modules
"""

import asyncio
from spacecracker.modules.ggb_scanner import GGBScanner
from spacecracker.modules.git_scanner import GitScanner  
from spacecracker.modules.js_scanner import JSScanner


async def test_ggb_scanner():
    """Test the enhanced GGB scanner"""
    print("Testing GGB Scanner...")
    scanner = GGBScanner()
    
    # Test with a GitHub repository URL
    test_url = "https://github.com/octocat/Hello-World"
    result = await scanner.run(test_url, None, {})
    
    print(f"GGB Scanner Results for {test_url}:")
    print(f"  Findings: {len(result['findings'])}")
    print(f"  Errors: {len(result['errors'])}")
    
    for finding in result['findings'][:3]:  # Show first 3 findings
        print(f"  - {finding['title']} ({finding['severity']})")
    
    print()


async def test_git_scanner():
    """Test the enhanced Git scanner"""
    print("Testing Git Scanner...")
    scanner = GitScanner()
    
    # Test with a URL that might have exposed .git
    test_url = "https://example.com"
    result = await scanner.run(test_url, None, {})
    
    print(f"Git Scanner Results for {test_url}:")
    print(f"  Findings: {len(result['findings'])}")
    print(f"  Errors: {len(result['errors'])}")
    
    for finding in result['findings'][:3]:  # Show first 3 findings
        print(f"  - {finding['title']} ({finding['severity']})")
    
    print()


async def test_js_scanner():
    """Test the enhanced JS scanner"""
    print("Testing JavaScript Scanner...")
    scanner = JSScanner()
    
    # Test with a website that has JavaScript
    test_url = "https://example.com"
    result = await scanner.run(test_url, None, {})
    
    print(f"JS Scanner Results for {test_url}:")
    print(f"  Findings: {len(result['findings'])}")
    print(f"  Errors: {len(result['errors'])}")
    
    for finding in result['findings'][:3]:  # Show first 3 findings
        print(f"  - {finding['title']} ({finding['severity']})")
    
    print()


async def main():
    """Run all module tests"""
    print("SpaceCracker V2 - Enhanced Module Testing")
    print("=" * 50)
    
    try:
        await test_ggb_scanner()
        await test_git_scanner()
        await test_js_scanner()
        
        print("All module tests completed successfully!")
        
    except Exception as e:
        print(f"Test error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())