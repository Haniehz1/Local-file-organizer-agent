#!/usr/bin/env python3
"""Quick test of the file organizer functionality"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from file_organizer.server import app, scan_files, classify_files, propose_organization


async def quick_test():
    """Run a quick test of the main functionality"""
    print("=" * 60)
    print("File Organizer - Quick Test")
    print("=" * 60)

    async with app.run():
        # Test scanning
        print("\n1. Testing scan_files...")
        result = await scan_files(paths=["~/Downloads"])
        print(f"✓ Scan completed: {result[:100]}...")

        # Test classification
        print("\n2. Testing classify_files...")
        result = await classify_files()
        print(f"✓ Classification completed: {result[:100]}...")

        # Test organization plan
        print("\n3. Testing propose_organization...")
        result = await propose_organization()
        print(f"✓ Plan created: {result[:200]}...")

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run: python main.py (interactive mode)")
        print("2. Run: python main.py --server (MCP server mode)")
        print("3. Add to Claude Desktop config (see USAGE.md)")


if __name__ == "__main__":
    try:
        asyncio.run(quick_test())
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
