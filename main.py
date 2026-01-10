"""
Main Orchestrator - Coordinates Auditor, Fixer, and Judge agents
Processes Python files through the complete refactoring pipeline
"""
import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Import agents
from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
from src.agents.judge import JudgeAgent

# Import tools
from src.tools.file_tools import list_python_files

# Import logger
from src.utils.logger import log_experiment, ActionType

# Load environment variables
load_dotenv()


def process_file(file_path: str, auditor: AuditorAgent, fixer: FixerAgent, judge: JudgeAgent, max_iterations: int = 10) -> dict:
    """
    Process a single Python file through the refactoring pipeline
    
    Args:
        file_path: Path to the Python file to process
        auditor: AuditorAgent instance
        fixer: FixerAgent instance
        judge: JudgeAgent instance
        max_iterations: Maximum number of fix-validate cycles
        
    Returns:
        Dictionary with processing results
    """
    print(f"\n{'='*70}")
    print(f"📄 PROCESSING: {file_path}")
    print(f"{'='*70}")
    
    iteration = 0
    previous_score = 0.0
    final_status = "UNKNOWN"
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'─'*70}")
        print(f"🔄 Iteration {iteration}/{max_iterations}")
        print(f"{'─'*70}")
        
        # ===== STEP 1: AUDITOR ANALYZES =====
        print("\n🔍 STEP 1: Auditor analyzing code...")
        audit_result = auditor.analyze_file(file_path)
        
        if audit_result.get('error'):
            print(f"❌ Audit failed: {audit_result.get('error')}")
            final_status = "AUDIT_FAILED"
            break
        
        # Check if there are issues to fix
        issues = audit_result.get('issues', [])
        total_issues = audit_result.get('summary', {}).get('total_issues', 0)
        critical_issues = audit_result.get('summary', {}).get('critical_issues', 0)
        
        print(f"📊 Found {total_issues} issues ({critical_issues} critical)")
        
        if not issues:
            print("✅ No issues found - code is clean!")
            final_status = "CLEAN"
            break
        
        # ===== STEP 2: FIXER ATTEMPTS TO FIX =====
        print("\n🔧 STEP 2: Fixer attempting to fix issues...")
        fix_result = fixer.fix_file(file_path, audit_result)
        
        if fix_result.get('error'):
            print(f"❌ Fix failed: {fix_result.get('error')}")
            final_status = "FIX_FAILED"
            break
        
        action_taken = fix_result.get('action')
        print(f"🎯 Fixer action: {action_taken}")
        
        if action_taken == 'SKIP':
            reason = fix_result.get('reason', 'Unknown reason')
            print(f"⚠️ Fixer skipped: {reason}")
            final_status = "SKIPPED"
            break
        
        if action_taken != 'FIX':
            print(f"⚠️ Unexpected action: {action_taken}")
            final_status = "UNEXPECTED_ACTION"
            break
        
        issues_fixed = fix_result.get('summary', {}).get('issues_fixed', 0)
        print(f"✓ Fixed {issues_fixed} issue(s)")
        
        # ===== STEP 3: JUDGE VALIDATES =====
        print("\n⚖️ STEP 3: Judge validating the fix...")
        
        # Look for test file (same name with test_ prefix or _test suffix)
        file_dir = Path(file_path).parent
        file_name = Path(file_path).stem
        
        # Common test file patterns
        test_patterns = [
            file_dir / f"test_{file_name}.py",
            file_dir / f"{file_name}_test.py",
            file_dir / "tests" / f"test_{file_name}.py",
        ]
        
        test_file = None
        for pattern in test_patterns:
            if pattern.exists():
                test_file = str(pattern)
                break
        
        validation_result = judge.validate_file(
            file_path=file_path,
            test_file_path=test_file,
            previous_score=previous_score
        )
        
        verdict = validation_result.get('verdict', 'FAIL')
        current_score = validation_result.get('actual_pylint_score', 0.0)
        test_passed = validation_result.get('actual_test_passed')
        
        print(f"📊 Pylint score: {current_score}/10 (previous: {previous_score}/10)")
        print(f"🧪 Tests: {'PASSED' if test_passed else 'FAILED' if test_passed is False else 'N/A'}")
        print(f"⚖️ Judge verdict: {verdict}")
        
        previous_score = current_score
        
        # ===== DECISION LOGIC =====
        if verdict == 'PASS':
            print(f"\n🎉 SUCCESS! File successfully refactored!")
            print(f"   Final score: {current_score}/10")
            final_status = "SUCCESS"
            break
        
        elif verdict == 'FAIL':
            print(f"\n🔄 Validation failed - retrying...")
            # Continue loop to retry
            
        elif verdict == 'RETRY':
            print(f"\n🔄 Minor issues remain - retrying...")
            # Continue loop
        
        else:
            print(f"\n⚠️ Unknown verdict: {verdict}")
            final_status = "UNKNOWN_VERDICT"
            break
    
    # Check if max iterations reached
    if iteration >= max_iterations and final_status not in ["SUCCESS", "CLEAN", "SKIPPED"]:
        print(f"\n⚠️ Reached maximum iterations ({max_iterations})")
        final_status = "MAX_ITERATIONS"
    
    return {
        "file": file_path,
        "status": final_status,
        "iterations": iteration,
        "final_score": previous_score
    }


def main():
    """
    Main orchestrator function - coordinates the entire refactoring pipeline
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='AI-powered code refactoring system using multi-agent collaboration'
    )
    parser.add_argument(
        '--target_dir',
        type=str,
        required=True,
        help='Directory containing Python files to refactor'
    )
    parser.add_argument(
        '--max_iterations',
        type=int,
        default=10,
        help='Maximum iterations per file (default: 10)'
    )
    args = parser.parse_args()
    
    target_dir = args.target_dir
    max_iterations = args.max_iterations
    
    # Validate target directory exists
    if not os.path.exists(target_dir):
        print(f"❌ Directory not found: {target_dir}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"🚀 AI CODE REFACTORING PIPELINE")
    print(f"{'='*70}")
    print(f"📁 Target Directory: {target_dir}")
    print(f"🔄 Max Iterations: {max_iterations}")
    print(f"{'='*70}")
    
    # Log pipeline start
    log_experiment(
        agent_name="Orchestrator",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Starting pipeline on directory: {target_dir}",
            "output_response": "Pipeline initialized",
            "target_directory": target_dir,
            "max_iterations": max_iterations
        },
        status="SUCCESS"
    )
    
    # Initialize all agents
    print("\n🤖 Initializing agents...")
    try:
        auditor = AuditorAgent()
        fixer = FixerAgent()
        judge = JudgeAgent()
        print("✅ All agents initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agents: {e}")
        sys.exit(1)
    
    # Find all Python files in target directory
    print(f"\n🔍 Scanning for Python files in {target_dir}...")
    python_files = list_python_files(target_dir)
    
    if not python_files:
        print(f"⚠️ No Python files found in {target_dir}")
        sys.exit(0)
    
    print(f"📋 Found {len(python_files)} Python file(s) to process")
    
    # Process each file
    results = []
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for idx, file_path in enumerate(python_files, 1):
        print(f"\n{'#'*70}")
        print(f"📌 File {idx}/{len(python_files)}")
        print(f"{'#'*70}")
        
        result = process_file(
            file_path=file_path,
            auditor=auditor,
            fixer=fixer,
            judge=judge,
            max_iterations=max_iterations
        )
        
        results.append(result)
        
        # Update counters
        if result['status'] in ['SUCCESS', 'CLEAN']:
            success_count += 1
        elif result['status'] == 'SKIPPED':
            skipped_count += 1
        else:
            failed_count += 1
    
    # Print final summary
    print(f"\n{'='*70}")
    print(f"📊 FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Successful: {success_count}/{len(python_files)}")
    print(f"❌ Failed: {failed_count}/{len(python_files)}")
    print(f"⚠️ Skipped: {skipped_count}/{len(python_files)}")
    print(f"{'='*70}")
    
    print("\n📄 Detailed Results:")
    for result in results:
        status_icon = {
            'SUCCESS': '✅',
            'CLEAN': '✅',
            'SKIPPED': '⚠️',
        }.get(result['status'], '❌')
        
        print(f"  {status_icon} {result['file']}")
        print(f"     Status: {result['status']} | Iterations: {result['iterations']} | Score: {result['final_score']}/10")
    
    print(f"\n{'='*70}")
    print(f"✅ REFACTORING PIPELINE COMPLETE!")
    print(f"📊 Check logs/experiment_data.json for detailed experiment data")
    print(f"{'='*70}\n")
    
    # Log pipeline completion
    log_experiment(
        agent_name="Orchestrator",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Pipeline completed for directory: {target_dir}",
            "output_response": f"Processed {len(python_files)} files",
            "total_files": len(python_files),
            "success_count": success_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "results": results
        },
        status="SUCCESS"
    )


if __name__ == "__main__":
    main()