# FireMonAdvancedBulkUpdate

## Usage Example
[admin@demo testing]$ python3 advancedBulkUpdate.py
FireMon app server IP or FQDN (default: localhost): >>
Username for FireMon UI account: >> adam
Password for FireMon UI account: >>
Authenticated successfully.
Fetching device packs (Page 1)...

Available Device Packs (Page 1 ):
AhnLab - TrusGuard Series (ID: 67)                                               Amazon - AWS Account (ID: 68)
Amazon - VPC (ID: 69)                                                            Amazon Web Services - AWS Account (ID: 127)
Amazon Web Services - AWS Organizations (ID: 146)                                Arista - EOS (ID: 155)
Aruba - CX (ID: 132)                                                             Aruba - Orchestrator (ID: 157)
Azure - Azure Subscription (ID: 99)                                              Azure - Azure vNet (ID: 100)
Blue Coat - ProxySG (ID: 47)                                                     Check Point - CMA (ID: 1)
Check Point - Edge Device (ID: 2)                                                Check Point - Firewall (ID: 3)
Check Point - Log Server (ID: 4)                                                 Check Point - MDS (ID: 5)
Check Point - R80 CMA (ID: 83)                                                   Check Point - R80 Edge Device (ID: 87)
Check Point - R80 Firewall (ID: 91)                                              Check Point - R80 MDS (ID: 88)

Select a device pack by entering its ID, or type 'n' for next page, 'p' for previous page: n
Fetching device packs (Page 2)...

Available Device Packs (Page 2 ):
Cisco - ACI (ID: 124)                                                            Cisco - ACI Tenant (ID: 125)
Cisco - ASA/FWSM (ID: 9)                                                         Cisco - ASA/FWSM Context (ID: 10)
Cisco - Firepower (ID: 79)                                                       Cisco - Firepower FDM (ID: 148)
Cisco - Firepower Management Center (FMC) (ID: 80)                               Cisco - IOS (ID: 7)
Cisco - IOS XR (ID: 89)                                                          Cisco - ISE (ID: 94)
Cisco - Meraki (ID: 118)                                                         Cisco - Meraki Network (ID: 119)
Cisco - Nexus (ID: 8)                                                            Cisco - Security Manager (CSM) (ID: 6)
Cisco - Viptela Tenant (ID: 145)                                                 Cisco - Viptela vManage (ID: 144)
Citrix - ADC (ID: 97)                                                            CloudGenix - CloudGenix Controller (ID: 122)
CloudGenix - CloudGenix Site (ID: 121)                                           F5 - BIG-IP (ID: 11)

Select a device pack by entering its ID, or type 'n' for next page, 'p' for previous page: 9
Selected Device Pack ID: 9

Please choose the fields you want to configure (enter the numbers separated by commas):
1. retrievalMethod (FromDevice/FromServer)              2. resetSSHKeyValue (true/false)
3. commitAdminChange (true/false)                       4. flattenConfigFile (true/false)
5. versionSshFallback (true/false)                      6. batchConfigRetrieval (true/false)
7. logMonitoringEnabled (true/false)                    8. retrievalCallTimeOut (integer)
9. checkForChangeEnabled (true/false)                   10. skipUserFileRetrieval (true/false)
11. changeMonitoringEnabled (true/false)                12. suppressFQDNCapabilities (true/false)
13. scheduledRetrievalEnabled (true/false)              14. trackUsageUsingHitCounters (true/false)
15. layerTwoEnforcementInterfaces (true/false)          16. recommendChangesViaTheManager (true/false)
17. skipDynamicBlockListRetrieval (true/false)          18. normalizeApplicationDerivedServices (true/false)
19. skipRoute (true/false)                              20. deprecatedCA (true/false)
21. supportsFQDN (true/false)                           22. routesFromConfig (true/false)
23. usePrivateConfig (true/false)                       24. serverAliveInterval (integer)
25. skipApplicationFile (true/false)                    26. useSpecialAccessList (true/false)
27. fallbackAuthentication (true/false)                 28. retrieveSetSyntaxConfig (true/false)
29. useCLICommandGeneration (true/false)

Enter the numbers of the options you want to configure (e.g., 1,3,5):29
Enter value for useCLICommandGeneration (true/false): true
There are a total of 5 devices that will be updated.
Enter y to continue: y
Running update script against page 1 of 1
Attempt to update settings for Cisco - ASA (ID: 1) resulted in status code: 204
Attempt to update settings for Cisco - ASA - 5506X (ID: 63) resulted in status code: 204
Attempt to update settings for Cisco ASA - automation 2 (ID: 351) resulted in status code: 204
Attempt to update settings for Cisco Live (ID: 1362) resulted in status code: 204
Attempt to update settings for Cisco - RSA-CiscoASA (ID: 32) resulted in status code: 204

