"""
Deployment Verification Script for Enhanced Rumble Bot on Render
"""
import requests
import sys
import time
from typing import Dict, Any


def check_health_endpoint(url: str) -> Dict[str, Any]:
    """Check the health endpoint of the deployed service"""
    try:
        print(f"🔍 Checking health endpoint: {url}")
        response = requests.get(f"{url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check successful!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Timestamp: {data.get('timestamp', 'unknown')}")
            return {"success": True, "data": data}
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return {"success": False, "error": str(e)}


def verify_telegram_bot(bot_token: str) -> Dict[str, Any]:
    """Verify Telegram bot is accessible"""
    try:
        print("🤖 Verifying Telegram bot...")
        api_url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print("✅ Telegram bot verification successful!")
                print(f"   Bot Name: {bot_info.get('first_name', 'Unknown')}")
                print(f"   Username: @{bot_info.get('username', 'Unknown')}")
                return {"success": True, "data": bot_info}
            else:
                print(f"❌ Telegram API error: {data.get('description', 'Unknown')}")
                return {"success": False, "error": data.get('description', 'Unknown')}
        else:
            print(f"❌ Telegram API failed with status: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Telegram verification failed: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Main verification function"""
    print("🧪 Enhanced Rumble Bot - Deployment Verification")
    print("=" * 60)
    
    # Get deployment URL
    render_url = input("Enter your Render service URL (e.g., https://enhanced-rumble-bot.onrender.com): ").strip()
    if not render_url:
        print("❌ No URL provided")
        return False
    
    # Remove trailing slash
    render_url = render_url.rstrip('/')
    
    print(f"\n🎯 Verifying deployment at: {render_url}")
    
    # Check 1: Health endpoint
    print("\n" + "="*40)
    print("Test 1: Health Endpoint Check")
    health_result = check_health_endpoint(render_url)
    
    if not health_result["success"]:
        print("\n⚠️ Health check failed. This might indicate:")
        print("   - Service is still starting up (wait a few minutes)")
        print("   - Build failed (check Render logs)")
        print("   - Environment variables not set correctly")
        print("   - Port configuration issue")
        return False
    
    # Check 2: Telegram bot verification (optional)
    print("\n" + "="*40)
    print("Test 2: Telegram Bot Verification (Optional)")
    
    bot_token = input("Enter your Telegram bot token (or press Enter to skip): ").strip()
    if bot_token:
        telegram_result = verify_telegram_bot(bot_token)
        if not telegram_result["success"]:
            print("\n⚠️ Telegram bot verification failed.")
            print("   This doesn't affect deployment but check your bot token.")
    else:
        print("⏭️ Skipping Telegram bot verification")
    
    # Final status
    print("\n" + "="*60)
    print("🎉 DEPLOYMENT VERIFICATION COMPLETE!")
    print("=" * 60)
    
    if health_result["success"]:
        print("✅ Your Enhanced Rumble Bot is successfully deployed!")
        print(f"🌐 Service URL: {render_url}")
        print(f"🔍 Health Check: {render_url}/health")
        print("\n📱 Next Steps:")
        print("   1. Test your Telegram bot by sending it a message")
        print("   2. Try uploading a small video file")
        print("   3. Monitor the Render logs for any issues")
        print("   4. Enjoy the enhanced features!")
        return True
    else:
        print("❌ Deployment verification failed")
        print("   Check the Render dashboard logs for more details")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Verification cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        sys.exit(1)
