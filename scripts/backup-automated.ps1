# Hotel PMS - Backup Automation with Windows Task Scheduler
# PowerShell script for automated backups on Windows

# Configuration
$ProjectRoot = "C:\Users\alhaj\OneDrive\Documents\Projects\PMS-app"
$BackendPath = "$ProjectRoot\backend"
$BackupRoot = "$ProjectRoot\backups"
$RetentionDays = 30

# Load .env file
if (Test-Path "$BackendPath\.env") {
    Get-Content "$BackendPath\.env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.+)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DateDir = Get-Date -Format "yyyy-MM-dd"

# Backup directories
$DbBackupDir = "$BackupRoot\database\$DateDir"
$MediaBackupDir = "$BackupRoot\media\$DateDir"
$LogFile = "$BackupRoot\backup.log"

# Create directories
New-Item -ItemType Directory -Force -Path $DbBackupDir | Out-Null
New-Item -ItemType Directory -Force -Path $MediaBackupDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $LogFile) | Out-Null

function Write-Log {
    param($Message)
    $LogMessage = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

function Backup-Database {
    Write-Log "Starting database backup..."
    
    # For SQLite
    if ($env:DATABASE_ENGINE -like "*sqlite3*") {
        $DbFile = "$BackendPath\$($env:DATABASE_NAME)"
        if (Test-Path $DbFile) {
            $BackupFile = "$DbBackupDir\db_$Timestamp.sqlite3"
            Copy-Item -Path $DbFile -Destination $BackupFile
            
            # Compress
            Compress-Archive -Path $BackupFile -DestinationPath "$BackupFile.zip" -Force
            Remove-Item $BackupFile
            
            Write-Log "Database backup completed: $BackupFile.zip"
        }
    }
    # For PostgreSQL
    else {
        $DbName = $env:DATABASE_NAME
        $DbUser = $env:DATABASE_USER
        $DbHost = $env:DATABASE_HOST
        $DbPort = $env:DATABASE_PORT
        $env:PGPASSWORD = $env:DATABASE_PASSWORD
        
        $BackupFile = "$DbBackupDir\${DbName}_$Timestamp.sql"
        
        & pg_dump -h $DbHost -p $DbPort -U $DbUser -d $DbName `
            --no-owner --no-acl --clean --if-exists `
            -f $BackupFile
        
        # Compress
        Compress-Archive -Path $BackupFile -DestinationPath "$BackupFile.zip" -Force
        Remove-Item $BackupFile
        
        Remove-Item Env:\PGPASSWORD
        
        Write-Log "Database backup completed: $BackupFile.zip"
    }
}

function Backup-Media {
    Write-Log "Starting media backup..."
    
    $MediaDir = "$BackendPath\media"
    if (Test-Path $MediaDir) {
        $BackupFile = "$MediaBackupDir\media_$Timestamp.zip"
        Compress-Archive -Path "$MediaDir\*" -DestinationPath $BackupFile -Force
        
        $Size = (Get-Item $BackupFile).Length / 1MB
        Write-Log "Media backup completed: $BackupFile ($([math]::Round($Size, 2)) MB)"
    } else {
        Write-Log "No media directory found to backup"
    }
}

function Cleanup-OldBackups {
    Write-Log "Cleaning up backups older than $RetentionDays days..."
    
    $CutoffDate = (Get-Date).AddDays(-$RetentionDays)
    
    # Clean database backups
    Get-ChildItem -Path "$BackupRoot\database" -Recurse -File | 
        Where-Object { $_.LastWriteTime -lt $CutoffDate } |
        Remove-Item -Force
    
    # Clean media backups
    Get-ChildItem -Path "$BackupRoot\media" -Recurse -File | 
        Where-Object { $_.LastWriteTime -lt $CutoffDate } |
        Remove-Item -Force
    
    # Remove empty directories
    Get-ChildItem -Path "$BackupRoot" -Recurse -Directory | 
        Where-Object { (Get-ChildItem $_.FullName).Count -eq 0 } |
        Remove-Item -Force
    
    Write-Log "Cleanup completed"
}

# Main execution
Write-Log "=========================================="
Write-Log "Hotel PMS Backup Started"
Write-Log "=========================================="

try {
    Backup-Database
    Backup-Media
    Cleanup-OldBackups
    
    Write-Log "=========================================="
    Write-Log "Backup completed successfully!"
    Write-Log "Location: $BackupRoot\$DateDir"
    Write-Log "=========================================="
    
    exit 0
}
catch {
    Write-Log "ERROR: $_"
    exit 1
}
