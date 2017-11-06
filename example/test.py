import moddb_parser
reader = moddb_parser.Reader()
game = reader.parse_game("http://www.moddb.com/games/battle-for-middle-earth-ii-rise-of-the-witch-king")
mod = reader.parse_mod("http://www.moddb.com/mods/edain-mod")
print(game)
print(mod)