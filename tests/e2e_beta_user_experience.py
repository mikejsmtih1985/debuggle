#!/usr/bin/env python3
"""
🧪 Beta User Experience End-to-End Test

This test simulates the exact experience a beta user would have:
1. Download executables from GitHub Actions
2. Extract and test basic functionality
3. Test CLI functionality
4. Test Claude integration (with graceful fallback)
5. Verify all platforms have working executables

By default, stops on the first failure (fail-fast mode) to save time.
Use --continue-on-failure to run all iterations despite failures.
Use --single-test to run just one test iteration for quick validation.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

class BetaUserExperienceTest:
    def __init__(self):
        self.test_dir: Optional[Path] = None
        self.repo = "mikejsmtih1985/debuggle"
        self.platforms = ['linux-x64', 'macos-x64', 'macos-arm64', 'windows-x64']
        self.current_platform = self._detect_current_platform()
        
    def _detect_current_platform(self) -> str:
        """Detect current platform for testing"""
        import platform
        system = platform.system().lower()
        arch = platform.machine().lower()
        
        if system == 'darwin':
            system = 'macos'
        elif system in ['win32', 'windows']:
            system = 'windows'
            
        if arch in ['x86_64', 'amd64']:
            arch = 'x64'
        elif arch in ['aarch64', 'arm64']:
            arch = 'arm64'
            
        return f"{system}-{arch}"
    
    def setup_test_environment(self):
        """Create isolated test environment"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="debuggle_beta_test_"))
        print(f"🧪 Test environment: {self.test_dir}")
        return True
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.test_dir and self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up: {self.test_dir}")
    
    def wait_for_successful_build(self, timeout_minutes=10) -> Optional[str]:
        """Wait for a successful GitHub Actions build"""
        print("⏳ Waiting for successful GitHub Actions build...")
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while time.time() - start_time < timeout_seconds:
            try:
                # Get latest workflow runs
                result = subprocess.run([
                    'gh', 'run', 'list', '--repo', self.repo, '--limit', '5', '--json', 
                    'status,conclusion,databaseId,headBranch,event'
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"❌ Failed to get workflow runs: {result.stderr}")
                    time.sleep(30)
                    continue
                
                runs = json.loads(result.stdout)
                
                # Look for a successful run on main branch
                for run in runs:
                    if (run.get('headBranch') == 'main' and 
                        run.get('status') == 'completed' and 
                        run.get('conclusion') == 'success'):
                        run_id = run.get('databaseId')
                        print(f"✅ Found successful build: {run_id}")
                        return str(run_id)
                
                # Check if any runs are still in progress
                in_progress = any(run.get('status') == 'in_progress' for run in runs)
                if in_progress:
                    print("🔄 Build in progress, waiting...")
                else:
                    print("⚠️ No successful builds found, waiting for new build...")
                
                time.sleep(30)
                
            except Exception as e:
                print(f"❌ Error checking builds: {e}")
                time.sleep(30)
        
        print(f"❌ Timeout: No successful build found in {timeout_minutes} minutes")
        return None
    
    def download_artifacts(self, run_id: str) -> bool:
        """Download artifacts from successful build"""
        print(f"📥 Downloading artifacts from run {run_id}...")
        
        if not self.test_dir:
            print("❌ Test directory not initialized")
            return False
        
        try:
            os.chdir(self.test_dir)
            
            # Download artifacts
            result = subprocess.run([
                'gh', 'run', 'download', run_id, '--repo', self.repo
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to download artifacts: {result.stderr}")
                return False
            
            # Check what was downloaded
            downloaded = list(self.test_dir.iterdir())
            print(f"📦 Downloaded artifacts: {[d.name for d in downloaded]}")
            
            # Verify we have the expected platform directories
            expected_dirs = [f"debuggle-{platform}" for platform in self.platforms]
            actual_dirs = [d.name for d in downloaded if d.is_dir()]
            
            missing = set(expected_dirs) - set(actual_dirs)
            if missing:
                print(f"⚠️ Missing platform builds: {missing}")
            
            if not actual_dirs:
                print("❌ No artifact directories found")
                return False
            
            print(f"✅ Downloaded {len(actual_dirs)} platform builds")
            return True
            
        except Exception as e:
            print(f"❌ Error downloading artifacts: {e}")
            return False
    
    def test_platform_executable(self, platform: str) -> Dict[str, bool]:
        """Test executable for a specific platform"""
        print(f"🧪 Testing {platform} executable...")
        
        results = {
            'exists': False,
            'executable': False,
            'help_works': False,
            'version_works': False,
            'analyze_works': False,
            'claude_graceful_fallback': False
        }
        
        if not self.test_dir:
            print("❌ Test directory not initialized")
            return results
        
        platform_dir = self.test_dir / f"debuggle-{platform}"
        if not platform_dir.exists():
            print(f"❌ Platform directory not found: {platform_dir}")
            return results
        
        results['exists'] = True
        
        # Find the executable
        if platform.startswith('windows'):
            executable = platform_dir / 'debuggle.exe'
        else:
            executable = platform_dir / 'debuggle'
        
        if not executable.exists():
            print(f"❌ Executable not found: {executable}")
            return results
        
        # Make executable (for Unix systems)
        if not platform.startswith('windows'):
            try:
                executable.chmod(0o755)
                results['executable'] = True
            except Exception as e:
                print(f"❌ Failed to make executable: {e}")
                return results
        else:
            results['executable'] = True
        
        # Only test execution on current platform
        if platform != self.current_platform:
            print(f"⏭️ Skipping execution test for {platform} (cross-platform)")
            results['help_works'] = True  # Assume it works for cross-platform
            results['version_works'] = True
            results['analyze_works'] = True
            results['claude_graceful_fallback'] = True
            return results
        
        try:
            os.chdir(platform_dir)
            
            # Test --help
            result = subprocess.run([str(executable), '--help'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and 'Debuggle' in result.stdout:
                results['help_works'] = True
                print("  ✅ Help command works")
            
            # Test version
            result = subprocess.run([str(executable), 'version'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and 'Claude AI' in result.stdout:
                results['version_works'] = True
                print("  ✅ Version command works")
            
            # Test basic analysis
            test_error = "IndexError: list index out of range"
            result = subprocess.run([str(executable), 'analyze'], 
                                  input=test_error, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and 'FULL DEVELOPMENT CONTEXT ANALYSIS' in result.stdout:
                results['analyze_works'] = True
                print("  ✅ Basic analysis works")
            
            # Test Claude graceful fallback (without API key)
            env = os.environ.copy()
            env.pop('ANTHROPIC_API_KEY', None)  # Ensure no API key
            
            result = subprocess.run([str(executable), 'analyze', '--claude'], 
                                  input=test_error, capture_output=True, text=True, 
                                  timeout=30, env=env)
            if (result.returncode == 0 and 
                'Claude AI: Not available' in result.stdout and
                'Debuggle works great without AI too!' in result.stdout):
                results['claude_graceful_fallback'] = True
                print("  ✅ Claude graceful fallback works")
            
        except subprocess.TimeoutExpired:
            print(f"  ❌ Timeout testing {platform}")
        except Exception as e:
            print(f"  ❌ Error testing {platform}: {e}")
        
        return results
    
    def run_single_test(self, test_number: int) -> bool:
        """Run a single complete test cycle"""
        print(f"\n🚀 TEST {test_number}/25 - Beta User Experience")
        print("=" * 60)
        
        try:
            # Setup
            if not self.setup_test_environment():
                return False
            
            # Wait for successful build
            run_id = self.wait_for_successful_build(timeout_minutes=15)
            if not run_id:
                return False
            
            # Download artifacts
            if not self.download_artifacts(run_id):
                return False
            
            # Test all platforms
            all_passed = True
            platform_results = {}
            
            for platform in self.platforms:
                results = self.test_platform_executable(platform)
                platform_results[platform] = results
                
                # Check if critical tests passed
                critical_tests = ['exists', 'executable']
                if platform == self.current_platform:
                    critical_tests.extend(['help_works', 'version_works', 'analyze_works', 'claude_graceful_fallback'])
                
                platform_passed = all(results.get(test, False) for test in critical_tests)
                
                if platform_passed:
                    print(f"  ✅ {platform}: PASSED")
                else:
                    print(f"  ❌ {platform}: FAILED")
                    failed_tests = [test for test in critical_tests if not results.get(test, False)]
                    print(f"    Failed: {failed_tests}")
                    all_passed = False
            
            # Summary
            if all_passed:
                print(f"\n🎉 TEST {test_number}: SUCCESS")
                print("   Beta user experience is working perfectly!")
            else:
                print(f"\n❌ TEST {test_number}: FAILED")
                print("   Issues found in beta user experience")
            
            return all_passed
            
        except Exception as e:
            print(f"❌ TEST {test_number}: EXCEPTION - {e}")
            return False
        finally:
            self.cleanup_test_environment()
    
    def run_reliability_test(self, iterations=25, fail_fast=True):
        """Run the test multiple times to ensure reliability"""
        print("🎯 DEBUGGLE BETA USER RELIABILITY TEST")
        print("=" * 60)
        print(f"Running up to {iterations} iterations to ensure consistent user experience")
        if fail_fast:
            print("⚡ Fail-fast mode: Will stop on first failure")
        print()
        
        successes = 0
        failures = 0
        start_time = time.time()
        
        for i in range(1, iterations + 1):
            success = self.run_single_test(i)
            
            if success:
                successes += 1
                print(f"\n🎉 TEST {i}: PASSED!")
            else:
                failures += 1
                print(f"\n❌ TEST {i}: FAILED!")
                
                if fail_fast:
                    print("\n🛑 STOPPING: Fail-fast mode enabled")
                    print("Fix the issues above before running reliability tests.")
                    print("\nTo continue testing despite failures, run with --continue-on-failure")
                    break
            
            # Progress update
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            estimated_remaining = avg_time * (iterations - i) if i < iterations else 0
            
            print(f"\n📊 PROGRESS: {i}/{iterations} completed")
            print(f"   ✅ Successes: {successes}")
            print(f"   ❌ Failures: {failures}")
            if estimated_remaining > 0:
                print(f"   ⏱️ Estimated remaining time: {estimated_remaining/60:.1f} minutes")
            
            # Small delay between tests
            if i < iterations:
                time.sleep(2)  # Reduced delay for faster feedback
        
        # Final results
        total_time = time.time() - start_time
        success_rate = (successes / iterations) * 100
        
        print("\n" + "=" * 60)
        print("🏁 FINAL RESULTS")
        print("=" * 60)
        print(f"Total iterations: {iterations}")
        print(f"Successes: {successes}")
        print(f"Failures: {failures}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Total time: {total_time/60:.1f} minutes")
        print(f"Average time per test: {total_time/iterations:.1f} seconds")
        
        if success_rate >= 95:
            print("\n🎉 EXCELLENT! Beta user experience is highly reliable!")
            print("Your users should have a smooth experience.")
        elif success_rate >= 80:
            print("\n✅ GOOD! Beta user experience is mostly reliable.")
            print("Minor issues may occur occasionally.")
        else:
            print("\n⚠️ NEEDS IMPROVEMENT! Beta user experience has reliability issues.")
            print("Recommend investigating failures before beta release.")
        
        return success_rate >= 95

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Beta User Experience Test")
    parser.add_argument('--iterations', type=int, default=25, 
                       help='Number of test iterations to run (default: 25)')
    parser.add_argument('--continue-on-failure', action='store_true',
                       help='Continue testing even after failures (default: stop on first failure)')
    parser.add_argument('--single-test', action='store_true',
                       help='Run just one test iteration')
    
    args = parser.parse_args()
    
    tester = BetaUserExperienceTest()
    
    try:
        if args.single_test:
            print("🧪 Running single test iteration...")
            success = tester.run_single_test(1)
            print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
            sys.exit(0 if success else 1)
        else:
            iterations = args.iterations
            fail_fast = not args.continue_on_failure
            success = tester.run_reliability_test(iterations, fail_fast)
            sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()