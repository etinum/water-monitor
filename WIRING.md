# Wiring Guide - Water Level Monitor

## GPIO Pin Reference

Using **BCM (Broadcom) numbering** - GPIO 17

### Physical Pin Layout (40-pin header)
```
Raspberry Pi GPIO Header (Top View)

     3.3V [ 1] [ 2] 5V
    GPIO2 [ 3] [ 4] 5V
    GPIO3 [ 5] [ 6] GND
    GPIO4 [ 7] [ 8] GPIO14
      GND [ 9] [10] GPIO15
   GPIO17 [11] [12] GPIO18  ← GPIO 17 (Physical Pin 11)
   GPIO27 [13] [14] GND     ← GND (Physical Pin 14)
   GPIO22 [15] [16] GPIO23
     3.3V [17] [18] GPIO24
   GPIO10 [19] [20] GND
    GPIO9 [21] [22] GPIO25
   GPIO11 [23] [24] GPIO8
      GND [25] [26] GPIO7
    GPIO0 [27] [28] GPIO1
    GPIO5 [29] [30] GND
    GPIO6 [31] [32] GPIO12
   GPIO13 [33] [34] GND
   GPIO19 [35] [36] GPIO16
   GPIO26 [37] [38] GPIO20
      GND [39] [40] GPIO21
```

## Float Switch Wiring

### Simple 2-Wire Float Switch (Normally Open)

```
Float Switch                    Raspberry Pi
┌──────────┐
│          │
│  Float   │
│  Switch  │
│          │
│  Pin 1   ├─────────────────→ GPIO 17 (Physical Pin 11)
│          │
│  Pin 2   ├─────────────────→ GND (Physical Pin 9 or 14)
│          │
└──────────┘
```

### How It Works

**Water Level OK (Float UP):**
```
Float UP → Switch OPEN → GPIO 17 pulled HIGH by internal resistor → Reads 1
```

**Water Level LOW (Float DOWN):**
```
Float DOWN → Switch CLOSED → GPIO 17 connected to GND → Reads 0
```

## Connection Steps

1. **Power off your Raspberry Pi** before connecting wires

2. **Identify GPIO 17:**
   - Physical Pin 11 (left side, 6th pin from top)
   - Or use BCM numbering: GPIO 17

3. **Connect Float Switch Pin 1:**
   - Connect to GPIO 17 (Physical Pin 11)
   - Use a female-to-male jumper wire

4. **Connect Float Switch Pin 2:**
   - Connect to any GND pin (Physical Pin 9, 14, 20, 25, 30, 34, or 39)
   - Recommended: Physical Pin 9 (closest to GPIO 17)

5. **Verify connections:**
   - Float Switch Pin 1 → GPIO 17
   - Float Switch Pin 2 → GND
   - No other connections needed (internal pull-up resistor used)

6. **Power on Raspberry Pi**

## Testing the Wiring

Run the test script to verify your wiring:

```bash
python3 test_water_monitor.py
```

You should see:
- **Float UP (water OK):** Pin reads HIGH (1)
- **Float DOWN (water low):** Pin reads LOW (0)

Move the float up and down to test both states.

## Troubleshooting

### Always reads HIGH (1)
- ✓ Normal when float is up (water OK)
- ✗ If float is down but still reads HIGH:
  - Check GND connection
  - Verify float switch is normally open (NO) type
  - Test float switch with multimeter

### Always reads LOW (0)
- ✓ Normal when float is down (water low)
- ✗ If float is up but still reads LOW:
  - Check GPIO 17 connection
  - Verify float switch polarity
  - Try swapping float switch wires

### Intermittent readings
- Check for loose connections
- Verify jumper wires are secure
- Test with different jumper wires
- Check float switch mechanism

## Float Switch Types

### Normally Open (NO) - Recommended ✓
- Switch is OPEN when float is up (water OK)
- Switch CLOSES when float is down (water low)
- **This is what the code expects**

### Normally Closed (NC) - Not Compatible ✗
- Switch is CLOSED when float is up
- Switch OPENS when float is down
- **Will give inverted readings**
- If you have NC type, you'll need to modify the code

## Alternative GPIO Pins

If GPIO 17 is already in use, you can use a different pin:

1. Edit `config.py`:
   ```python
   FLOAT_PIN = 27  # Or any available GPIO pin
   ```

2. Update your wiring to match the new pin

3. Recommended alternative pins:
   - GPIO 27 (Physical Pin 13)
   - GPIO 22 (Physical Pin 15)
   - GPIO 23 (Physical Pin 16)
   - GPIO 24 (Physical Pin 18)

## Safety Notes

- Always power off Pi before connecting/disconnecting wires
- Don't connect 5V to GPIO pins (they are 3.3V tolerant only)
- Float switch should be rated for low voltage (3.3V is safe)
- Keep connections away from water
- Use waterproof enclosure for Pi if near water

## Visual Reference

```
Side View of Float Switch Operation:

Water Level OK:                Water Level LOW:
┌─────────────┐               ┌─────────────┐
│   Water     │               │             │
│             │               │             │
│    ╭─╮      │               │             │
│    │○│ UP   │               │    ╭─╮      │
│    ╰─╯      │               │    │○│ DOWN │
│             │               │    ╰─╯      │
└─────────────┘               └─────────────┘
Switch: OPEN                  Switch: CLOSED
GPIO: HIGH (1)                GPIO: LOW (0)
Status: OK ✓                  Status: LOW ⚠️
```

## Need Help?

1. Run `python3 test_water_monitor.py` to see live GPIO readings
2. Check connections match the diagram above
3. Verify float switch type (should be normally open)
4. Test float switch with multimeter if available
