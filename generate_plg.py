import base64
import os

page_settings_content = """Menu="Utilities"
Title="HDD Wakeup Stats"
---
<?php
$config_file = '/boot/config/plugins/hddwakeupstats/settings.cfg';

$disks_ini = @parse_ini_file('/var/local/emhttp/disks.ini', true);
$dev_to_name = [];
if ($disks_ini) {
    foreach($disks_ini as $info) {
        if(isset($info['device']) && isset($info['name'])) {
            $dev_to_name[$info['device']] = $info['name'];
        }
    }
}

$disks = [];
$out = shell_exec("lsblk -d -n -o NAME,MODEL | grep -E '^(sd|nvme)'");
if ($out) {
    $lines = array_filter(explode("\\n", trim($out)));
    foreach ($lines as $line) {
        $parts = preg_split('/\\s+/', $line, 2);
        $name = $parts[0];
        $model = isset($parts[1]) ? trim($parts[1]) : 'Unbekannt';
        $disks[$name] = $model;
    }
}

if (isset($_POST['save'])) {
    $selected = isset($_POST['disks']) ? $_POST['disks'] : [];
    $days = isset($_POST['history_days']) ? intval($_POST['history_days']) : 7;
    
    $content = "DISKS=\\"" . implode(',', $selected) . "\\"\\n";
    $content .= "HISTORY_DAYS=\\"$days\\"\\n";
    
    @mkdir(dirname($config_file), 0777, true);
    file_put_contents($config_file, $content);
    $message = "Einstellungen erfolgreich gespeichert.";
    
    // Prune history based on new settings immediately
    shell_exec("/usr/local/emhttp/plugins/hddwakeupstats/sync.php > /dev/null 2>&1 &");
}

if (isset($_POST['reset'])) {
    file_put_contents('/tmp/hddwakeupstats.json', '{}');
    file_put_contents('/boot/config/plugins/hddwakeupstats/wakeups.json', '{}');
    $message = "Historie erfolgreich zurückgesetzt.";
}

$cfg = @parse_ini_file($config_file);
$tracked_disks = isset($cfg['DISKS']) ? explode(',', $cfg['DISKS']) : [];
$history_days = isset($cfg['HISTORY_DAYS']) ? intval($cfg['HISTORY_DAYS']) : 7;
?>

<style>
.dwt-container { padding: 20px; background-color: #f9f9f9; border-radius: 8px; border: 1px solid #e0e0e0; margin-bottom: 20px; color: #333; }
.dwt-btn { padding: 8px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
.dwt-btn:hover { background-color: #0056b3; }
.dwt-msg { padding: 10px; background-color: #d4edda; color: #155724; border-radius: 4px; margin-bottom: 15px; }

@media (prefers-color-scheme: dark) {
    .dwt-container { background-color: #2c2c2c; border-color: #444; color: #eee; }
}
</style>

<div class="dwt-container">
    <h2 style="margin-top:0;">HDD Wakeup Stats Einstellungen</h2>
    <p style="font-size: 13px; color: #666;">Wähle die Festplatten aus, die überwacht werden sollen. Die Anzeige erfolgt im Unraid Dashboard.</p>
    
    <?php if (isset($message)) echo "<div class='dwt-msg'>$message</div>"; ?>
    
    <form method="POST">
        <div style="margin-bottom: 20px;">
            <label style="font-weight: bold; display: block; margin-bottom: 5px;">Historien-Dauer (Tage):</label>
            <input type="number" name="history_days" value="<?php echo $history_days; ?>" min="1" style="width: 80px; padding: 5px; border-radius: 4px; border: 1px solid #ccc;">
            <div style="font-size: 12px; color: #888; margin-top: 5px;">Alte Einträge werden automatisch nach Ablauf dieser Zeit gelöscht.</div>
        </div>
        
        <div style="margin-bottom: 20px;">
            <label style="font-weight: bold; display: block; margin-bottom: 5px;">Zu überwachende Festplatten (Drag & Drop zum Sortieren):</label>
            <?php
            $ordered_disks = [];
            foreach ($tracked_disks as $td) {
                if (isset($disks[$td])) $ordered_disks[$td] = $disks[$td];
            }
            foreach ($disks as $d => $model) {
                if (!isset($ordered_disks[$d])) $ordered_disks[$d] = $model;
            }
            ?>
            <div id="disk-sortable-list" style="background: #fff; border: 1px solid #ccc; padding: 10px; border-radius: 4px; max-height: 400px; overflow-y: auto; color: #333;">
            <?php if (empty($ordered_disks)): ?>
                <i>Keine Festplatten gefunden.</i>
            <?php else: ?>
                <?php foreach ($ordered_disks as $d => $model): 
                    $friendly = isset($dev_to_name[$d]) ? ucfirst($dev_to_name[$d]) : $d;
                ?>
                    <div class="sortable-disk-item" style="padding: 8px; border: 1px solid #ddd; margin-bottom: 5px; border-radius: 4px; background: #fdfdfd; display: flex; align-items: center; cursor: grab;">
                        <i class="fa fa-bars" style="color: #aaa; margin-right: 15px;"></i>
                        <input type="checkbox" name="disks[]" id="disk_<?php echo htmlspecialchars($d); ?>" value="<?php echo htmlspecialchars($d); ?>" <?php if(in_array($d, $tracked_disks)) echo "checked"; ?> style="transform: scale(1.2); margin-right: 15px;">
                        <label for="disk_<?php echo htmlspecialchars($d); ?>" style="cursor: pointer; margin: 0; width: 100%;">
                            <b style="color: #000;"><?php echo htmlspecialchars($friendly); ?></b> 
                            <span style="color: #666; font-size: 12px; margin-left: 5px;">(/dev/<?php echo htmlspecialchars($d); ?> - <?php echo htmlspecialchars($model); ?>)</span>
                        </label>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
            </div>
            
<script>
$(function() {
    if (typeof $.fn.sortable !== 'undefined') {
        $("#disk-sortable-list").sortable({
            items: ".sortable-disk-item",
            cursor: "grabbing",
            axis: "y",
            containment: "parent"
        });
    }
});
</script>
        </div>
        
        <div style="margin-top: 10px;">
            <input type="submit" name="save" value="Einstellungen Speichern" class="dwt-btn">
            <input type="submit" name="reset" value="Historie Zurücksetzen" class="dwt-btn" style="background-color: #dc3545; margin-left: 15px;" onclick="return confirm('Möchtest du die gesamte Historie wirklich löschen? Alle bisherigen Zähler werden auf 0 gesetzt.');">
        </div>
    </form>
</div>
"""

page_dashboard_content = """Menu="Buttons:199"
Link="nav-user"
---
<?php
$pluginname = "HDD Wakeups";
if (isset($mytiles)) {
$mytiles[$pluginname]['column1'] = <<<EOT
<style>
.wakeup-badge { background: #007bff; color: white; padding: 1px 5px; border-radius: 8px; font-weight: bold; font-size: 10px; }
.wakeup-trigger { font-size: 10px; color: #aaa; display: block; max-width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.wu-row { display: flex; align-items: center; padding: 4px 0; border-bottom: 1px solid #e0e0e0; font-size: 11px; }
@media (prefers-color-scheme: dark) { .wu-row { border-bottom: 1px solid #444; } }
.wu-col-disk { width: 30%; padding-right: 5px; }
.wu-col-time { width: 40%; padding-right: 5px; overflow: hidden; }
.wu-col-today { width: 15%; text-align: center; }
.wu-col-total { width: 15%; text-align: center; }
</style>

<tbody id="hddwakeupstats" title="HDD Wakeups">
    <tr>
      <td style="padding: 0;">
        <div id="hddwakeupstats-container" style="width: 100%; box-sizing: border-box;">
          <div class="wu-row" style="border-bottom: 1px solid #888; padding-bottom: 4px; font-weight: bold;">
            <div class="wu-col-disk">Laufwerk</div>
            <div class="wu-col-time">Zuletzt</div>
            <div class="wu-col-today">Heute</div>
            <div class="wu-col-total" id="wu-header-total">7 T.</div>
          </div>
          <div id="hddwakeupstats-content">
            <div style="text-align: center; padding: 10px; color: #888; font-size: 11px;">Lade Daten...</div>
          </div>
        </div>
      </td>
    </tr>
</tbody>

<script>
function updateWakeupData() {
    fetch('/plugins/hddwakeupstats/get_data.php')
    .then(r => r.json())
    .then(data => {
        let html = '';
        const histDays = data.settings.history_days;
        document.getElementById('wu-header-total').innerText = histDays + ' T.';
        
        if (Object.keys(data.stats).length === 0) {
            html = '<div style="text-align:center; padding:15px; color:#888;">Keine überwachten Laufwerke konfiguriert.</div>';
        } else {
            for (const disk in data.stats) {
                const s = data.stats[disk];
                html += '<div class="wu-row">';
                html += '<div class="wu-col-disk">' + (s.friendly_name || disk) + '</div>';
                html += '<div class="wu-col-time">';
                if (s.last_time) {
                    html += '<div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">' + s.last_time + '</div>';
                    if (s.last_trigger) {
                        html += '<div class="wakeup-trigger" title="' + s.last_trigger + '">durch ' + s.last_trigger + '</div>';
                    }
                } else {
                    html += '<div style="color: #666;">-</div>';
                }
                html += '</div>';
                html += '<div class="wu-col-today"><span class="wakeup-badge">' + s.count_today + '</span></div>';
                html += '<div class="wu-col-total"><span class="wakeup-badge" style="background:#28a745;">' + s.count_total + '</span></div>';
                html += '</div>';
            }
        }
        document.getElementById('hddwakeupstats-content').innerHTML = html;
    })
    .catch(e => console.error(e));
}

updateWakeupData();
setInterval(updateWakeupData, 30000);
</script>
EOT;
}
?>
"""

php_api_content = """<?php
header('Content-Type: application/json');
$config_file = '/boot/config/plugins/hddwakeupstats/settings.cfg';
$json_file = '/tmp/hddwakeupstats.json';

$cfg = @parse_ini_file($config_file);
$history_days = isset($cfg['HISTORY_DAYS']) ? intval($cfg['HISTORY_DAYS']) : 7;
$tracked_disks = isset($cfg['DISKS']) ? explode(',', $cfg['DISKS']) : [];

$disks_ini = @parse_ini_file('/var/local/emhttp/disks.ini', true);
$dev_to_name = [];
if ($disks_ini) {
    foreach($disks_ini as $info) {
        if(isset($info['device']) && isset($info['name'])) {
            $dev_to_name[$info['device']] = ucfirst($info['name']);
        }
    }
}

$data = [];
if (file_exists($json_file)) {
    $data = json_decode(file_get_contents($json_file), true);
}

$today_start = strtotime("today 00:00:00");

$response = [
    'settings' => ['history_days' => $history_days],
    'stats' => []
];

foreach ($tracked_disks as $disk) {
    if (empty($disk)) continue;
    $events = isset($data[$disk]) ? $data[$disk] : [];
    
    $count_today = 0;
    $count_total = count($events);
    $last_time = null;
    $last_trigger = null;
    
    foreach ($events as $e) {
        $t = is_array($e) ? $e['time'] : $e;
        if ($t >= $today_start) $count_today++;
    }
    
    if ($count_total > 0) {
        $last_event = end($events);
        $last_time = is_array($last_event) ? $last_event['time'] : $last_event;
        $last_time = date("d.m. H:i", $last_time);
        $last_trigger = is_array($last_event) && isset($last_event['trigger']) ? $last_event['trigger'] : null;
    }
    
    $response['stats'][$disk] = [
        'friendly_name' => isset($dev_to_name[$disk]) ? $dev_to_name[$disk] : $disk,
        'count_today' => $count_today,
        'count_total' => $count_total,
        'last_time' => $last_time,
        'last_trigger' => $last_trigger
    ];
}

echo json_encode($response);
?>
"""

php_daemon_content = """#!/usr/bin/php
<?php
$config_file = '/boot/config/plugins/hddwakeupstats/settings.cfg';
$json_file = '/tmp/hddwakeupstats.json';

// Ensure file exists
if (!file_exists($json_file)) {
    // try to load from boot if exists
    $persist_file = '/boot/config/plugins/hddwakeupstats/wakeups.json';
    if (file_exists($persist_file)) {
        copy($persist_file, $json_file);
    } else {
        file_put_contents($json_file, '{}');
    }
}

$f = popen("tail -F /var/log/syslog", "r");
if (!$f) {
    die("Cannot open syslog\\n");
}

while ($line = fgets($f)) {
    $disk = "";
    if (preg_match('/read SMART \\/dev\\/([a-z0-9]+)/', $line, $m)) {
        $disk = $m[1];
    } elseif (preg_match('/spinning up \\/dev\\/([a-z0-9]+)/', $line, $m)) {
        $disk = $m[1];
    }
    
    if ($disk) {
        $cfg = @parse_ini_file($config_file);
        $tracked_disks = isset($cfg['DISKS']) ? explode(',', $cfg['DISKS']) : [];
        if (in_array($disk, $tracked_disks)) {
            $data = [];
            if (file_exists($json_file)) {
                $data = json_decode(file_get_contents($json_file), true);
            }
            if (!isset($data[$disk])) $data[$disk] = [];
            
            $now = time();
            $last_event = end($data[$disk]);
            $last_time = is_array($last_event) ? $last_event['time'] : $last_event;
            
            // Prevent duplicates within 60 seconds (spin up can take up to 10s, causing delayed SMART reads)
            if (!$last_time || ($now - $last_time) > 60) {
                // Try to find what triggered the spinup
                $process = "";
                $mount = "";
                
                // Get mount point from Unraid config
                $disks_ini = @parse_ini_file('/var/local/emhttp/disks.ini', true);
                if ($disks_ini) {
                    foreach($disks_ini as $info) {
                        if(isset($info['device']) && $info['device'] == $disk) {
                            if (isset($info['fsStatus']) && strpos($info['fsStatus'], 'Mounted') !== false) {
                                $mount = "/mnt/" . $info['name'];
                            }
                            break;
                        }
                    }
                }
                
                // Fallback to lsblk
                if (empty($mount)) {
                    $mounts = shell_exec("lsblk -n -o MOUNTPOINT /dev/$disk | grep -v '^$'");
                    if ($mounts) {
                        $mount = trim(explode("\\n", trim($mounts))[0]);
                    }
                }
                
                if (!empty($mount) && is_dir($mount)) {
                    $fuser_out = shell_exec("fuser -m $mount 2>/dev/null");
                    if ($fuser_out) {
                        $pids = preg_split('/\\s+/', trim($fuser_out));
                        $names = [];
                        foreach($pids as $p) {
                            if(is_numeric($p)) {
                                $name = trim(shell_exec("ps -p $p -o comm="));
                                if ($name) $names[] = $name;
                            }
                        }
                        if (!empty($names)) {
                            $process = implode(", ", array_unique($names));
                        }
                    }
                    if (empty($process)) {
                        // try lsof as fallback
                        $lsof_out = shell_exec("lsof +D $mount 2>/dev/null | grep -v COMMAND | head -n 1");
                        if (!empty($lsof_out)) {
                            $parts = preg_split('/\\s+/', trim($lsof_out));
                            if (isset($parts[0])) $process = $parts[0];
                        }
                    }
                }
                
                if (empty($process)) {
                    $lsof_out = shell_exec("lsof /dev/$disk 2>/dev/null | grep -v COMMAND | head -n 1");
                    if (!empty($lsof_out)) {
                        $parts = preg_split('/\\s+/', trim($lsof_out));
                        if (isset($parts[0])) $process = $parts[0];
                    }
                }
                if (empty($process)) $process = "Unbekannt";
                
                $data[$disk][] = ['time' => $now, 'trigger' => substr($process, 0, 50)];
                file_put_contents($json_file, json_encode($data));
                
                // Immediately call sync script to persist to USB and prune
                shell_exec("/usr/local/emhttp/plugins/hddwakeupstats/sync.php > /dev/null 2>&1 &");
            }
        }
    }
}
?>
"""

php_sync_content = """#!/usr/bin/php
<?php
$config_file = '/boot/config/plugins/hddwakeupstats/settings.cfg';
$json_file = '/tmp/hddwakeupstats.json';
$persist_file = '/boot/config/plugins/hddwakeupstats/wakeups.json';

$cfg = @parse_ini_file($config_file);
$history_days = isset($cfg['HISTORY_DAYS']) ? intval($cfg['HISTORY_DAYS']) : 7;
$cutoff = time() - ($history_days * 86400);

$data = [];
if (file_exists($json_file)) {
    $data = json_decode(file_get_contents($json_file), true);
} elseif (file_exists($persist_file)) {
    $data = json_decode(file_get_contents($persist_file), true);
}

if (is_array($data)) {
    $modified = false;
    foreach ($data as $disk => $events) {
        if (!is_array($events)) continue;
        $new_events = [];
        foreach ($events as $e) {
            $t = is_array($e) ? $e['time'] : $e;
            if ($t >= $cutoff) {
                // Ensure format conversion from old plain integer to object
                if (!is_array($e)) {
                    $new_events[] = ['time' => $t, 'trigger' => 'Unbekannt'];
                    $modified = true;
                } else {
                    $new_events[] = $e;
                }
            } else {
                $modified = true;
            }
        }
        $data[$disk] = $new_events;
    }
    
    $json = json_encode($data);
    file_put_contents($json_file, $json);
    
    // Create dir if needed
    @mkdir(dirname($persist_file), 0777, true);
    file_put_contents($persist_file, $json);
}
?>
"""

def get_b64(content):
    return base64.encodebytes(content.encode('utf-8')).decode('utf-8')

plg_content = f"""<?xml version="1.0" standalone="yes"?>
<PLUGIN name="hddwakeupstats" author="Antigravity" version="2026.06.12" pluginURL="" icon="hdd-o">

<FILE Name="/boot/config/plugins/hddwakeupstats/settings.cfg">
<INLINE>
DISKS=""
HISTORY_DAYS="7"
</INLINE>
</FILE>

<FILE Run="/bin/bash">
<INLINE>
mkdir -p /usr/local/emhttp/plugins/hddwakeupstats

# Cleanup old dashboard file from previous attempt
rm -f /usr/local/emhttp/plugins/hddwakeupstats/hddwakeupstats_dashboard.page

base64 -d &lt;&lt;EOF &gt; /usr/local/emhttp/plugins/hddwakeupstats/hddwakeupstats_settings.page
{get_b64(page_settings_content)}EOF

base64 -d &lt;&lt;EOF &gt; /usr/local/emhttp/plugins/hddwakeupstats/hddwakeupstats.page
{get_b64(page_dashboard_content)}EOF

base64 -d &lt;&lt;EOF &gt; /usr/local/emhttp/plugins/hddwakeupstats/get_data.php
{get_b64(php_api_content)}EOF

base64 -d &lt;&lt;EOF &gt; /usr/local/emhttp/plugins/hddwakeupstats/tracker.php
{get_b64(php_daemon_content)}EOF

base64 -d &lt;&lt;EOF &gt; /usr/local/emhttp/plugins/hddwakeupstats/sync.php
{get_b64(php_sync_content)}EOF

chmod +x /usr/local/emhttp/plugins/hddwakeupstats/tracker.php
chmod +x /usr/local/emhttp/plugins/hddwakeupstats/sync.php

# Start Daemon
nohup /usr/local/emhttp/plugins/hddwakeupstats/tracker.php &gt; /dev/null 2&gt;&amp;1 &amp;

# Setup cron for hourly sync just in case
CRON_JOB="0 * * * * /usr/local/emhttp/plugins/hddwakeupstats/sync.php &gt; /dev/null 2&gt;&amp;1"
crontab -l 2&gt;/dev/null | grep -v "/usr/local/emhttp/plugins/hddwakeupstats/sync.php" &gt; /tmp/cron_temp
echo "$CRON_JOB" &gt;&gt; /tmp/cron_temp
crontab /tmp/cron_temp
rm -f /tmp/cron_temp

echo ""
echo "----------------------------------------------------"
echo " HDD Wakeup Stats plugin installed successfully"
echo "----------------------------------------------------"
echo ""
</INLINE>
</FILE>

<FILE Run="/bin/bash" Method="remove">
<INLINE>
# Kill daemon
pkill -f /usr/local/emhttp/plugins/hddwakeupstats/tracker.php 2&gt;/dev/null
# Remove files
rm -rf /usr/local/emhttp/plugins/hddwakeupstats

# Remove cron
crontab -l 2&gt;/dev/null | grep -v "/usr/local/emhttp/plugins/hddwakeupstats/sync.php" &gt; /tmp/cron_temp
crontab /tmp/cron_temp
rm -f /tmp/cron_temp

echo ""
echo "----------------------------------------------------"
echo " HDD Wakeup Stats plugin uninstalled"
echo "----------------------------------------------------"
echo ""
</INLINE>
</FILE>

</PLUGIN>
"""

with open("hddwakeupstats.plg", "w") as f:
    f.write(plg_content)
