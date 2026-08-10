# check_server.py
import requests
import sys

def check_server():
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running on http://localhost:5000")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on http://localhost:5000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server connection timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if not check_server():
        print("\nTo start the server:")
        print("1. Open a new terminal")
        print("2. Navigate to your project folder")
        print("3. Run: python app.py")
        print("4. Wait for 'Running on http://127.0.0.1:5000'")
        print("5. Run this script again or run test_data.py")
        sys.exit(1)
    else:
        print("\nYou can now run: python test_data.py")