# Unraid HDD Wakeup Stats Plugin

![Unraid Version](https://img.shields.io/badge/Unraid-6.12%2B%20%7C%207.x-blue) ![License](https://img.shields.io/badge/license-MIT-green)

[🇬🇧 English](#english) | [🇩🇪 Deutsch](#deutsch)

---

<a name="english"></a>
## 🇬🇧 English

### Overview
**HDD Wakeup Stats** is a lightweight, fully integrated Unraid plugin that tracks and displays hard drive spin-up (wakeup) events. It helps you monitor your server's power efficiency by showing you exactly how often your disks spin up, and attempts to identify the trigger/process responsible for waking them.

The plugin provides a native, responsive dashboard widget designed specifically for Unraid 6.12+ and Unraid 7.x, seamlessly blending into the WebGUI.

### Features
* **Native Dashboard Integration:** Beautiful, compact widget that fits perfectly into the Unraid 6.12/7.x responsive tile layout.
* **Accurate Tracking:** Uses efficient kernel polling to detect state changes from `standby` to `active/idle`.
* **Trigger Detection:** Attempts to log the reason or process that triggered the wakeup event.
* **Drag & Drop Sorting:** Easily sort the order of monitored disks via the plugin settings page.
* **Historical Data:** Keeps track of wakeups for "Today" and over a customizable "X Days" timeframe.
* **Low Resource Footprint:** Runs completely in the background via a lightweight PHP daemon.

### Installation
You can install the plugin via the Unraid command line. Paste the following command into the Unraid terminal:
```bash
plugin install https://raw.githubusercontent.com/Blacksoul87/unraid-hddwakeupstats-plugin/main/hddwakeupstats.plg
```
*(Note: Replace the URL above with the actual raw URL of the `.plg` file once uploaded to GitHub).*

Alternatively, place the `hddwakeupstats.plg` file into `/boot/config/plugins/` and run:
```bash
plugin install /boot/config/plugins/hddwakeupstats.plg
```

### Usage
1. After installation, navigate to **Settings > HDD Wakeup Stats**.
2. Select the hard drives you wish to monitor by checking the boxes.
3. Sort the drives via Drag & Drop if desired.
4. Click **Save Settings**.
5. Go to your Unraid **Dashboard**. The "HDD Wakeups" tile will appear and can be dragged to your preferred layout column.

---

<a name="deutsch"></a>
## 🇩🇪 Deutsch

### Übersicht
**HDD Wakeup Stats** ist ein schlankes, vollständig integriertes Unraid-Plugin, das das Aufwachen (Spin-up) von Festplatten überwacht und anzeigt. Es hilft dir, die Energieeffizienz deines Servers im Blick zu behalten, indem es dir genau zeigt, wie oft deine Festplatten anlaufen, und versucht, den Prozess oder Auslöser für das Aufwachen zu identifizieren.

Das Plugin bietet eine native, responsive Dashboard-Kachel, die speziell für Unraid 6.12+ und Unraid 7.x entwickelt wurde und sich nahtlos in die WebGUI einfügt.

### Funktionen
* **Native Dashboard-Integration:** Eine kompakte, moderne Kachel, die perfekt in das responsive Grid-Layout von Unraid 6.12/7.x passt.
* **Präzises Tracking:** Nutzt effizientes Kernel-Polling, um Statusänderungen von `standby` zu `active/idle` zu erkennen.
* **Auslöser-Erkennung:** Versucht, den Prozess oder Grund zu protokollieren, der das Aufwachen der Festplatte verursacht hat.
* **Drag & Drop Sortierung:** Lege die Reihenfolge der angezeigten Festplatten bequem in den Plugin-Einstellungen fest.
* **Historische Daten:** Zählt die Spin-ups für "Heute" und über einen anpassbaren "X Tage"-Zeitraum.
* **Geringer Ressourcenverbrauch:** Läuft vollständig im Hintergrund über einen leichtgewichtigen PHP-Daemon.

### Installation
Du kannst das Plugin bequem über die Unraid-Kommandozeile installieren. Kopiere den folgenden Befehl in das Unraid-Terminal:
```bash
plugin install https://raw.githubusercontent.com/Blacksoul87/unraid-hddwakeupstats-plugin/main/hddwakeupstats.plg
```
*(Hinweis: Ersetze die obige URL durch die tatsächliche Raw-URL der `.plg`-Datei, sobald das Projekt auf GitHub hochgeladen wurde).*

Alternativ kannst du die Datei `hddwakeupstats.plg` in den Ordner `/boot/config/plugins/` legen und folgenden Befehl ausführen:
```bash
plugin install /boot/config/plugins/hddwakeupstats.plg
```

### Nutzung
1. Navigiere nach der Installation zu **Settings > HDD Wakeup Stats** (Einstellungen).
2. Wähle die Festplatten aus, die überwacht werden sollen, indem du die entsprechenden Häkchen setzt.
3. Sortiere die Laufwerke bei Bedarf per Drag & Drop in die gewünschte Reihenfolge.
4. Klicke auf **Einstellungen Speichern**.
5. Wechsle auf dein Unraid **Dashboard**. Die Kachel "HDD Wakeups" erscheint dort und kann an die gewünschte Stelle gezogen werden.

---

### Uninstallation / Deinstallation
```bash
plugin remove hddwakeupstats
```

### License
MIT License
