#!/usr/bin/env python3
"""
Test the interactive wizard functionality
"""
import subprocess
import sys

def test_interactive_dry_run():
    """Test interactive mode with automated input"""
    
    # Prepare input for wizard
    input_sequence = [
        'y',  # Authorization consent
        'simple_test.txt',  # Target file
        '1',  # Select first module (js_scanner)
        '1',  # 1 thread
        '1',  # 1 req/s
        'n',  # No telegram
        'n'   # Don't proceed (dry run effect)
    ]
    
    try:
        # Run the interactive wizard
        proc = subprocess.Popen(
            [sys.executable, 'launch.py', '--interactive'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        
        # Provide input
        input_text = '\n'.join(input_sequence) + '\n'
        stdout, stderr = proc.communicate(input=input_text)
        
        print("Interactive wizard test output:")
        print(stdout)
        
        if stderr:
            print("Errors:")
            print(stderr)
            
        return proc.returncode
        
    except subprocess.TimeoutExpired:
        print("Interactive test timed out")
        return 1
    except Exception as e:
        print(f"Test failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = test_interactive_dry_run()
    print(f"\nInteractive test {'PASSED' if exit_code == 0 else 'FAILED'}")
    sys.exit(exit_code)