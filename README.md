# moddb-reader

A simple python scrapper to get some information from ModDB mod pages. Just supply an url to `parse_mod` or `parse_game` and watch the magic unfold.

Example:

```py
from moddb_reader import parse_mod, parse_game
mod = parse_mod("http://www.moddb.com/mods/edain-mod")
mod.name
# Edain Mod
mod.game
# Battle for Middle Earth 2: Rise of the Witch King

game = parse_game("http://www.moddb.com/games/battle-for-middle-earth-ii-rise-of-the-witch-king")
game.name
# Battle for Middle-earth II: Rise of the Witch King
game.engine
#SAGE (Strategy Action Game Engine)
```

For more information on game and mod attributes check out the source code.
