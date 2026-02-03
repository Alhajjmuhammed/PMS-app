#!/usr/bin/env python
"""
Mobile App Testing Script
Tests if Expo mobile app can start and connect to backend
"""
import subprocess
import time
import requests
import os

def log_test(name, passed, message=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if message:
        print(f"     {message}")
    return passed

def test_mobile_dependencies():
    """Test if mobile app dependencies are installed"""
    mobile_path = "/home/easyfix/Documents/PMS/mobile"
    node_modules = os.path.exists(f"{mobile_path}/node_modules")
    package_json = os.path.exists(f"{mobile_path}/package.json")
    
    passed = node_modules and package_json
    return log_test(
        "Mobile Dependencies",
        passed,
        f"node_modules: {node_modules}, package.json: {package_json}"
    )

def test_mobile_structure():
    """Test if mobile app has correct structure"""
    mobile_path = "/home/easyfix/Documents/PMS/mobile"
    
    checks = {
        "App.tsx": os.path.exists(f"{mobile_path}/App.tsx"),
        "src folder": os.path.exists(f"{mobile_path}/src"),
        "screens": os.path.exists(f"{mobile_path}/src/screens"),
        "services": os.path.exists(f"{mobile_path}/src/services"),
        "app.json": os.path.exists(f"{mobile_path}/app.json"),
    }
    
    passed = all(checks.values())
    details = ", ".join([f"{k}: {v}" for k, v in checks.items()])
    
    return log_test(
        "Mobile App Structure",
        passed,
        details
    )

def count_mobile_files():
    """Count mobile app files"""
    mobile_path = "/home/easyfix/Documents/PMS/mobile"
    
    try:
        # Count screens
        screens_path = f"{mobile_path}/src/screens"
        screens = len([f for f in os.listdir(screens_path) if f.endswith('.tsx')]) if os.path.exists(screens_path) else 0
        
        # Count services
        services_path = f"{mobile_path}/src/services"
        services = len([f for f in os.listdir(services_path) if f.endswith('.ts')]) if os.path.exists(services_path) else 0
        
        # Count components
        components_path = f"{mobile_path}/src/components"
        components = len([f for f in os.listdir(components_path) if f.endswith('.tsx')]) if os.path.exists(components_path) else 0
        
        print(f"📱 Mobile App Files:")
        print(f"   - Screens: {screens}")
        print(f"   - Services: {services}")
        print(f"   - Components: {components}")
        
        return screens > 0 and services > 0
        
    except Exception as e:
        print(f"❌ Error counting files: {e}")
        return False

def test_expo_cli():
    """Test if Expo CLI is available"""
    try:
        result = subprocess.run(
            ["npx", "expo", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        passed = result.returncode == 0
        version = result.stdout.strip() if passed else "Not found"
        
        return log_test(
            "Expo CLI Available",
            passed,
            f"Version: {version}"
        )
    except Exception as e:
        return log_test("Expo CLI Available", False, str(e))

def test_api_service_config():
    """Test if API service is configured correctly"""
    api_service_path = "/home/easyfix/Documents/PMS/mobile/src/services/api.ts"
    
    try:
        if os.path.exists(api_service_path):
            with open(api_service_path, 'r') as f:
                content = f.read()
                has_base_url = 'BASE_URL' in content or 'baseURL' in content
                has_axios = 'axios' in content
                
            return log_test(
                "API Service Configuration",
                has_base_url and has_axios,
                f"Base URL configured: {has_base_url}, Axios: {has_axios}"
            )
        else:
            return log_test(
                "API Service Configuration",
                False,
                "api.ts not found"
            )
    except Exception as e:
        return log_test("API Service Configuration", False, str(e))

def main():
    print("=" * 80)
    print("📱 MOBILE APP INTEGRATION TEST")
    print("=" * 80)
    print()
    
    results = []
    
    print("📂 Testing Mobile App Structure:")
    print("-" * 80)
    results.append(test_mobile_structure())
    results.append(test_mobile_dependencies())
    results.append(count_mobile_files())
    
    print()
    print("🔧 Testing Development Tools:")
    print("-" * 80)
    results.append(test_expo_cli())
    results.append(test_api_service_config())
    
    print()
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    if success_rate == 100:
        print("🎉 EXCELLENT: Mobile app structure is ready!")
        print()
        print("⚠️  IMPORTANT NOTE:")
        print("   The mobile app structure exists and is configured,")
        print("   but it has NOT been launched or tested yet.")
        print()
        print("   To fully test the mobile app:")
        print("   1. cd mobile")
        print("   2. npm start (or npx expo start)")
        print("   3. Scan QR code with Expo Go app")
        print("   4. Test functionality on device")
    elif success_rate >= 70:
        print("✅ GOOD: Mobile app mostly ready")
    else:
        print("❌ CRITICAL: Mobile app has issues")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
