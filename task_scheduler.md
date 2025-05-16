## Automate Daily CSV Export Refresh

To schedule the reporting script to run every day at 02:00:

### Windows (Task Scheduler)

1. Open PowerShell **as Administrator**.
2. Run the following command:

   ```powershell
   schtasks /Create /SC DAILY /TN "RefreshExports" `
     /TR "powershell -ExecutionPolicy Bypass -File   Path to  --> refresh_reporting.ps1" `
     /ST 02:00
   ```