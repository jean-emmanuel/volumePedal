volumePedal
===========

Midi volume pedal with midi learn function.

Released under GNU/GPL License v3 (http://www.gnu.org/)

Usage : python volumePedal.py [OPTIONS]

Options :
- -d, --device		midi input device number
- -c, --control		midi control number
- -s, --stereo		stereo mode (2 channels controled by one pedal)
- -h, --help		show this help


**Requires**

- jack
- python-pyo (& dependencies)
- wxgtk2-8

I strongly recommand using gladish as a session manager for jack.
