#!/usr/bin/python
# advancedBulkUpdate.py
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
    
    # Ask user to choose between device packs or device groups
    print("\n" + "="*60)
    print("Select target type:")
    print("1. Device Packs")
    print("2. Device Groups")
    print("="*60)
    
    target_choice = input("Enter your choice (1 or 2): ").strip()
    
    if target_choice == "1":
        # Device Packs workflow (original functionality)
        print("\nYou selected: Device Packs")
        
        # Pagination setup
        page_size = 20  # 20 device packs per page
        current_page = 0
        total_device_packs = None
        selected_device_pack_id = None

        while True:
            # Fetch device packs from the correct endpoint (paginated)
            print(f"\nFetching device packs (Page {current_page + 1})...")
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
        selected_target_id = selected_device_pack_id
        filter_type = "devicepackids"
        
    elif target_choice == "2":
        # Device Groups workflow
        print("\nYou selected: Device Groups")
        
        # Pagination setup
        page_size = 20  # 20 device groups per page
        current_page = 0
        total_device_groups = None
        selected_device_group_id = None

        while True:
            # Fetch device groups from the API endpoint (paginated)
            print(f"\nFetching device groups (Page {current_page + 1})...")
            device_group_url = f"https://{IP}/securitymanager/api/siql/devicegroup/paged-search?q=domain%7Bid%3D1%7D&page={current_page}&pageSize={page_size}&sortdir=asc&sort=name"
            device_group_response = session.get(device_group_url, verify=False)

            if device_group_response.status_code == 200:
                device_groups = device_group_response.json().get('results', [])
                total_device_groups = device_group_response.json().get('total', 0)

                if not device_groups:
                    print("No device groups found.")
                    sys.exit(1)

                # Display the device groups in two columns
                print("\nAvailable Device Groups (Page", current_page + 1, "):")
                for i in range(0, len(device_groups), 2):
                    col1 = device_groups[i]
                    col2 = device_groups[i + 1] if i + 1 < len(device_groups) else None
                    col1_display = f"{col1.get('name', 'Unknown Group')} (ID: {col1['id']})"
                    col2_display = f"{col2.get('name', 'Unknown Group')} (ID: {col2['id']})" if col2 else ""

                    print(f"{col1_display:<55} {col2_display}")

                # Pagination controls
                action = input("\nSelect a device group by entering its ID, or type 'n' for next page, 'p' for previous page: ").strip()

                if action.lower() == 'n':
                    if (current_page + 1) * page_size >= total_device_groups:
                        print("You are already on the last page.")
                    else:
                        current_page += 1
                elif action.lower() == 'p':
                    if current_page == 0:
                        print("You are already on the first page.")
                    else:
                        current_page -= 1
                elif action.isdigit():
                    selected_device_group_id = action
                    break
                else:
                    print("Invalid input. Please enter a valid device group ID or 'n'/'p' for navigation.")
            else:
                print("Failed to retrieve device groups. Please check the API call or your permissions.")
                sys.exit(1)

        print(f"Selected Device Group ID: {selected_device_group_id}")
        selected_target_id = selected_device_group_id
        filter_type = "devicegroupids"
        
    else:
        print("Invalid choice. Please run the script again and select 1 or 2.")
        sys.exit(1)

    # Menu for update_data options - Updated with all fields including arrays
    update_options = [
        ("access_key", "string"),
        ("aws_account_id", "string"),
        ("batchConfigRetrieval", "true/false"),
        ("changeMonitoringEnabled", "true/false"),
        ("checkForChange.intervalInMinutes", "integer"), 
        ("checkForChangeEnabled", "true/false"),
        ("checkForChangeOnChangeDetection", "true/false"),
        ("client_id", "string"),
        ("commitAdminChange", "true/false"),
        ("default_region", "string"),
        ("deprecatedCA", "true/false"),
        ("disableVDOMCheck", "true/false"),
        ("doNotGenerateComments", "true/false"),
        ("fallbackAuthentication", "true/false"),
        ("flattenConfigFile", "true/false"),
        ("flowLogSearchWindow", "integer"),
        ("granularChange", "true/false"),
        ("hitCounterRetrievalInterval", "integer"),
        ("key_id", "string"),
        ("layerTwoEnforcementInterfaces", "true/false"),
        ("limitRegions", "array"),
        ("loggingPlugin", "string"),
        ("logMonitoringEnabled", "true/false"),
        ("logMonitoringMethod", "string"),
        ("monitoringPlugin", "string"),
        ("noPasswordDevice", "true/false"),
        ("normalizeApplicationDerivedServices", "true/false"),
        ("ntpServer", "string"),
        ("processNoInterfacePolicies", "true/false"),
        ("recommendChangesViaTheManager", "true/false"),
        ("resetSSHKeyValue", "true/false"),
        ("retrievalCallTimeOut", "integer"),
        ("retrievalMethod", "string"),
        ("retrievalPlugin", "string"),
        ("retrieveRoutesViaApi", "true/false"),
        ("retrieveSetSyntaxConfig", "true/false"),
        ("routesFromConfig", "true/false"),
        ("scheduledRetrievalEnabled", "true/false"),
        ("secret", "string"),
        ("serverAliveInterval", "integer"),
        ("serverCertSecurity", "string"),
        ("skipApplicationFile", "true/false"),
        ("skipDynamicBlockListRetrieval", "true/false"),
        ("skipRoute", "true/false"),
        ("skipUserFileRetrieval", "true/false"),
        ("supportsFQDN", "true/false"),
        ("suppressFQDNCapabilities", "true/false"),
        ("tenant", "string"),
        ("trackUsageUsingHitCounters", "true/false"),
        ("useCLICommandGeneration", "true/false"),
        ("use_default_region_only", "true/false"),
        ("use_role", "true/false"),
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
            
            if option_type == "array":
                # Handle array input
                print(f"\nEnter values for {option_name} (comma-separated):")
                if option_name == "limitRegions":
                    print("Example: us-east-1,us-east-2,us-west-1,us-west-2")
                    print("Available regions: us-east-1, us-east-2, us-west-1, us-west-2, af-south-1, ap-east-1,")
                    print("ap-south-1, ap-northeast-1, ap-northeast-2, ap-northeast-3, ap-southeast-1,")
                    print("ap-southeast-2, ca-central-1, eu-central-1, eu-west-1, eu-west-2, eu-west-3,")
                    print("eu-south-1, eu-north-1, me-south-1, sa-east-1, cn-north-1, cn-northwest-1,")
                    print("us-gov-east-1, us-gov-west-1")
                value = input(f"Enter values: ").strip()
                # Split by comma and strip whitespace from each element
                array_values = [v.strip() for v in value.split(",") if v.strip()]
                update_data[option_name] = array_values
            elif option_type == "true/false":
                # Handle boolean input
                value = input(f"Enter value for {option_name} (true/false): ").strip()
                update_data[option_name] = value.lower() == "true"
            elif option_type == "integer":
                # Handle integer input
                value = input(f"Enter value for {option_name} (integer): ").strip()
                update_data[option_name] = int(value)
            else:
                # Handle string input
                if option_name == "logMonitoringMethod":
                    print("Options: syslog, hitcounter, Hit counters")
                elif option_name == "retrievalMethod":
                    print("Options: FromDevice, FromServer")
                elif option_name == "serverCertSecurity":
                    print("Options: VERIFY_NONE, VERIFY_HOSTNAME, VERIFY_ALL")
                value = input(f"Enter value for {option_name}: ").strip()
                update_data[option_name] = value
        except ValueError:
            print(f"Invalid input for option {option_name}. Skipping.")

    # Display the configuration that will be applied
    print("\n" + "="*60)
    print("Configuration to be applied:")
    print("="*60)
    for key, value in update_data.items():
        if isinstance(value, list):
            print(f"{key}: {', '.join(value)}")
        else:
            print(f"{key}: {value}")
    print("="*60)

    # Get the total number of devices for the selected target
    if target_choice == "1":
        # Device pack filter
        get_num = session.get(f'https://{IP}/securitymanager/api/domain/1/device/filter?pageSize=1&filter={filter_type}={selected_target_id}', verify=False)
    else:
        # Device group - use SIQL search
        get_num = session.get(f'https://{IP}/securitymanager/api/siql/device/paged-search?q=devicegroup%7Bid%3D{selected_target_id}%7D&page=0&pageSize=1', verify=False)
    
    total_dev = get_num.json().get('total', 0)
    pages = total_dev // 1000

    print(f"\nThere are a total of {total_dev} devices that will be updated.")

    # Confirm to proceed
    answer = input("Enter y to continue: ")
    if answer.lower() == "y":
        for page in range(pages + 1):
            print(f"Running update script against page {page + 1} of {pages + 1}")
            
            if target_choice == "1":
                # Device pack filter
                get_data = session.get(f'https://{IP}/securitymanager/api/domain/1/device/filter?page={page}&pageSize=1000&filter={filter_type}={selected_target_id}', verify=False)
            else:
                # Device group - use SIQL search
                get_data = session.get(f'https://{IP}/securitymanager/api/siql/device/paged-search?q=devicegroup%7Bid%3D{selected_target_id}%7D&page={page}&pageSize=1000', verify=False)

            for item in get_data.json().get('results', []):
                device_id = item['id']
                devicename = item['name']
                
                # For device groups, fetch the full device details to ensure we have all required fields
                if target_choice == "2":
                    # Get the complete device information from the device API
                    device_response = session.get(f'https://{IP}/securitymanager/api/domain/1/device/{device_id}', verify=False)
                    
                    if device_response.status_code == 200:
                        # Use the full device data instead of the SIQL result
                        item = device_response.json()
                    else:
                        print(f"Failed to fetch details for {devicename} (ID: {device_id}) - Status code: {device_response.status_code}")
                        continue
                
                # Update device settings
                if "extendedSettingsJson" not in item:
                    item["extendedSettingsJson"] = {}
                
                item["extendedSettingsJson"].update(update_data)
                
                payload = json.dumps(item)

                updatedevice = session.put(f'https://{IP}/securitymanager/api/domain/1/device/{device_id}?manualRetrieval=false', data=payload, verify=False)
                
                # Check for successful status codes (200-299 range)
                if 200 <= updatedevice.status_code < 300:
                    print(f"Successfully updated settings for {devicename} (ID: {device_id}) - Status code: {updatedevice.status_code}")
                else:
                    print(f"Failed to update {devicename} (ID: {device_id}) - Status code: {updatedevice.status_code}")
                    if updatedevice.text:
                        print(f"  Error details: {updatedevice.text}")
    else:
        print("Operation cancelled.")
else:
    print("Authorization failed. Please check your credentials.")
    time.sleep(2)
