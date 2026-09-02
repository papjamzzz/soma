# Soma

A 3D body you can rotate, with biomarkers mapped onto the regions they actually affect.
Heart rate lights the chest. Kidney markers light the lower back. The point is to see a
panel of numbers as a body rather than as a table.

## Two sources, one view

**Watch** is what an Apple Watch can genuinely measure: heart rate, HRV, resting heart
rate, blood oxygen, respiratory rate, VO2 max, sleep, activity. About twelve signals.

**Lab** is a simulated blood panel, the forty-odd markers a real draw would return.

**Both** overlays them, which is the actual argument of the thing: wearables sample
constantly but shallowly, and a blood panel is deep but a single moment. Neither is the
whole picture, and looking at one body lit by both makes that obvious in a way two
spreadsheets do not.

## Running it

```bash
make run
```

Or double-click `launch.command`. Rotate with a drag; toggle Watch, Lab or Both.

Python, Flask, WebGL.
