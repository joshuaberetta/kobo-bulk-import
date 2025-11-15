#!/usr/bin/env python3
"""
Quick wrapper script to submit data to Kobo.
Located in root for easy access.
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from submit_to_kobo import main

if __name__ == "__main__":
    main()
