"""
Main Orchestrator - Coordinates Auditor, Fixer, and Judge agents
Processes Python files through the complete refactoring pipeline
"""
import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import time

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
    retry_count = 0
    start_time = time.time()
    
    # Log file processing start
    log_experiment(
        agent_name="Orchestrator",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Starting processing of file: {file_path}",
            "output_response": f"File selected for refactoring pipeline",
            "file_path": file_path,
            "max_iterations": max_iterations
        },
        status="SUCCESS"
    )
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'─'*70}")
        print(f" Iteration {iteration}/{max_iterations}")
        print(f"{'─'*70}")
        
        # ===== STEP 1: AUDITOR ANALYZES =====
        print("\n STEP 1: Auditor analyzing code...")
        audit_result = auditor.analyze_file(file_path)
        
        if audit_result.get('error'):
            print(f" Audit failed: {audit_result.get('error')}")
            final_status = "AUDIT_FAILED"
            
            # Log audit failure
            log_experiment(
                agent_name="Orchestrator",
                model_used="N/A",
                action=ActionType.DEBUG,
                details={
                    "input_prompt": f"Audit failed for {file_path} at iteration {iteration}",
                    "output_response": f"Error: {audit_result.get('error')}",
                    "iteration": iteration,
                    "error": audit_result.get('error')
                },
                status="FAIL"
            )
            break
        
        # Check if there are issues to fix
        issues = audit_result.get('issues', [])
        total_issues = audit_result.get('summary', {}).get('total_issues', 0)
        critical_issues = audit_result.get('summary', {}).get('critical_issues', 0)
        
        print(f"📊 Found {total_issues} issues ({critical_issues} critical)")
        
        if not issues:
            print(" No issues found - code is clean!")
            final_status = "CLEAN"
            
            # Log clean code
            log_experiment(
                agent_name="Orchestrator",
                model_used="N/A",
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": f"Audit completed for {file_path} at iteration {iteration}",
                    "output_response": "Code is clean - no issues found",
                    "iteration": iteration,
                    "total_issues": 0
                },
                status="SUCCESS"
            )
            break
        
        # ===== STEP 2: FIXER ATTEMPTS TO FIX =====
        print("\n🔧 STEP 2: Fixer attempting to fix issues...")
        fix_result = fixer.fix_file(file_path, audit_result)
        
        if fix_result.get('error'):
            print(f" Fix failed: {fix_result.get('error')}")
            final_status = "FIX_FAILED"
            
            # Log fix failure
            log_experiment(
                agent_name="Orchestrator",
                model_used="N/A",
                action=ActionType.DEBUG,
                details={
                    "input_prompt": f"Fix attempt failed for {file_path} at iteration {iteration}",
                    "output_response": f"Error: {fix_result.get('error')}",
                    "iteration": iteration,
                    "error": fix_result.get('error')
                },
                status="FAIL"
            )
            break
        
        action_taken = fix_result.get('action')
        print(f"🛠️ Fixer action: {action_taken}")
        
        if action_taken == 'SKIP':
            reason = fix_result.get('reason', 'Unknown reason')
            print(f" Fixer skipped: {reason}")
            final_status = "SKIPPED"
            
            # Log skip decision
            log_experiment(
                agent_name="Orchestrator",
                model_used="N/A",
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": f"Fixer decided to skip {file_path} at iteration {iteration}",
                    "output_response": f"Skipped - Reason: {reason}",
                    "iteration": iteration,
                    "reason": reason
                },
                status="SUCCESS"
            )
            break
        
        if action_taken != 'FIX':
            print(f" Unexpected action: {action_taken}")
            final_status = "UNEXPECTED_ACTION"
            
            # Log unexpected action
            log_experiment(
                agent_name="Orchestrator",
                model_used="N/A",
                action=ActionType.DEBUG,
                details={
                    "input_prompt": f"Unexpected fixer action for {file_path} at iteration {iteration}",
                    "output_response": f"Unexpected action: {action_taken}",
                    "iteration": iteration,
                    "action": action_taken
                },
                status="FAIL"
            )
            break
        
        issues_fixed = fix_result.get('summary', {}).get('issues_fixed', 0)
        print(f"✓ Fixed {issues_fixed} issue(s)")
        
        # ===== STEP 3: JUDGE VALIDATES =====
        print("\n STEP 3: Judge validating the fix...")
        
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
        
        # Log test file detection
        if not test_file:
            log_experiment(
                agent_name="Orchestrator",
                model_used="N/A",
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": f"Searching for test file for {file_path}",
                    "output_response": "No test file found - validation will rely on pylint only",
                    "searched_patterns": [str(p) for p in test_patterns],
                    "iteration": iteration
                },
                status="WARNING"
            )
            print(" No test file found - relying on pylint score only")
        
        validation_result = judge.validate_file(
            file_path=file_path,
            test_file_path=test_file,
            previous_score=previous_score
        )
        
        verdict = validation_result.get('verdict', 'FAIL')
        current_score = validation_result.get('actual_pylint_score', 0.0)
        test_passed = validation_result.get('actual_test_passed')
        score_improvement = current_score - previous_score
        
        print(f" Pylint score: {current_score}/10 (previous: {previous_score}/10)")
        if score_improvement > 0:
            print(f"   ↗ Improvement: +{score_improvement:.2f}")
        elif score_improvement < 0:
            print(f"   ↘ Degradation: {score_improvement:.2f}")
        else:
            print(f"   → No change")
        
        print(f"🧪 Tests: {' PASSED' if test_passed else ' FAILED' if test_passed is False else ' N/A'}")
        print(f"⚖️ Judge verdict: {verdict}")
        
        # Log judge decision
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "input_prompt": f"Judge validation for {file_path} at iteration {iteration}",
                "output_response": f"Verdict: {verdict}, Score: {current_score}/10",
                "iteration": iteration,
                "verdict": verdict,
                "current_score": current_score,
                "previous_score": previous_score,
                "score_improvement": score_improvement,
                "test_passed": test_passed,
                "test_file": test_file
            },
            status="SUCCESS" if verdict == "PASS" else "RETRY" if verdict == "RETRY" else "FAIL"
        )
        
        previous_score = current_score
        
        # ===== DECISION LOGIC =====
        if verdict == 'PASS':
            print(f"\n SUCCESS! File successfully refactored!")
            print(f"   Final score: {current_score}/10")
            final_status = "SUCCESS"
            break
        
        elif verdict == 'FAIL':
            print(f"\n Validation failed - retrying...")
            # Continue loop to retry
            
        elif verdict == 'RETRY':
            retry_count += 1
            print(f"\n Minor issues remain - retrying... (retry #{retry_count})")
            
            # If too many retries with RETRY verdict, might indicate stuck loop
            if retry_count > 5:
                print(f" Warning: Many retries detected - may need different strategy")
                log_experiment(
                    agent_name="Orchestrator",
                    model_used="N/A",
                    action=ActionType.DEBUG,
                    details={
                        "input_prompt": f"High retry count detected for {file_path}",
                        "output_response": f"Retry count: {retry_count} - potential stuck loop",
                        "iteration": iteration,
                        "retry_count": retry_count
                    },
                    status="WARNING"
                )
        else:
            print(f"\n Unknown verdict: {verdict}")
            final_status = "UNKNOWN_VERDICT"
            
            # Log unknown verdict
            log_experiment(
                agent_name="Orchestrator",
                model_used="N/A",
                action=ActionType.DEBUG,
                details={
                    "input_prompt": f"Unknown verdict for {file_path} at iteration {iteration}",
                    "output_response": f"Unknown verdict: {verdict}",
                    "iteration": iteration,
                    "verdict": verdict
                },
                status="FAIL"
            )
            break
    
    # Check if max iterations reached
    if iteration >= max_iterations and final_status not in ["SUCCESS", "CLEAN", "SKIPPED"]:
        print(f"\n⏱ Reached maximum iterations ({max_iterations})")
        final_status = "MAX_ITERATIONS"
        
        # Log max iterations
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "input_prompt": f"Max iterations reached for {file_path}",
                "output_response": f"Stopped after {max_iterations} iterations",
                "iteration": iteration,
                "max_iterations": max_iterations,
                "final_score": previous_score
            },
            status="FAIL"
        )
    
    processing_time = time.time() - start_time
    
    # Log file processing completion
    log_experiment(
        agent_name="Orchestrator",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Completed processing of {file_path}",
            "output_response": f"Final status: {final_status}",
            "file_path": file_path,
            "final_status": final_status,
            "iterations": iteration,
            "final_score": previous_score,
            "processing_time_seconds": round(processing_time, 2)
        },
        status="SUCCESS" if final_status in ["SUCCESS", "CLEAN"] else "FAIL"
    )
    
    return {
        "file": file_path,
        "status": final_status,
        "iterations": iteration,
        "final_score": previous_score,
        "processing_time": round(processing_time, 2)
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
        help='Directory containing Python files to refactor (must be inside ./sandbox)'
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
    
    # ===== CRITICAL: SANDBOX SECURITY VALIDATION =====
    sandbox_dir = Path("./sandbox").resolve()
    target_path = Path(target_dir).resolve()
    
    # Ensure target_dir exists first
    if not target_path.exists():
        print(f" ERROR: Directory not found: {target_dir}")
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Validating target_dir: {target_dir}",
                "output_response": "REJECTED - directory does not exist",
                "attempted_path": str(target_path)
            },
            status="FAIL"
        )
        sys.exit(1)
    
    # Verify target_dir is inside sandbox (SECURITY REQUIREMENT)
    if not str(target_path).startswith(str(sandbox_dir)):
        print(f" SECURITY ERROR: target_dir must be inside ./sandbox")
        print(f"   Attempted: {target_path}")
        print(f"   Allowed:   {sandbox_dir}/*")
        print(f"\n   This restriction prevents agents from modifying files outside the sandbox.")
        
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Security validation for target_dir: {target_dir}",
                "output_response": "REJECTED - outside sandbox boundary",
                "attempted_path": str(target_path),
                "sandbox_path": str(sandbox_dir),
                "security_violation": True
            },
            status="FAIL"
        )
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f" AI CODE REFACTORING PIPELINE")
    print(f"{'='*70}")
    print(f" Target Directory: {target_dir}")
    print(f" Sandbox: {sandbox_dir}")
    print(f" Max Iterations: {max_iterations}")
    print(f"{'='*70}")
    
    # Log pipeline start
    log_experiment(
        agent_name="Orchestrator",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Starting refactoring pipeline on directory: {target_dir}",
            "output_response": "Pipeline initialized successfully",
            "target_directory": target_dir,
            "sandbox_directory": str(sandbox_dir),
            "max_iterations": max_iterations,
            "security_validated": True
        },
        status="SUCCESS"
    )
    
    # Initialize all agents
    print("\n Initializing agents...")
    try:
        auditor = AuditorAgent()
        print("   ✓ Auditor Agent initialized")
        fixer = FixerAgent()
        print("   ✓ Fixer Agent initialized")
        judge = JudgeAgent()
        print("   ✓ Judge Agent initialized")
        print(" All agents initialized successfully")
        
        # Log successful agent initialization
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "Initializing all agents (Auditor, Fixer, Judge)",
                "output_response": "All agents initialized successfully",
                "agents": ["AuditorAgent", "FixerAgent", "JudgeAgent"]
            },
            status="SUCCESS"
        )
    except Exception as e:
        print(f" Failed to initialize agents: {e}")
        
        # Log agent initialization failure
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "input_prompt": "Attempting to initialize agents",
                "output_response": f"Initialization failed: {str(e)}",
                "error": str(e)
            },
            status="FAIL"
        )
        sys.exit(1)
    
    # Find all Python files in target directory
    print(f"\n Scanning for Python files in {target_dir}...")
    python_files = list_python_files(target_dir)
    
    if not python_files:
        print(f" No Python files found in {target_dir}")
        
        # Log no files found
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Scanning directory: {target_dir}",
                "output_response": "No Python files found",
                "target_directory": target_dir
            },
            status="SUCCESS"
        )
        sys.exit(0)
    
    print(f" Found {len(python_files)} Python file(s) to process")
    
    # Log files found
    log_experiment(
        agent_name="Orchestrator",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Scanning completed for {target_dir}",
            "output_response": f"Found {len(python_files)} Python files",
            "file_count": len(python_files),
            "files": python_files
        },
        status="SUCCESS"
    )
    
    # Process each file
    results = []
    success_count = 0
    failed_count = 0
    skipped_count = 0
    total_processing_time = 0
    
    pipeline_start_time = time.time()
    
    for idx, file_path in enumerate(python_files, 1):
        print(f"\n{'#'*70}")
        print(f" File {idx}/{len(python_files)}")
        print(f"{'#'*70}")
        
        result = process_file(
            file_path=file_path,
            auditor=auditor,
            fixer=fixer,
            judge=judge,
            max_iterations=max_iterations
        )
        
        results.append(result)
        total_processing_time += result.get('processing_time', 0)
        
        # Update counters
        if result['status'] in ['SUCCESS', 'CLEAN']:
            success_count += 1
        elif result['status'] == 'SKIPPED':
            skipped_count += 1
        else:
            failed_count += 1
    
    pipeline_duration = time.time() - pipeline_start_time
    
    # Print final summary
    print(f"\n{'='*70}")
    print(f" FINAL SUMMARY")
    print(f"{'='*70}")
    print(f" Successful: {success_count}/{len(python_files)}")
    print(f" Failed: {failed_count}/{len(python_files)}")
    print(f" Skipped: {skipped_count}/{len(python_files)}")
    print(f" Total Time: {round(pipeline_duration, 2)}s")
    print(f"{'='*70}")
    
    print("\n📋 Detailed Results:")
    for result in results:
        status_icon = {
            'SUCCESS': '✅',
            'CLEAN': '✅',
            'SKIPPED': '⚠️',
        }.get(result['status'], '❌')
        
        print(f"  {status_icon} {result['file']}")
        print(f"     Status: {result['status']} | Iterations: {result['iterations']} | Score: {result['final_score']}/10 | Time: {result['processing_time']}s")
    
    print(f"\n{'='*70}")
    print(f" REFACTORING PIPELINE COMPLETE!")
    print(f" Check logs/experiment_data.json for detailed experiment data")
    print(f"{'='*70}\n")
    
    # Log pipeline completion with comprehensive metrics
    log_experiment(
        agent_name="Orchestrator",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Pipeline completed for directory: {target_dir}",
            "output_response": f"Successfully processed {len(python_files)} files",
            "total_files": len(python_files),
            "success_count": success_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "success_rate": round(success_count / len(python_files) * 100, 2) if python_files else 0,
            "total_processing_time_seconds": round(total_processing_time, 2),
            "pipeline_duration_seconds": round(pipeline_duration, 2),
            "average_time_per_file": round(pipeline_duration / len(python_files), 2) if python_files else 0,
            "results": results
        },
        status="SUCCESS"
    )


if __name__ == "__main__":
    main()