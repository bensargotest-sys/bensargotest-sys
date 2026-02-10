#!/usr/bin/env python3
from datetime import datetime

def main():
    print("Hello from Coder!")
    timestamp = datetime.now().isoformat()
    print(f"Current timestamp: {timestamp}")
    return timestamp

if __name__ == "__main__":
    main()
