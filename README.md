DNS Tool Pro
User Guide (README)

====================================================

1) HOW TO INSTALL

Option A: Using Installer (Recommended)
----------------------------------------
1. Run "DNS_Tool_Setup.exe"
2. Click "Next"
3. Choose installation directory (default is recommended)
   Example:
   C:\Program Files\DNS Tool Pro\
4. Click "Install"
5. After installation completes, click "Finish"
6. The tool will be available in:
   - Desktop shortcut
   - Start Menu

Option B: Portable Version (Manual)
-----------------------------------
1. Extract the ZIP folder (if provided)
2. Make sure these files are in the same folder:
   - dns-check-tool.exe
   - dns.txt
3. Run dns-check-tool.exe directly
4. Do NOT remove or rename dns.txt

IMPORTANT NOTES:
- dns.txt must always be in the same directory as the executable
- If dns.txt is missing, the tool will not run properly
- No internet installation is required for the tool itself

====================================================

2) HOW TO USE THE TOOL

Step 1: Run the application
---------------------------
Open "DNS Tool Pro" from Desktop or Start Menu
or run dns-check-tool.exe directly

Step 2: Enter domain
--------------------
You will see:
Enter domain:

Examples:
google.com
cloudflare.com
example.com

You may also use quick switches:
google.com -a    → A Record lookup
google.com -mx   → MX Record lookup

If no switch is provided, the tool will ask you to choose:
1) A Record
2) MX Record

Step 3: Wait for results
------------------------
The tool will:
- Test all DNS servers in dns.txt
- Check reachability
- Resolve domain records
- Measure response time (latency)

Step 4: View results
--------------------
Results are shown in a table with:
- DNS Server IP
- PTR / Name
- Reachability status
- Resolution status (YES/NO)
- Resolved IP(s)
- Latency (ms)

Results are automatically sorted by fastest response time.

Step 5: Summary
---------------
At the end, a summary will be displayed:
- Total DNS servers tested
- How many responded successfully
- How many failed
- Average latency
- Fastest DNS server

Step 6: Restart or Exit
-----------------------
After completion:
- Press ENTER → Run again
- Press ESC → Exit application

====================================================

DNS LIST CONFIGURATION (dns.txt)

- The file "dns.txt" contains the list of DNS servers used by the tool
- Each DNS server must be written on a separate line
- You can freely EDIT this file without modifying the program

You are allowed to:
- Add new DNS servers
- Remove existing DNS servers
- Replace DNS servers with your own custom list

Example format:
----------------
8.8.8.8
8.8.4.4
1.1.1.1
9.9.9.9

IMPORTANT:
- One IP per line only
- Do not leave empty or invalid lines
- Invalid DNS entries may slow down or affect results

====================================================

TROUBLESHOOTING

- If the tool closes immediately:
  → Ensure dns.txt exists in the same folder as the exe

- If no DNS servers respond:
  → Check your internet connection
  → Verify DNS list in dns.txt

- If domain is invalid:
  → Ensure correct format (e.g. google.com)

====================================================

DNS Tool Pro
Developed by Aryogen Pharmed Co - IT Department