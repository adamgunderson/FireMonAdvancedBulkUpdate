#!/usr/bin/python
import sys
import os
import importlib.util

def ensure_module(module_name):
    """Dynamically import a module by searching for it in potential site-packages locations"""
    # First try the normal import in case it's already in the path
    try:
        return __import__(module_name)
    except ImportError:
        pass
    
    # Get the current Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # Create a list of potential paths to check
    base_path = '/usr/lib/firemon/devpackfw/lib'
    potential_paths = [
        # Current Python version
        f"{base_path}/python{py_version}/site-packages",
        # Exact Python version with patch
        f"{base_path}/python{sys.version.split()[0]}/site-packages",
        # Try a range of nearby versions (for future-proofing)
        *[f"{base_path}/python3.{i}/site-packages" for i in range(8, 20)]
    ]
    
    # Try each path
    for path in potential_paths:
        if os.path.exists(path):
            if path not in sys.path:
                sys.path.append(path)
            try:
                return __import__(module_name)
            except ImportError:
                continue
    
    # If we get here, we couldn't find the module
    raise ImportError(f"Could not find module {module_name} in any potential site-packages location")

# Import required modules
requests = ensure_module("requests")
json = ensure_module("json")
urllib3 = ensure_module("urllib3")
getpass = ensure_module("getpass")
time = ensure_module("time")

# Continue with the rest of your script...
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Default FQDN as localhost
IP = input("FireMon app server IP or FQDN (default: localhost): >> ") or "localhost"
username = input("Username for FireMon UI account: >> ")
password = getpass.getpass('Password for FireMon UI account: >> ')

# Initialize session
session = requests.Session()
session.auth = (username, password)
session.headers = {'Content-Type': 'application/json'}

# Verify username/password and authenticate
logon_data = {
    'username': username,
    'password': password
}
verify_auth = session.post(f'https://{IP}/securitymanager/api/authentication/validate', data=json.dumps(logon_data), verify=False)

if verify_auth.status_code != 200:
    print("Authentication failed. Please check your username and/or password and try again.")
    sys.exit(1)

auth_status = verify_auth.json().get('authStatus', '')
if auth_status == 'AUTHORIZED':
    print("Authenticated successfully.")

    # Pagination setup
    page_size = 20  # 20 device packs per page
    current_page = 0
    total_device_packs = None
    selected_device_pack_id = None

    while True:
        # Fetch device packs from the correct endpoint (paginated)
        print(f"Fetching device packs (Page {current_page + 1})...")
        device_pack_url = f"https://{IP}/securitymanager/api/plugin/list/DEVICE_PACK.json?domainId=1&page={current_page}&pageSize={page_size}&search=&showHidden=true&sort=vendor&sort=deviceName"
        device_pack_response = session.get(device_pack_url, verify=False)

        if device_pack_response.status_code == 200:
            device_packs = device_pack_response.json().get('results', [])
            total_device_packs = device_pack_response.json().get('total', 0)

            if not device_packs:
                print("No device packs found.")
                sys.exit(1)

            # Display the device packs in two columns
            print("\nAvailable Device Packs (Page", current_page + 1, "):")
            for i in range(0, len(device_packs), 2):
                col1 = device_packs[i]
                col2 = device_packs[i + 1] if i + 1 < len(device_packs) else None
                col1_display = f"{col1.get('vendor', 'Unknown Vendor')} - {col1.get('deviceName', 'Unknown Device Pack')} (ID: {col1['id']})"
                col2_display = f"{col2.get('vendor', 'Unknown Vendor')} - {col2.get('deviceName', 'Unknown Device Pack')} (ID: {col2['id']})" if col2 else ""

                print(f"{col1_display:<55} {col2_display}")

            # Pagination controls
            action = input("\nSelect a device pack by entering its ID, or type 'n' for next page, 'p' for previous page: ").strip()

            if action.lower() == 'n':
                if (current_page + 1) * page_size >= total_device_packs:
                    print("You are already on the last page.")
                else:
                    current_page += 1
            elif action.lower() == 'p':
                if current_page == 0:
                    print("You are already on the first page.")
                else:
                    current_page -= 1
            elif action.isdigit():
                selected_device_pack_id = action
                break
            else:
                print("Invalid input. Please enter a valid device pack ID or 'n'/'p' for navigation.")
        else:
            print("Failed to retrieve device packs. Please check the API call or your permissions.")
            sys.exit(1)

    print(f"Selected Device Pack ID: {selected_device_pack_id}")

    # Menu for update_data options
    update_options = [
        ("access_key", "string"),
        ("aws_account_id", "string"),
        ("batchConfigRetrieval", "true/false"),
        ("changeMonitoringEnabled", "true/false"),
        ("checkForChangeEnabled", "true/false"),
        ("checkForChangeOnChangeDetection", "true/false"),
        ("client_id", "string"),
        ("commitAdminChange", "true/false"),
        ("deprecatedCA", "true/false"),
        ("disableVDOMCheck", "true/false"),
        ("doNotGenerateComments", "true/false"),
        ("fallbackAuthentication", "true/false"),
        ("flattenConfigFile", "true/false"),
        ("granularChange", "true/false"),
        ("key_id", "string"),
        ("layerTwoEnforcementInterfaces", "true/false"),
        ("logMonitoringEnabled", "true/false"),
        ("logMonitoringMethod", "syslog/hitcounter"),
        ("noPasswordDevice", "true/false"),
        ("normalizeApplicationDerivedServices", "true/false"),
        ("ntpServer", "string"),
        ("processNoInterfacePolicies", "true/false"),
        ("recommendChangesViaTheManager", "true/false"),
        ("resetSSHKeyValue", "true/false"),
        ("retrievalCallTimeOut", "integer"),
        ("retrievalMethod", "FromDevice/FromServer"),
        ("retrieveRoutesViaApi", "true/false"),
        ("retrieveSetSyntaxConfig", "true/false"),
        ("routesFromConfig", "true/false"),
        ("scheduledRetrievalEnabled", "true/false"),
        ("secret", "string"),
        ("serverAliveInterval", "integer"),
        ("skipApplicationFile", "true/false"),
        ("skipDynamicBlockListRetrieval", "true/false"),
        ("skipRoute", "true/false"),
        ("skipUserFileRetrieval", "true/false"),
        ("supportsFQDN", "true/false"),
        ("suppressFQDNCapabilities", "true/false"),
        ("tenant", "string"),
        ("trackUsageUsingHitCounters", "true/false"),
        ("useCLICommandGeneration", "true/false"),
        ("usePrivateConfig", "true/false"),
        ("useSpecialAccessList", "true/false"),
        ("versionSshFallback", "true/false")
    ]

    # Function to display the menu in two columns with larger spacing
    def display_menu(options):
        print("\nPlease choose the fields you want to configure (enter the numbers separated by commas):")
        for i in range(0, len(options), 2):
            col1 = f"{i+1}. {options[i][0]} ({options[i][1]})"
            col2 = f"{i+2}. {options[i+1][0]} ({options[i+1][1]})" if i + 1 < len(options) else ""
            print(f"{col1:<55} {col2}")

    # Display the menu and get user input
    display_menu(update_options)
    selected_options = input("\nEnter the numbers of the options you want to configure (e.g., 1,3,5): ").split(",")

    update_data = {}
    for option in selected_options:
        try:
            idx = int(option.strip()) - 1
            if idx < 0 or idx >= len(update_options):
                print(f"Invalid option number: {option}")
                continue

            option_name, option_type = update_options[idx]
            value = input(f"Enter value for {option_name} ({option_type}): ").strip()

            # Convert boolean and integer fields appropriately
            if option_type == "true/false":
                update_data[option_name] = value.lower() == "true"
            elif option_type == "integer":
                update_data[option_name] = int(value)
            else:
                # For string types and other types, keep as string
                update_data[option_name] = value
        except ValueError:
            print(f"Invalid input for option {option_name}. Skipping.")

    # Get the total number of devices for the selected device pack
    get_num = session.get(f'https://{IP}/securitymanager/api/domain/1/device/filter?pageSize=1&filter=devicepackids={selected_device_pack_id}', verify=False)
    total_dev = get_num.json().get('total', 0)
    pages = total_dev // 1000

    print(f"There are a total of {total_dev} devices that will be updated.")

    # Confirm to proceed
    answer = input("Enter y to continue: ")
    if answer.lower() == "y":
        for page in range(pages + 1):
            print(f"Running update script against page {page + 1} of {pages + 1}")
            get_data = session.get(f'https://{IP}/securitymanager/api/domain/1/device/filter?page={page}&pageSize=1000&filter=devicepackids={selected_device_pack_id}', verify=False)

            for item in get_data.json().get('results', []):
                # Update device settings
                item["extendedSettingsJson"].update(update_data)
                payload = json.dumps(item)
                device_id = item['id']
                devicename = item['name']

                updatedevice = session.put(f'https://{IP}/securitymanager/api/domain/1/device/{device_id}?manualRetrieval=false', data=payload, verify=False)
                print(f"Attempt to update settings for {devicename} (ID: {device_id}) resulted in status code: {updatedevice.status_code}")
    else:
        print("Operation cancelled.")
else:
    print("Authorization failed. Please check your credentials.")
    time.sleep(2)
