from __future__ import annotations

import os
import sys
import yaml
from pathlib import Path
from typing import Any

def validate_yaml(file_path: Path) -> bool:
    """Check if a YAML file is valid and can be loaded."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            yaml.safe_load(f)
        return True
    except Exception as e:
        print(f"Error in {file_path}: {e}")
        return False

def main() -> int:
    """Validate all YAML configurations in the configs directory."""
    config_root = Path("configs")
    if not config_root.is_dir():
        print(f"Error: Config directory '{config_root}' not found.")
        return 1

    print(f"Validating configurations in {config_root.absolute()}...")
    
    yaml_files = list(config_root.rglob("*.yaml"))
    if not yaml_files:
        print("No YAML configuration files found.")
        return 0

    valid_count = 0
    invalid_count = 0

    for yaml_file in yaml_files:
        if validate_yaml(yaml_file):
            print(f"  [OK] {yaml_file}")
            valid_count += 1
        else:
            print(f"  [FAIL] {yaml_file}")
            invalid_count += 1

    print("-" * 40)
    print(f"Total: {len(yaml_files)} | Valid: {valid_count} | Invalid: {invalid_count}")

    if invalid_count > 0:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
