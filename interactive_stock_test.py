#!/usr/bin/env python3
"""
Interactive script to test stock parser with user input
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from stock_parser import get_stock_info

def interactive_test():
    """Interactive testing of the stock parser"""
    print("🤖 Stock Parser Interactive Tester")
    print("=" * 40)
    print("Enter messages to test the stock parser.")
    print("Examples: #2330, #2884, #0050")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            user_input = input("💬 Enter message: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                print("ℹ️  Please enter a message.\n")
                continue
            
            print(f"📝 Processing: '{user_input}'")
            
            # Test the stock parser
            result = get_stock_info(user_input)
            
            if result:
                icon = ""
                if result["upsOrDowns"] == 1:
                    icon = "🚀"
                elif result["upsOrDowns"] == -1:
                    icon = "💸"

                print(f"🎯 Bot Response: {result["name"]}: {result["price"]} {icon}")
            else:
                print("ℹ️  No stock command detected (message would be ignored)")
            
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"💥 Error: {e}")
            print("-" * 40)

if __name__ == "__main__":
    interactive_test()