#!/usr/bin/env python3
"""
Interactive script to test stock parser with user input
"""

import argparse
import asyncio
import os
import sys
import traceback

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from line.command_parser import parse_line_command
from routing.config import natural_language_routing_enabled
from routing.executor import FinancialExecutor
from routing.models import ExecutionPlan, FinancialContext
from routing.router import FinancialRouter


def process_message(user_input: str, *, enable_financial_routing: bool):
    """Process one message using either the legacy parser or financial routing."""
    if not enable_financial_routing:
        return parse_line_command(user_input, True)

    result = asyncio.run(
        FinancialRouter().route_line_request(
            FinancialContext(user_id="interactive-test", conversation_id="interactive-test", message=user_input),
            is_one_to_one=True,
        )
    )
    if isinstance(result, ExecutionPlan):
        return FinancialExecutor().execute(result, query=user_input)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactively test stock commands and financial request routing.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--enable-financial-routing", action="store_true", help="Enable the FinancialRouter for unmatched messages.")
    group.add_argument("--disable-financial-routing", action="store_true", help="Disable the FinancialRouter and use the legacy parser only.")
    return parser.parse_args()


def interactive_test(*, enable_financial_routing: bool | None = None):
    """Interactive testing of the stock parser"""
    if enable_financial_routing is None:
        enable_financial_routing = natural_language_routing_enabled()

    print("🤖 Stock Parser Interactive Tester")
    print("=" * 40)
    print("Enter messages to test the stock parser.")
    print("Examples: #2330, #2884, #0050")
    print("Type 'quit' or 'exit' to stop.")
    print(f"Financial routing: {'ON' if enable_financial_routing else 'OFF'}\n")

    while True:
        try:
            user_input = input("💬 Enter message: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break

            if not user_input:
                print("ℹ️  Please enter a message.\n")
                continue

            print(f"📝 Processing: '{user_input}'")

            result = process_message(user_input, enable_financial_routing=enable_financial_routing)

            if result:
                print("🎯 Bot Response:")
                print(result)
            else:
                print("ℹ️  No stock command detected (message would be ignored)")

            print("-" * 40)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"💥 Error: {e}")
            print(traceback.format_exc())
            print("-" * 40)


if __name__ == "__main__":
    args = parse_args()
    explicit_mode = True if args.enable_financial_routing else False if args.disable_financial_routing else None
    interactive_test(enable_financial_routing=explicit_mode)
