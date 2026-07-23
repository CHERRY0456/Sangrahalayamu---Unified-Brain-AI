import re
import sys

def fix_config():
    path = "app/core/config.py"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Replace alias="something" with validation_alias="something"
    new_text = re.sub(r'alias="([^"]+)"', r'validation_alias="\1"', text)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_text)

if __name__ == "__main__":
    fix_config()
