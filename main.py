from playwright.sync_api import sync_playwright
from pathlib import Path
import argparse
import time


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for launching Brave.
    """
    parser = argparse.ArgumentParser(
        description="Brave Profile Smoke Tester - Test multiple Brave Profiles"
    )
    parser.add_argument(
        '--brave-path',
        required=True,
        help='Full path to brave.exe file'
    )
    parser.add_argument(
        '--profile-path',
        required=True,
        help='Path to a single profile directory (temporary - will be replaced with --profiles-root later)'
    ) # TODO: change to --profiles-root
    parser.add_argument(
        '--url',
        default='https://brave.com',
        help='URL to navigate to (default: https://brave.com)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        default=False,
        help='Run browser in headless mode (default: False)'
    )
    parser.add_argument(
        '--page-load-timeout',
        type=int,
        default=30000,
        help='Timeout in milliseconds for page load (default: 30000)'
    )
    return parser.parse_args()

def launch_brave_with_profile(
        brave_path: str, 
        profile_path: str, 
        url: str, 
        headless: bool = False
) -> None:
    """
    Launch Brave browser with a specific profile and navigate to URL.
    
    Args:
        brave_path: Path to Brave executable
        profile_path: Path to profile directory
        url: URL to navigate to
        headless: Whether to run in headless mode
    """
    # Create profile directory if it doesn't exist
    profile_dir: Path = Path(profile_path)
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            executable_path=brave_path,
            headless=headless
        )
        time.sleep(3)
        context.close()


def main() -> None:
    """
        Main entry point for the smoke tester.
    """
    args = parse_arguments()
    
    launch_brave_with_profile(
        brave_path=args.brave_path,
        profile_path=args.profile_path,
        url=args.url,
        headless=args.headless
    )
    print("Test completed")


if __name__ == "__main__":
    main()