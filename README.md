## 📦 Installation

1. Copy the following files in the /dist into the folder:

```
/RetroBat/plugins/StartupLaunchGame/
```

- `boot.exe`  
- `boot.ini`

2. Make sure your paths inside `boot.ini` are correctly set (see below).

---

## ⚙️ Configuration

Inside `boot.ini`, define:

```ini
bootrom = C:\RetroBat\roms\<system>\<game_name>.zip
bootcommand = ..\..\RetroBat.exe
```

- `bootrom`: path to the ROM file you want to auto-launch (relative or absolute).
- `bootcommand`: path to RetroBat or any launcher script (e.g., a `.bat` file).

Paths are resolved relative to the `StartupLaunchGame` folder.

---

## 🚀 Optional: Auto-Launch at Windows Startup

To launch the game automatically when Windows starts:

1. Right-click `boot.exe` → **Create shortcut**  
2. Move the shortcut to the Windows startup folder:

```
C:\Users\<your_username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

This will run `boot.exe` at each Windows login.

## 💡 Notes

- No fixed delay: the tool waits for the ES to become available.
- Supports both relative and absolute paths.
- Integrates seamlessly with RetroBat on Windows.

---

## 📄 License

This project is open-source and free to use. Feel free to contribute or suggest improvements!
```
