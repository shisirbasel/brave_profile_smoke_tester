from playwright.sync_api import sync_playwright
from pathlib import Path
import argparse
import time


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Brave Profile Smoke Tester - Test multiple Brave Profiles"
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
        default='https://brave.com',
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
            time.sleep(1)
            context.close()


def main() -> None:
    args = parse_arguments()
    profiles = find_profiles(args.profiles_root)

    if not profiles:
        print("No profiles found.")
        return

    print("Testing profiles:")

    for profile in profiles:
        print(f"  Launching profile: {profile}")
        try:
            launch_brave_with_profile(
                brave_path=args.brave_path,
                profile_path=profile,
                url=args.url,
                headless=args.headless,
                timeout=args.page_load_timeout
            )
            print(f"  Profile {profile} -> PASS")
        except Exception as e:
            print(f"  Profile {profile} -> FAIL ({e})")

    print("All profiles tested")


if __name__ == "__main__":
    main()
