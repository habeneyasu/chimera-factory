#!/usr/bin/env python3
"""
Task 2 Validation Script
Validates all deliverables for Task 2: The Architect

Usage:
    uv run python scripts/validate_task2.py
    # or
    make validate-task2
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class Task2Validator:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.errors = []
        self.warnings = []
        self.passed = []
        
    def check_file_exists(self, filepath: str, description: str) -> bool:
        """Check if a file exists"""
        full_path = self.root_dir / filepath
        if full_path.exists():
            self.passed.append(f"✅ {description}: {filepath}")
            return True
        else:
            self.errors.append(f"❌ {description}: {filepath} NOT FOUND")
            return False
    
    def check_file_size(self, filepath: str, min_lines: int, description: str) -> bool:
        """Check if a file has minimum expected lines"""
        full_path = self.root_dir / filepath
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            
            if lines >= min_lines:
                self.passed.append(f"✅ {description}: {filepath} ({lines} lines, expected ≥{min_lines})")
                return True
            else:
                self.warnings.append(f"⚠️  {description}: {filepath} has {lines} lines (expected ≥{min_lines})")
                return False
        except Exception as e:
            self.errors.append(f"❌ Error reading {filepath}: {e}")
            return False
    
    def check_json_valid(self, filepath: str, description: str) -> bool:
        """Check if a JSON file is valid"""
        full_path = self.root_dir / filepath
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                json.load(f)
            self.passed.append(f"✅ {description}: {filepath} (valid JSON)")
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ {description}: {filepath} - Invalid JSON: {e}")
            return False
        except Exception as e:
            self.errors.append(f"❌ Error reading {filepath}: {e}")
            return False
    
    def check_contains_text(self, filepath: str, text: str, description: str) -> bool:
        """Check if a file contains specific text"""
        full_path = self.root_dir / filepath
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if text.lower() in content.lower():
                self.passed.append(f"✅ {description}: {filepath} contains '{text}'")
                return True
            else:
                self.warnings.append(f"⚠️  {description}: {filepath} does not contain '{text}'")
                return False
        except Exception as e:
            self.errors.append(f"❌ Error reading {filepath}: {e}")
            return False
    
    def validate_task_2_1(self) -> Dict[str, bool]:
        """Validate Task 2.1: Master Specification"""
        print(f"\n{BOLD}{BLUE}=== Task 2.1: Master Specification ==={RESET}\n")
        
        results = {}
        
        # Check all spec files
        spec_files = {
            "specs/_meta.md": ("Master Specification", 200),
            "specs/functional.md": ("Functional Specs (User Stories)", 400),
            "specs/technical.md": ("Technical Specs (API Contracts)", 500),
            "specs/database/schema.sql": ("Database Schema", 150),
            "specs/database/erd.md": ("Entity Relationship Diagram", 100),
            "specs/openclaw_integration.md": ("OpenClaw Integration", 700),
            "specs/api/orchestrator.yaml": ("OpenAPI Specification", 50),
        }
        
        for filepath, (desc, min_lines) in spec_files.items():
            exists = self.check_file_exists(filepath, desc)
            if exists:
                self.check_file_size(filepath, min_lines, desc)
            results[filepath] = exists
        
        # Check for Prime Directive in _meta.md
        self.check_contains_text("specs/_meta.md", "Prime Directive", "Prime Directive in _meta.md")
        
        # Check for user stories in functional.md
        self.check_contains_text("specs/functional.md", "As an Agent", "User stories in functional.md")
        
        # Check for JSON Schema in technical.md
        self.check_contains_text("specs/technical.md", "json schema", "JSON Schema in technical.md")
        
        return results
    
    def validate_task_2_2(self) -> Dict[str, bool]:
        """Validate Task 2.2: Context Engineering"""
        print(f"\n{BOLD}{BLUE}=== Task 2.2: Context Engineering ==={RESET}\n")
        
        results = {}
        
        # Check .cursor/rules file
        rules_file = ".cursor/rules"
        exists = self.check_file_exists(rules_file, "AI Co-Pilot Rules")
        results[rules_file] = exists
        
        if exists:
            # Check file size
            self.check_file_size(rules_file, 400, "AI Co-Pilot Rules")
            
            # Check for key content
            self.check_contains_text(rules_file, "Project Chimera", "Project context in rules")
            self.check_contains_text(rules_file, "NEVER generate code without checking specs", "Prime Directive in rules")
            self.check_contains_text(rules_file, "Explain your plan before writing code", "Traceability in rules")
        
        return results
    
    def validate_task_2_3(self) -> Dict[str, bool]:
        """Validate Task 2.3: Tooling & Skills Strategy"""
        print(f"\n{BOLD}{BLUE}=== Task 2.3: Tooling & Skills Strategy ==={RESET}\n")
        
        results = {}
        
        # Check developer tools documentation
        tooling_file = "research/tooling_strategy.md"
        exists = self.check_file_exists(tooling_file, "Developer Tools Documentation")
        results[tooling_file] = exists
        if exists:
            self.check_file_size(tooling_file, 400, "Developer Tools Documentation")
        
        # Check skills README
        skills_readme = "skills/README.md"
        exists = self.check_file_exists(skills_readme, "Skills Overview")
        results[skills_readme] = exists
        if exists:
            self.check_file_size(skills_readme, 200, "Skills Overview")
        
        # Check critical skills
        critical_skills = {
            "skills/skill_trend_research/README.md": ("Trend Research Skill", 200),
            "skills/skill_content_generate/README.md": ("Content Generation Skill", 300),
            "skills/skill_engagement_manage/README.md": ("Engagement Management Skill", 300),
        }
        
        for filepath, (desc, min_lines) in critical_skills.items():
            exists = self.check_file_exists(filepath, desc)
            results[filepath] = exists
            if exists:
                self.check_file_size(filepath, min_lines, desc)
        
        # Check skill contracts (JSON Schema)
        contract_files = [
            "skills/skill_trend_research/contract.json",
            "skills/skill_content_generate/contract.json",
            "skills/skill_engagement_manage/contract.json",
        ]
        
        for contract_file in contract_files:
            exists = self.check_file_exists(contract_file, f"Skill Contract: {Path(contract_file).parent.name}")
            results[contract_file] = exists
            if exists:
                self.check_json_valid(contract_file, f"Skill Contract: {Path(contract_file).parent.name}")
                # Check for required schema fields
                try:
                    with open(self.root_dir / contract_file, 'r') as f:
                        contract = json.load(f)
                    if 'input' in contract and 'output' in contract:
                        self.passed.append(f"✅ {contract_file} has input/output contracts")
                    else:
                        self.warnings.append(f"⚠️  {contract_file} missing input/output contracts")
                except:
                    pass
        
        return results
    
    def run_validation(self) -> Tuple[bool, Dict]:
        """Run all validations"""
        print(f"{BOLD}{GREEN}Task 2 Validation Report{RESET}")
        print(f"{'=' * 60}\n")
        
        task_2_1_results = self.validate_task_2_1()
        task_2_2_results = self.validate_task_2_2()
        task_2_3_results = self.validate_task_2_3()
        
        # Summary
        print(f"\n{BOLD}{BLUE}=== Summary ==={RESET}\n")
        
        total_checks = len(self.passed) + len(self.warnings) + len(self.errors)
        print(f"Total Checks: {total_checks}")
        print(f"{GREEN}Passed: {len(self.passed)}{RESET}")
        print(f"{YELLOW}Warnings: {len(self.warnings)}{RESET}")
        print(f"{RED}Errors: {len(self.errors)}{RESET}\n")
        
        # Print warnings
        if self.warnings:
            print(f"{BOLD}{YELLOW}Warnings:{RESET}")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        # Print errors
        if self.errors:
            print(f"{BOLD}{RED}Errors:{RESET}")
            for error in self.errors:
                print(f"  {error}")
            print()
        
        # Overall status
        success = len(self.errors) == 0
        if success:
            print(f"{BOLD}{GREEN}✅ Task 2 Validation: PASSED{RESET}")
            if self.warnings:
                print(f"{YELLOW}⚠️  Some warnings present, but all critical files exist.{RESET}")
        else:
            print(f"{BOLD}{RED}❌ Task 2 Validation: FAILED{RESET}")
            print(f"{RED}Please fix the errors above before proceeding.{RESET}")
        
        return success, {
            'passed': len(self.passed),
            'warnings': len(self.warnings),
            'errors': len(self.errors),
            'task_2_1': task_2_1_results,
            'task_2_2': task_2_2_results,
            'task_2_3': task_2_3_results,
        }


def main():
    """Main entry point"""
    # Get project root (assuming script is in scripts/ directory)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    validator = Task2Validator(root_dir)
    success, results = validator.run_validation()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
