#!/usr/bin/env python3
"""
Fix emoji encoding issues in test files
"""

import os
import re

def remove_emojis_from_file(file_path):
    """Remove emojis from a file"""
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define emoji patterns and their replacements
    emoji_replacements = {
        '🔧': '',
        '📊': '',
        '📁': '',
        '🌐': '',
        '🔌': '',
        '👤': '',
        '🗄️': '',
        '🔄': '',
        '✅': '',
        '❌': '',
        '🎉': '',
        '🚀': '',
        '⚠️': '',
        '💡': '',
        '🔍': '',
        '🔥': '',
        '💚': '',
        '🍽️': '',
        '🟢': '',
        '🟡': '',
        '🟠': '',
        '🔴': '',
        '😏': '',
        '🌟': '',
        '🎯': '',
        '✨': '',
        '🤓': '',
        '📝': '',
        '💀': '',
        '☠️': '',
        '🚨': '',
        '🧪': '',
        '⏱️': '',
        '📈': '',
        '🔧': '',
        '🧪': '',
        '⚡': '',
        '💻': '',
        '🎊': '',
        '🎈': '',
        '🎁': '',
        '🎀': '',
        '🎂': '',
        '🍰': '',
        '🧁': '',
        '🍪': '',
        '🍫': '',
        '🍬': '',
        '🍭': '',
        '🍮': '',
        '🍯': '',
        '🍼': '',
        '🥛': '',
        '☕': '',
        '🍵': '',
        '🧃': '',
        '🥤': '',
        '🍶': '',
        '🍾': '',
        '🍷': '',
        '🍸': '',
        '🍹': '',
        '🍺': '',
        '🍻': '',
        '🥂': '',
        '🥃': '',
        '🥗': '',
        '🍞': '',
        '🥩': '',
        '🥑': '',
    }
    
    # Replace emojis
    for emoji, replacement in emoji_replacements.items():
        content = content.replace(emoji, replacement)
    
    # Also remove any remaining emoji-like unicode characters
    # This regex matches most emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    content = emoji_pattern.sub('', content)
    
    # Clean up any double spaces or empty lines created by emoji removal
    content = re.sub(r'  +', ' ', content)  # Multiple spaces to single space
    content = re.sub(r'^ +', '', content, flags=re.MULTILINE)  # Leading spaces
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed {file_path}")

def main():
    """Fix all test files"""
    test_files = [
        'test_database.py',
        'test_improvements.py', 
        'test_nb_note.py',
        'test_mysql_connection.py'
    ]
    
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    for test_file in test_files:
        file_path = os.path.join(tests_dir, test_file)
        if os.path.exists(file_path):
            remove_emojis_from_file(file_path)
        else:
            print(f"File not found: {file_path}")
    
    print("All test files have been processed!")

if __name__ == "__main__":
    main()
