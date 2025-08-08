#!/usr/bin/env python3
"""
Master test runner for Neo4j MCP Server.
Runs all unit tests and provides comprehensive coverage reporting.
"""

import os
import sys
import unittest
import asyncio
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Any


class TestRunner:
    """Comprehensive test runner for Neo4j MCP Server."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests"
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def discover_tests(self) -> List[str]:
        """Discover all test files in the tests directory."""
        test_files = []
        
        if not self.tests_dir.exists():
            print(f"❌ Tests directory not found: {self.tests_dir}")
            return test_files
        
        for test_file in self.tests_dir.glob("test_*.py"):
            if test_file.is_file():
                test_files.append(str(test_file))
        
        return sorted(test_files)
    
    def run_single_test_file(self, test_file: str) -> Dict[str, Any]:
        """Run a single test file and return results."""
        print(f"\n🚀 Running tests from: {os.path.basename(test_file)}")
        print("=" * 60)
        
        # Add the project root to Python path
        sys.path.insert(0, str(self.project_root))
        
        # Load and run the test
        loader = unittest.TestLoader()
        suite = loader.discover(os.path.dirname(test_file), pattern=os.path.basename(test_file))
        
        # Create a test runner
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        
        # Run the tests
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # Compile results
        test_result = {
            "file": test_file,
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
            "success": result.wasSuccessful(),
            "execution_time": end_time - start_time,
            "failures_details": result.failures,
            "errors_details": result.errors
        }
        
        # Print summary
        status = "✅ PASS" if test_result["success"] else "❌ FAIL"
        print(f"\n{status} - {os.path.basename(test_file)}")
        print(f"   Tests: {test_result['tests_run']}, "
              f"Failures: {test_result['failures']}, "
              f"Errors: {test_result['errors']}, "
              f"Time: {test_result['execution_time']:.2f}s")
        
        return test_result
    
    def run_all_tests(self) -> bool:
        """Run all discovered tests and return overall success."""
        print("🧪 Neo4j MCP Server - Comprehensive Test Suite")
        print("=" * 80)
        print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project root: {self.project_root}")
        print(f"Tests directory: {self.tests_dir}")
        
        self.start_time = time.time()
        
        # Discover test files
        test_files = self.discover_tests()
        
        if not test_files:
            print("❌ No test files found!")
            return False
        
        print(f"\n📋 Found {len(test_files)} test files:")
        for test_file in test_files:
            print(f"   - {os.path.basename(test_file)}")
        
        # Run each test file
        all_success = True
        for test_file in test_files:
            try:
                result = self.run_single_test_file(test_file)
                self.results[test_file] = result
                
                if not result["success"]:
                    all_success = False
                    
            except Exception as e:
                print(f"❌ Error running {test_file}: {e}")
                self.results[test_file] = {
                    "file": test_file,
                    "tests_run": 0,
                    "failures": 0,
                    "errors": 1,
                    "skipped": 0,
                    "success": False,
                    "execution_time": 0,
                    "failures_details": [],
                    "errors_details": [(test_file, str(e))]
                }
                all_success = False
        
        self.end_time = time.time()
        
        # Print comprehensive report
        self.print_comprehensive_report()
        
        return all_success
    
    def print_comprehensive_report(self):
        """Print a comprehensive test report."""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        total_tests = sum(r["tests_run"] for r in self.results.values())
        total_failures = sum(r["failures"] for r in self.results.values())
        total_errors = sum(r["errors"] for r in self.results.values())
        total_skipped = sum(r["skipped"] for r in self.results.values())
        total_time = self.end_time - self.start_time if self.end_time else 0
        
        passed_files = sum(1 for r in self.results.values() if r["success"])
        total_files = len(self.results)
        
        print(f"📈 Overall Statistics:")
        print(f"   Test Files: {total_files}")
        print(f"   Passed Files: {passed_files}")
        print(f"   Failed Files: {total_files - passed_files}")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed Tests: {total_tests - total_failures - total_errors - total_skipped}")
        print(f"   Failed Tests: {total_failures}")
        print(f"   Error Tests: {total_errors}")
        print(f"   Skipped Tests: {total_skipped}")
        print(f"   Success Rate: {((total_tests - total_failures - total_errors - total_skipped) / total_tests * 100):.1f}%" if total_tests > 0 else "0%")
        print(f"   Total Execution Time: {total_time:.2f}s")
        
        print(f"\n📋 Test File Results:")
        for test_file, result in self.results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status} {os.path.basename(test_file)}")
            print(f"      Tests: {result['tests_run']}, "
                  f"Failures: {result['failures']}, "
                  f"Errors: {result['errors']}, "
                  f"Time: {result['execution_time']:.2f}s")
        
        # Print detailed failure information
        if total_failures > 0 or total_errors > 0:
            print(f"\n❌ Detailed Failure Information:")
            for test_file, result in self.results.items():
                if result["failures"] > 0:
                    print(f"\n   Failures in {os.path.basename(test_file)}:")
                    for test, traceback in result["failures_details"]:
                        print(f"      - {test}: {traceback.split('AssertionError:')[-1].strip()}")
                
                if result["errors"] > 0:
                    print(f"\n   Errors in {os.path.basename(test_file)}:")
                    for test, traceback in result["errors_details"]:
                        print(f"      - {test}: {traceback.split('Exception:')[-1].strip()}")
        
        # Print coverage analysis
        self.print_coverage_analysis()
        
        print(f"\n{'✅ ALL TESTS PASSED' if all(r['success'] for r in self.results.values()) else '❌ SOME TESTS FAILED'}")
        print(f"Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def print_coverage_analysis(self):
        """Print test coverage analysis."""
        print(f"\n📊 Coverage Analysis:")
        
        # Define expected test files and their purposes
        expected_tests = {
            "test_server.py": "Main server functionality",
            "test_database_operations.py": "Database connection and queries",
            "test_search_operations.py": "Search and find operations",
            "test_entity_operations.py": "Entity creation and deletion",
            "test_relationship_operations.py": "Relationship management",
            "test_observation_operations.py": "Observation management",
            "test_tools.py": "Tool definitions and schemas",
            "test_utils.py": "Validation utilities"
        }
        
        found_tests = set(os.path.basename(f) for f in self.results.keys())
        missing_tests = set(expected_tests.keys()) - found_tests
        
        print(f"   Expected Test Files: {len(expected_tests)}")
        print(f"   Found Test Files: {len(found_tests)}")
        print(f"   Missing Test Files: {len(missing_tests)}")
        
        if missing_tests:
            print(f"   Missing Tests:")
            for missing in sorted(missing_tests):
                print(f"      - {missing}: {expected_tests[missing]}")
        
        # Calculate coverage percentage
        coverage_percentage = (len(found_tests) / len(expected_tests)) * 100
        print(f"   Test Coverage: {coverage_percentage:.1f}%")
        
        # Module coverage analysis
        modules_tested = {
            "server.py": "test_server.py" in found_tests,
            "database/operations.py": "test_database_operations.py" in found_tests,
            "operations/search_operations.py": "test_search_operations.py" in found_tests,
            "operations/entity_operations.py": "test_entity_operations.py" in found_tests,
            "operations/relationship_operations.py": "test_relationship_operations.py" in found_tests,
            "operations/observation_operations.py": "test_observation_operations.py" in found_tests,
            "tools/tool_definitions.py": "test_tools.py" in found_tests,
            "utils/validators.py": "test_utils.py" in found_tests
        }
        
        tested_modules = sum(modules_tested.values())
        total_modules = len(modules_tested)
        module_coverage = (tested_modules / total_modules) * 100
        
        print(f"\n   Module Coverage: {module_coverage:.1f}% ({tested_modules}/{total_modules})")
        for module, tested in modules_tested.items():
            status = "✅" if tested else "❌"
            print(f"      {status} {module}")
    
    def run_syntax_check(self) -> bool:
        """Run syntax check on all Python files."""
        print("\n🔍 Running syntax check...")
        
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip tests directory and __pycache__
            if "tests" in root or "__pycache__" in root:
                continue
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        syntax_errors = []
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), py_file, 'exec')
            except SyntaxError as e:
                syntax_errors.append((py_file, str(e)))
            except Exception as e:
                syntax_errors.append((py_file, f"Unexpected error: {e}"))
        
        if syntax_errors:
            print("❌ Syntax errors found:")
            for file, error in syntax_errors:
                print(f"   - {file}: {error}")
            return False
        else:
            print("✅ All Python files have valid syntax!")
            return True


def main():
    """Main function to run all tests."""
    runner = TestRunner()
    
    # Run syntax check first
    syntax_ok = runner.run_syntax_check()
    if not syntax_ok:
        print("\n❌ Syntax check failed. Please fix syntax errors before running tests.")
        return False
    
    # Run all tests
    success = runner.run_all_tests()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 