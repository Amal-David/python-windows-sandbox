# Windows Sandbox Setup and Troubleshooting Guide

## Table of Contents
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [System Validation](#system-validation)
- [FAQ](#faq)

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 Pro/Enterprise/Education version 1903 (Build 18362) or later
- **Memory**: 4 GB RAM (8 GB recommended)
- **Storage**: 1 GB available disk space
- **CPU**: 2 cores minimum (4 cores recommended)
- **Architecture**: AMD64/x64
- **BIOS**: Virtualization capabilities enabled

### Supported Windows Editions
✅ **Supported:**
- Windows 10/11 Pro
- Windows 10/11 Enterprise
- Windows 10/11 Education
- Windows 10/11 Pro for Workstations

❌ **Not Supported:**
- Windows 10/11 Home
- Windows 10/11 S Mode
- Windows Server editions

## Installation Guide

### Step 1: Check System Compatibility

Run our system checker to verify your system meets all requirements:

```bash
# After installing the package
wsb check-system
```

Or use Python:

```python
from windows_sandbox_manager.utils.system_check import check_requirements, SystemChecker

result = check_requirements()
SystemChecker.print_requirements_report(result)
```

### Step 2: Enable Virtualization in BIOS

1. **Restart your computer** and enter BIOS/UEFI settings
   - Usually by pressing F2, F10, F12, or DEL during boot
   - Check your motherboard manual for specific key

2. **Find Virtualization Settings**
   - Look for: "Intel VT-x", "AMD-V", "SVM", "Virtualization Technology"
   - Location varies by manufacturer:
     - **Intel**: Advanced → CPU Configuration
     - **AMD**: Advanced → CPU Configuration or SVM Mode
     - **ASUS**: Advanced → CPU Configuration
     - **MSI**: OC → CPU Features
     - **Gigabyte**: M.I.T → Advanced Frequency Settings

3. **Enable Virtualization**
   - Set to "Enabled"
   - Save and exit BIOS (usually F10)

### Step 3: Enable Windows Sandbox Feature

#### Method 1: GUI (Recommended for beginners)

1. Press `Win + R`, type `optionalfeatures`, press Enter
2. Find "Windows Sandbox" in the list
3. Check the box next to it
4. Click OK
5. Restart when prompted

#### Method 2: PowerShell (Run as Administrator)

```powershell
# Check if feature is available
Get-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM"

# Enable Windows Sandbox
Enable-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM" -All

# Restart computer
Restart-Computer
```

#### Method 3: Command Prompt (Run as Administrator)

```cmd
# Enable Windows Sandbox
dism /online /enable-feature /featurename:"Containers-DisposableClientVM" /all

# Restart computer
shutdown /r /t 0
```

### Step 4: Verify Installation

After restart, verify Windows Sandbox is working:

```powershell
# Test Windows Sandbox manually
WindowsSandbox.exe

# Or use our tool
wsb check-system
```

## Common Issues and Solutions

### Issue 1: "Windows Sandbox feature not enabled"

**Error Message:**
```
SandboxCreationError: Windows Sandbox feature is not enabled on this system
```

**Solutions:**

1. **Enable the feature** (see Step 3 above)

2. **If feature won't enable**, check:
   - Windows edition (must be Pro/Enterprise/Education)
   - Windows version (must be 1903 or later)
   - Virtualization is enabled in BIOS

3. **If feature is grayed out:**
   ```powershell
   # Run as Administrator
   bcdedit /set hypervisorlaunchtype auto
   Restart-Computer
   ```

### Issue 2: "Insufficient privileges"

**Error Message:**
```
SandboxError: Access denied. Administrator privileges required
```

**Solutions:**

1. **Run as Administrator:**
   - Right-click on your terminal/command prompt
   - Select "Run as administrator"
   - Or use: `Start-Process powershell -Verb RunAs`

2. **For Python scripts:**
   ```python
   import ctypes
   import sys
   
   def is_admin():
       try:
           return ctypes.windll.shell32.IsUserAnAdmin()
       except:
           return False
   
   if not is_admin():
       # Re-run the program with admin rights
       ctypes.windll.shell32.ShellExecuteW(
           None, "runas", sys.executable, " ".join(sys.argv), None, 1
       )
   ```

3. **Permanent solution:**
   - Add your user to the "Hyper-V Administrators" group:
   ```powershell
   Add-LocalGroupMember -Group "Hyper-V Administrators" -Member $env:USERNAME
   ```

### Issue 3: "Windows version not supported"

**Error Message:**
```
SystemError: Windows 10 Home edition does not support Windows Sandbox
```

**Solutions:**

1. **Check your Windows edition:**
   ```powershell
   Get-ComputerInfo | select WindowsProductName, WindowsVersion, OsHardwareAbstractionLayer
   ```

2. **Upgrade Windows Home to Pro:**
   - Go to Settings → Update & Security → Activation
   - Click "Change product key" or "Go to Store"
   - Purchase and install Windows Pro upgrade

3. **For older Windows versions:**
   - Update to Windows 10 version 1903 or later
   - Settings → Update & Security → Windows Update
   - Check for updates

### Issue 4: "System resources insufficient"

**Error Message:**
```
ResourceError: Insufficient memory. 4GB minimum required, 8GB recommended
```

**Solutions:**

1. **Check available resources:**
   ```powershell
   # Check memory
   Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property capacity -Sum | 
       Foreach {"{0:N2}" -f ([math]::round(($_.Sum / 1GB),2))}
   
   # Check CPU cores
   (Get-CimInstance Win32_Processor).NumberOfCores
   
   # Check disk space
   Get-PSDrive C | Select-Object Used,Free
   ```

2. **Free up resources:**
   - Close unnecessary applications
   - Disable startup programs
   - Clean temporary files: `cleanmgr /sagerun:1`

3. **Adjust sandbox configuration:**
   ```python
   config = SandboxConfig(
       name="lightweight-sandbox",
       memory_mb=2048,  # Reduce memory allocation
       cpu_cores=1       # Reduce CPU cores
   )
   ```

### Issue 5: "Virtualization not enabled"

**Error Message:**
```
VirtualizationError: CPU virtualization (VT-x/AMD-V) is not enabled
```

**Solutions:**

1. **Check virtualization status:**
   ```powershell
   Get-ComputerInfo -property "HyperVRequirements*"
   ```

2. **Enable in BIOS** (see Step 2 above)

3. **Check if Hyper-V conflicts:**
   ```powershell
   # Disable Hyper-V if conflicting
   Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All
   
   # Or set to auto start
   bcdedit /set hypervisorlaunchtype auto
   ```

### Issue 6: "PowerShell execution policy"

**Error Message:**
```
PSSecurityException: Script execution is disabled on this system
```

**Solution:**
```powershell
# Check current policy
Get-ExecutionPolicy

# Set to allow scripts (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or temporarily bypass
powershell -ExecutionPolicy Bypass -File yourscript.ps1
```

## System Validation

### Built-in Validation

The library includes automatic validation before sandbox creation:

```python
from windows_sandbox_manager import SandboxManager
from windows_sandbox_manager.utils.system_check import verify_sandbox_ready

# Quick check
if not verify_sandbox_ready():
    print("System not ready for Windows Sandbox")
    # Run detailed check
    from windows_sandbox_manager.utils.system_check import check_requirements, SystemChecker
    result = check_requirements()
    SystemChecker.print_requirements_report(result)
    sys.exit(1)

# Proceed with sandbox creation
manager = SandboxManager()
```

### CLI System Check

```bash
# Full system check
wsb check-system

# Quick validation
wsb validate

# Verbose output
wsb check-system --verbose
```

### Programmatic Validation

```python
from windows_sandbox_manager.utils.system_check import SystemChecker, check_requirements

def validate_and_report():
    result = check_requirements()
    
    if not result.can_run_sandbox:
        print("❌ System is not ready for Windows Sandbox")
        
        # Show specific issues
        for req in result.requirements:
            if req.status == RequirementStatus.FAILED:
                print(f"\n{req.name}:")
                print(f"  Problem: {req.message}")
                if req.fix_instructions:
                    print(f"  Solution: {req.fix_instructions}")
        
        return False
    
    print("✅ System is ready for Windows Sandbox")
    return True

# Use in your application
if not validate_and_report():
    sys.exit(1)
```

## FAQ

### Q: Can I run Windows Sandbox on Windows Home?
**A:** No, Windows Sandbox requires Pro, Enterprise, or Education editions. You need to upgrade to use this feature.

### Q: Does Windows Sandbox work in virtual machines?
**A:** Yes, but you need:
- Nested virtualization support
- For Hyper-V VMs: `Set-VMProcessor -VMName <VMName> -ExposeVirtualizationExtensions $true`
- For VMware: Enable "Virtualize Intel VT-x/EPT or AMD-V/RVI"
- For VirtualBox: Limited support, not recommended

### Q: Can I run multiple sandboxes simultaneously?
**A:** Yes, but each sandbox consumes resources. Ensure you have sufficient RAM and CPU cores.

### Q: Why does sandbox creation fail even after enabling the feature?
**A:** Common causes:
1. Pending Windows updates
2. Corrupted Windows Sandbox installation
3. Group Policy restrictions
4. Antivirus interference

Try:
```powershell
# Repair Windows Sandbox
dism /online /cleanup-image /restorehealth
sfc /scannow

# Re-enable feature
Disable-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM"
Restart-Computer
Enable-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM" -All
Restart-Computer
```

### Q: How do I completely uninstall Windows Sandbox?
**A:**
```powershell
# Disable the feature
Disable-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM"

# Clean up
Remove-Item -Path "$env:LOCALAPPDATA\Packages\Microsoft.Windows.Sandbox_*" -Recurse -Force
```

## Getting Help

If you encounter issues not covered here:

1. **Run diagnostics:**
   ```bash
   wsb diagnose > diagnostics.txt
   ```

2. **Check logs:**
   - Windows Sandbox logs: `%LOCALAPPDATA%\Packages\Microsoft.Windows.Sandbox_8wekyb3d8bbwe\LocalState`
   - Event Viewer: Applications and Services Logs → Microsoft → Windows → Sandbox

3. **Report issues:**
   - GitHub: https://github.com/Amal-David/python-windows-sandbox/issues
   - Include output from `wsb check-system` and any error messages

## Additional Resources

- [Microsoft Windows Sandbox Documentation](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-sandbox/windows-sandbox-overview)
- [Hyper-V and Virtualization](https://docs.microsoft.com/en-us/virtualization/)
