import moddb_parser
reader = moddb_parser.Reader()

mod = reader.parse_mod("http://www.moddb.com/mods/edain-mod")
print(mod.share_links.twitter)
