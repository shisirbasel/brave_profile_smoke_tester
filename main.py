import sys
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for Brave smoke tester."""
    parser = argparse.ArgumentParser(
        description="Brave Profile Smoke Tester - Test multiple Brave profiles"
    )
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


def validate_brave_path(brave_path: str) -> None:
    """
    Validate that the Brave executable path exists.
    Exit immediately if the path is invalid.
    """
    brave_file = Path(brave_path)
    
    if not brave_file.exists():
        print(f"Error: Brave executable not found at: {brave_path}")
        print("Please check the --brave-path argument and try again.")
        sys.exit(1)
    
    if not brave_file.is_file():
        print(f"Error: Path is not a file: {brave_path}")
        sys.exit(1)


def find_profiles(root_dir: str) -> list:
    """
    Return a sorted list of profile directories inside the given root folder.
    """
    root_path = Path(root_dir)
    if not root_path.exists() or not root_path.is_dir():
        print(f"Error: Profiles root folder does not exist: {root_dir}")
        sys.exit(1)

    # Get all subdirectories and sort them alphabetically for deterministic ordering
    profiles = sorted([str(p) for p in root_path.iterdir() if p.is_dir()])
    return profiles


def launch_brave_with_profile(
        brave_path: str,
        profile_path: str,
        url: str,
        headless: bool,
        timeout: int
) -> None:
    """
    Launch Brave with a specific profile and navigate to a URL.
    
    Raises:
        FileNotFoundError: If profile directory doesn't exist
        NotADirectoryError: If profile path is not a directory
        PlaywrightTimeoutError: If page navigation times out
        PlaywrightError: If browser fails to launch or other Playwright errors
    """
    profile_dir = Path(profile_path)
    
    # Fail if profile directory doesn't exist (don't create it)
    if not profile_dir.exists():
        raise FileNotFoundError(f"Profile directory does not exist: {profile_path}")
    
    if not profile_dir.is_dir():
        raise NotADirectoryError(f"Profile path is not a directory: {profile_path}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            executable_path=brave_path,
            headless=headless
        )
        
        # Use existing page instead of creating new one
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()
        
        try:
            page.goto(url, timeout=timeout, wait_until="load")
        finally:
            if not headless:
                time.sleep(1)
            context.close()


def print_summary(results: dict) -> None:
    """Print a summary table of profile test results with PASS/FAIL counts."""
    print("\n======== Summary ========")
    pass_count = 0
    fail_count = 0

    for profile, result in results.items():
        status = result["status"]
        message = result["message"]
        profile_name = Path(profile).name
        print(f"Profile: {profile_name:<20} -> {status} ({message})")
        if status == "PASS":
            pass_count += 1
        else:
            fail_count += 1

    print(f"\nTotal profiles: {len(results)}")
    print(f"PASS: {pass_count}")
    print(f"FAIL: {fail_count}")


def main() -> None:
    """Main entry point: parse args, test profiles, and print summary."""
    args = parse_arguments()

    # Validate Brave path before doing anything else
    validate_brave_path(args.brave_path)

    profiles = find_profiles(args.profiles_root)

    if not profiles:
        print("Error: No profile directories found.")
        sys.exit(1)

    print("Testing profiles:")
    results = {}

    for profile in profiles:
        profile_name = Path(profile).name
        print(f"  Launching profile: {profile_name}")
        
        try:
            launch_brave_with_profile(
                brave_path=args.brave_path,
                profile_path=profile,
                url=args.url,
                headless=args.headless,
                timeout=args.page_load_timeout
            )
            results[profile] = {"status": "PASS", "message": "OK"}
            
        except FileNotFoundError as e:
            results[profile] = {"status": "FAIL", "message": str(e)}
            
        except NotADirectoryError as e:
            results[profile] = {"status": "FAIL", "message": str(e)}
            
        except PlaywrightTimeoutError:
            results[profile] = {"status": "FAIL", "message": f"Timeout loading {args.url}"}
            
        except PlaywrightError as e:
            error_msg = str(e).split('\n')[0]
            results[profile] = {"status": "FAIL", "message": f"Browser error: {error_msg}"}
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e).split('\n')[0][:100]
            results[profile] = {"status": "FAIL", "message": f"{error_type}: {error_msg}"}

    print_summary(results)

    # Exit with appropriate code
    if any(r["status"] == "FAIL" for r in results.values()):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()