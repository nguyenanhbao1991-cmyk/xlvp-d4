<#
.SYNOPSIS
  Gỡ tác vụ chạy nền, tác vụ sao lưu và luật tường lửa của QL CBCS LAN.
  KHÔNG xoá mã nguồn, qlcbcs.env, CSDL hay các bản sao lưu.
#>
#Requires -RunAsAdministrator
param()
. "$PSScriptRoot\chung.ps1"

foreach ($ten in @($TEN_TAC_VU_MAY_CHU, $TEN_TAC_VU_SAO_LUU)) {
    if (Get-ScheduledTask -TaskName $ten -ErrorAction SilentlyContinue) {
        Stop-ScheduledTask -TaskName $ten -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $ten -Confirm:$false
        Ghi "Đã gỡ tác vụ $ten"
    }
}
Get-NetFirewallRule -DisplayName "QL CBCS LAN (TCP *" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
Ghi "Đã gỡ luật tường lửa QL CBCS LAN (nếu có)."
