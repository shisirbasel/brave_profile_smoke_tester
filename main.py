import sys
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

def parse_arguments() -> argparse.Namespace:
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--brave-path',
        required=True,
        help='Full path to brave.exe file'
    )
    parser.add_argument(
        '--profiles-root',
        required=True,
        help='Path to the root folder containing multiple Brave profiles'
    )
    parser.add_argument(
        '--url',
        required=True,
        help='URL to navigate to'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        default=False,
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--page-load-timeout',
        type=int,
        default=30000,
        help='Timeout in milliseconds for page load'
    )
    return parser.parse_args()


def find_profiles(root_dir: str) -> list:
    # Get all subdirectories in the profiles root folder
    root_path = Path(root_dir)
    if not root_path.exists() or not root_path.is_dir():
        print(f"Profiles root folder does not exist: {root_dir}")
        return []

    profiles = [str(p) for p in root_path.iterdir() if p.is_dir()]
    return profiles


def launch_brave_with_profile(
        brave_path: str,
        profile_path: str,
        url: str,
        headless: bool = False,
        timeout: int = 10000
) -> None:
    # Launch Brave with a specific profile and navigate to the URL
    profile_dir: Path = Path(profile_path)
    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            executable_path=brave_path,
            headless=headless
        )
        page = context.new_page()
        try:
            page.goto(url, timeout=timeout, wait_until="load")
        finally:
            # Close the browser after navigation
            time.sleep(1)
            context.close()


def print_summary(results: dict) -> None:
    # Print a clean summary table of profile test results
    print("\n======== Summary ========")
    pass_count = 0
    fail_count = 0

    for profile, result in results.items():
        status = result["status"]
        message = result["message"]
        # Show profile name, status, and message
        print(f"Profile: {Path(profile).name:<20} -> {status} ({message})")
        if status == "PASS":
            pass_count += 1
        else:
            fail_count += 1

    # Print total counts
    print(f"\nTotal profiles: {len(results)}")
    print(f"PASS: {pass_count}")
    print(f"FAIL: {fail_count}")


def main() -> None:
    args = parse_arguments()
    profiles = find_profiles(args.profiles_root)

    if not profiles:
        print("No profiles found.")
        sys.exit(1)

    print("Testing profiles:")
    results = {}

    for profile in profiles:
        print(f"  Launching profile: {profile}")
        try:
            # Attempt to launch Brave and navigate
            launch_brave_with_profile(
                brave_path=args.brave_path,
                profile_path=profile,
                url=args.url,
                headless=args.headless,
                timeout=args.page_load_timeout
            )
            # Mark profile as PASS if no exception occurs
            results[profile] = {"status": "PASS", "message": "OK"}
        except Exception as e:
            # Mark profile as FAIL if any error occurs
            results[profile] = {"status": "FAIL", "message": str(e)}

    # Print summary after all profiles tested
    print_summary(results)

    # Exit with non-zero code if any profile failed
    if any(r["status"] == "FAIL" for r in results.values()):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
