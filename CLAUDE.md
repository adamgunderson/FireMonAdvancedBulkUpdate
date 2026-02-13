# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-file Python CLI tool (`advancedBulkUpdate.py`) for bulk-updating device settings in FireMon Security Manager. It authenticates against the FireMon API, lets the user select a target (device pack or device group), choose configuration fields to modify, then applies those changes across all matching devices.

## Running

```bash
python3 advancedBulkUpdate.py
```

Interactive prompts collect: server address, credentials, target type (device pack vs device group), fields to update, and values. No command-line arguments.

## Architecture

The script is a single procedural file with no tests or build system. Key flow:

1. **Module loading** — `ensure_module()` dynamically searches FireMon's bundled Python site-packages (`/usr/lib/firemon/devpackfw/lib/python*/site-packages`) as a fallback when standard imports fail. This is critical for running on FireMon appliances.
2. **Authentication** — POST to `/securitymanager/api/authentication/validate`, then reuses a `requests.Session` with basic auth.
3. **Target selection** — Paginated browsing of device packs (`/securitymanager/api/plugin/list/DEVICE_PACK.json`) or device groups (`/securitymanager/api/siql/devicegroup/paged-search`).
4. **Field configuration** — User picks from `update_options` list (booleans, strings, integers, arrays) and enters values.
5. **Bulk update** — Iterates devices in pages of 1000. For device groups, fetches full device details via `/securitymanager/api/domain/1/device/{id}` before updating. Merges user settings into `extendedSettingsJson` and PUTs the full device object back.

## FireMon API Details

- Base URL pattern: `https://{IP}/securitymanager/api/...`
- All requests use `verify=False` (self-signed certs on appliances)
- Device filter endpoint: `/domain/1/device/filter?filter=devicepackids={id}` or SIQL search for device groups
- Device update: PUT `/domain/1/device/{id}?manualRetrieval=false` with full device JSON payload
- Settings are stored in the `extendedSettingsJson` dict on each device object

## Key Conventions

- The `update_options` list defines all configurable fields with their types — add new fields here when FireMon adds device pack settings
- Boolean values are stored as Python bools (not strings) in the payload
- Array fields (e.g., `limitRegions`) are stored as JSON arrays
- Pagination uses 0-indexed pages; display pages are 1-indexed
