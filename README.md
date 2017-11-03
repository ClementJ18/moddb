# moddb-reader

A simple python scrapper to get some information from ModDB mod pages. Just supply an url to `parse_mod` and watch the magic unfold.

Example:

```py
from moddb-reader import parse_mod
mod = parse_mod("http://www.moddb.com/mods/edain-mod")
mod.name
# Edain Mod
mod.game_name
# Battle for Middl Earth 2: Rise of the Witch King
```