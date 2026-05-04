# old-electronics-fix-max-year-limit

A lightweight Python tool which I programmed to extend the usability of electronic devices with limited calendar ranges (e.g. maximum year 2020).

It determines a **past year** where the **day, month, and weekday** match the real calendar for as long as possible, allowing the device to remain practically usable despite displaying the wrong year.

## Features

- Python 3 (tested with 3.11)  
- Simple GUI (Tkinter) and command-line interface  
- No external dependencies  
- Efficient leap-year–based algorithm  

## Requirements

- Python 3.10 or newer  
- Tkinter (included with most Python installations)

On some Linux systems:
```bash
sudo apt install python3-tk
```

## Usage

### GUI
```bash
python main.py
```

### Command line
```bash
python calendar_matcher.py --date 2026-05-03 --earliest 2000 --latest 2020 --horizon 3653
```

## Notes

- The year range is inclusive  
- Leap years are handled correctly  
- Assumes the device advances the date automatically each day  

## Disclaimer

This software is provided without warranty. Please verify results on your device before relying on them.

(c) 2026 TecJVS
