## U-Backup

<code><a href="https://github.com/umarurize/UTP"><img height="25" src="https://github.com/umarurize/U_Backup/blob/master/logo/logo.jpg" alt="U-Backup" /></a>&nbsp;U-Backup</code>

### :maple_leaf:Attention!
U-Backup only packages the `worlds` folder into a `.zip` file for backup.

### 🔔Introductions
* **Two backup modes**
- [x] Manual backup
- [x] Schedule backup
* **Highly customizable**
* **Detection of free disk space**
* **Multithreading processing**
* **Beautiful GUI forms**
* **Hot reload support**
* **Localized languages support**

### :hammer:Installation
[Optional pre-plugin] ZX_UI

Put `.whl` file into the endstone plugins folder, and then start the server. Enter the command `/ub` to call out the main form.

### :computer:Download
Now, you can get the release version from this repo or <code><a href="https://www.minebbs.com/resources/ubackup.9854/"><img height="20" src="https://github.com/umarurize/umaru-cdn/blob/main/images/minebbs.png" alt="Minebbs" /></a>&nbsp;Minebbs</code>.

### 📁File structure
```
Plugins/
├─ ubackup/
│  ├─ config.json
│  ├─ backups/
│  │  ├─ 2025-06-01-18-00-00.zip (for example)
│  │  ├─ ...
│  ├─ langs/
│  │  ├─ zh_CN.json
│  │  ├─ en_US.json
│  │  ├─ ...
```

### 📝Configuration
U-Backup allows server owner to edit and save `config.json` and reload it in game directly through GUI forms.

`config.json`
```json5
{
    "schedule_backup_time": [ // the schedule backup time points (Server owner can add any number of time points)
        "00:00:00",
        "6:00:00",
        "12:00:00",
        "20:30:00"
    ],
    "max_backups_num": 3 // the max number of backups can be retained by the server
}
```

### 🌐Languages
- [x] `zh_CN`
- [x] `en_US`

Off course you can add your mother language to U-Backup, just creat `XX_XX.json` (such as `ja_JP.json`) and translate value with reference to `en_US.json`.

You can also creat a PR to this repo to make your mother language one of the official languages of U-Backup.

### 📷Screenshots
You can view related screenshots of U-Backup from images folder of this repo.

![](https://img.shields.io/badge/language-python-blue.svg) [![GitHub License](https://img.shields.io/github/license/umarurize/U_Backup)](LICENSE)



