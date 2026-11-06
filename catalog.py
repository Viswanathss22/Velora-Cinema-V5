"""Curated catalogue of actual released movies, television series and anime.

No streams or episodes are hosted. Image retrieval accepts only title-matched artwork.
"""
from urllib.parse import quote_plus
from movies import MOVIES as ORIGINAL_MOVIES

for film in ORIGINAL_MOVIES:
    film['kind'] = 'Movies'


def entry(kind, id, title, year, genre, extra, synopsis, creator, runtime, search=None):
    return dict(id=id,kind=kind,title=title,year=int(year),genre=genre,extra=extra,
        synopsis=synopsis,director=creator,runtime=runtime,poster='',backdrop='',
        tagline=('Explore this story in the collection.' if kind != 'Movies' else 'A story worth discovering.'),
        apple='https://www.themoviedb.org/search?query='+quote_plus(title),
        search=search or title)

EXTRA_MOVIES = [
    entry("Movies", 'shawshank', 'The Shawshank Redemption', 1994, 'Drama', 'Crime', 'Two prisoners forge a lasting friendship and search for hope within the walls of a penitentiary.', 'Frank Darabont', '2h 22m'),
    entry("Movies", 'godfather', 'The Godfather', 1972, 'Crime', 'Drama', 'The aging head of a New York crime family hands responsibility to his reluctant son.', 'Francis Ford Coppola', '2h 55m'),
    entry("Movies", 'pulpfiction', 'Pulp Fiction', 1994, 'Crime', 'Thriller', 'Intertwining stories of Los Angeles criminals collide in an unpredictable series of encounters.', 'Quentin Tarantino', '2h 34m'),
    entry("Movies", 'fightclub', 'Fight Club', 1999, 'Drama', 'Thriller', 'An unhappy office worker meets a charismatic soap salesman and discovers a dangerous secret world.', 'David Fincher', '2h 19m'),
    entry("Movies", 'matrix', 'The Matrix', 1999, 'Sci-Fi', 'Action', 'A computer hacker discovers the truth about reality and joins the resistance against machine control.', 'Lana Wachowski, Lilly Wachowski', '2h 16m'),
    entry("Movies", 'gladiator', 'Gladiator', 2000, 'Action', 'Drama', 'A betrayed Roman general seeks justice in the gladiatorial arena.', 'Ridley Scott', '2h 35m'),
    entry("Movies", 'titanic', 'Titanic', 1997, 'Romance', 'Drama', 'Two young passengers from different backgrounds fall in love aboard an ill-fated ocean liner.', 'James Cameron', '3h 14m'),
    entry("Movies", 'avatar', 'Avatar', 2009, 'Sci-Fi', 'Adventure', 'A former Marine becomes involved in the fate of Pandora and its indigenous Na’vi people.', 'James Cameron', '2h 42m'),
    entry("Movies", 'topgun', 'Top Gun: Maverick', 2022, 'Action', 'Drama', 'An ace Navy aviator trains a new generation of pilots for a high-risk mission.', 'Joseph Kosinski', '2h 10m'),
    entry("Movies", 'wick4', 'John Wick: Chapter 4', 2023, 'Action', 'Thriller', 'A legendary assassin seeks a path to freedom while facing powerful enemies across the globe.', 'Chad Stahelski', '2h 49m'),
    entry("Movies", 'endgame', 'Avengers: Endgame', 2019, 'Action', 'Sci-Fi', 'The Avengers reunite to attempt a final mission after a devastating cosmic defeat.', 'Anthony Russo, Joe Russo', '3h 1m'),
    entry("Movies", 'prestige', 'The Prestige', 2006, 'Drama', 'Mystery', 'Two rival magicians compete to create the ultimate illusion in Victorian London.', 'Christopher Nolan', '2h 10m'),
    entry("Movies", 'arrival', 'Arrival', 2016, 'Sci-Fi', 'Drama', 'A linguist attempts to communicate with mysterious visitors after spacecraft appear on Earth.', 'Denis Villeneuve', '1h 56m'),
    entry("Movies", 'her', 'Her', 2013, 'Romance', 'Sci-Fi', 'A lonely writer develops an unexpected connection with an advanced operating system.', 'Spike Jonze', '2h 6m'),
    entry("Movies", 'socialnetwork', 'The Social Network', 2010, 'Drama', 'History', 'A student creates a social networking site while personal conflicts grow around its success.', 'David Fincher', '2h'),
    entry("Movies", 'getout', 'Get Out', 2017, 'Horror', 'Thriller', 'A young man discovers something deeply unsettling while visiting his girlfriend’s family.', 'Jordan Peele', '1h 44m'),
    entry("Movies", 'coco', 'Coco', 2017, 'Animation', 'Adventure', 'An aspiring musician journeys into the Land of the Dead to uncover his family history.', 'Lee Unkrich, Adrian Molina', '1h 45m'),
    entry("Movies", 'insideout', 'Inside Out', 2015, 'Animation', 'Comedy', 'A young girl’s emotions navigate big changes following her family’s move to a new city.', 'Pete Docter', '1h 35m'),
    entry("Movies", 'nwh', 'Spider-Man: No Way Home', 2021, 'Action', 'Adventure', 'Peter Parker turns to Doctor Strange after the world learns his secret identity.', 'Jon Watts', '2h 28m'),
    entry("Movies", 'fordvferrari', 'Ford v Ferrari', 2019, 'Drama', 'Action', 'An automotive designer and racing driver challenge Ferrari at Le Mans.', 'James Mangold', '2h 32m'),
]

TV_SHOWS = [
    entry("TV Shows", 'breakingbad', 'Breaking Bad', 2008, 'Crime', 'Drama', 'A chemistry teacher turns to making methamphetamine after a life-changing diagnosis.', 'Vince Gilligan', "TV series"),
    entry("TV Shows", 'bettercallsaul', 'Better Call Saul', 2015, 'Crime', 'Drama', 'A struggling lawyer begins a transformation into the criminal attorney Saul Goodman.', 'Vince Gilligan, Peter Gould', "TV series"),
    entry("TV Shows", 'strangerthings', 'Stranger Things', 2016, 'Sci-Fi', 'Horror', 'A group of friends confronts supernatural threats in a small Indiana town.', 'The Duffer Brothers', "TV series"),
    entry("TV Shows", 'got', 'Game of Thrones', 2011, 'Fantasy', 'Drama', 'Noble families battle for control of the Iron Throne as an ancient threat draws near.', 'David Benioff, D. B. Weiss', "TV series"),
    entry("TV Shows", 'lastofus', 'The Last of Us', 2023, 'Drama', 'Sci-Fi', 'A hardened survivor escorts a teenager across a world ravaged by a pandemic.', 'Craig Mazin, Neil Druckmann', "TV series"),
    entry("TV Shows", 'houseofthedragon', 'House of the Dragon', 2022, 'Fantasy', 'Drama', 'The Targaryen dynasty grapples with power, succession and rival claims to the throne.', 'Ryan Condal, George R. R. Martin', "TV series"),
    entry("TV Shows", 'theboys', 'The Boys', 2019, 'Action', 'Drama', 'A vigilante group investigates corruption among famous, powerful superheroes.', 'Eric Kripke', "TV series"),
    entry("TV Shows", 'severance', 'Severance', 2022, 'Thriller', 'Sci-Fi', 'Office employees undergo a procedure dividing their work memories from personal life.', 'Dan Erickson', "TV series"),
    entry("TV Shows", 'dark', 'Dark', 2017, 'Sci-Fi', 'Thriller', 'Disappearing children expose unsettling secrets that span generations in a German town.', 'Baran bo Odar, Jantje Friese', "TV series"),
    entry("TV Shows", 'thebear', 'The Bear', 2022, 'Drama', 'Comedy', 'A talented chef returns home to run his family’s struggling Chicago sandwich shop.', 'Christopher Storer', "TV series"),
    entry("TV Shows", 'office', 'The Office', 2005, 'Comedy', 'Workplace', 'A documentary crew follows the everyday lives of employees at a paper company.', 'Greg Daniels', "TV series"),
    entry("TV Shows", 'sherlock', 'Sherlock', 2010, 'Mystery', 'Crime', 'Sherlock Holmes and John Watson solve complex crimes in modern London.', 'Mark Gatiss, Steven Moffat', "TV series"),
    entry("TV Shows", 'peakyblinders', 'Peaky Blinders', 2013, 'Crime', 'Drama', 'The Shelby family builds a criminal empire in postwar Birmingham.', 'Steven Knight', "TV series"),
    entry("TV Shows", 'crown', 'The Crown', 2016, 'Drama', 'History', 'A dramatic account of the reign of Queen Elizabeth II and the challenges of the monarchy.', 'Peter Morgan', "TV series"),
    entry("TV Shows", 'wednesday', 'Wednesday', 2022, 'Fantasy', 'Mystery', 'Wednesday Addams investigates mysterious events at Nevermore Academy.', 'Alfred Gough, Miles Millar', "TV series"),
    entry("TV Shows", 'moneyheist', 'Money Heist', 2017, 'Crime', 'Thriller', 'A criminal mastermind coordinates a daring heist with a carefully selected group.', 'Álex Pina', "TV series"),
    entry("TV Shows", 'chernobyl', 'Chernobyl', 2019, 'Drama', 'History', 'A dramatization of the 1986 nuclear disaster and the people responding to it.', 'Craig Mazin', "TV series"),
    entry("TV Shows", 'mandalorian', 'The Mandalorian', 2019, 'Sci-Fi', 'Adventure', 'A lone bounty hunter travels through the Star Wars galaxy with a mysterious child.', 'Jon Favreau', "TV series"),
    entry("TV Shows", 'fallout', 'Fallout', 2024, 'Sci-Fi', 'Adventure', 'A vault dweller enters a strange and dangerous post-apocalyptic wasteland.', 'Graham Wagner, Geneva Robertson-Dworet', "TV series"),
    entry("TV Shows", 'arcane', 'Arcane', 2021, 'Animation', 'Fantasy', 'Two sisters are caught in a conflict between the cities of Piltover and Zaun.', 'Christian Linke, Alex Yee', "TV series"),
]

ANIME = [
    entry("Anime", 'aot', 'Attack on Titan', 2013, 'Action', 'Fantasy', 'Humanity fights for survival behind giant walls against terrifying Titans.', 'Wit Studio / MAPPA', "Anime series", 'Attack on Titan'),
    entry("Anime", 'deathnote', 'Death Note', 2006, 'Thriller', 'Mystery', 'A student finds a supernatural notebook that can kill anyone whose name is written in it.', 'Madhouse', "Anime series", 'Death Note'),
    entry("Anime", 'demonslayer', 'Demon Slayer: Kimetsu no Yaiba', 2019, 'Action', 'Fantasy', 'Tanjiro becomes a demon slayer after a tragedy strikes his family.', 'ufotable', "Anime series", 'Kimetsu no Yaiba'),
    entry("Anime", 'jjk', 'Jujutsu Kaisen', 2020, 'Action', 'Fantasy', 'A high school student enters the world of jujutsu sorcerers and cursed spirits.', 'MAPPA', "Anime series", 'Jujutsu Kaisen'),
    entry("Anime", 'onepiece', 'One Piece', 1999, 'Adventure', 'Fantasy', 'Monkey D. Luffy and his crew sail the seas in pursuit of the legendary treasure.', 'Toei Animation', "Anime series", 'One Piece'),
    entry("Anime", 'naruto', 'Naruto', 2002, 'Action', 'Adventure', 'A young ninja strives to earn the recognition of his village and become Hokage.', 'Studio Pierrot', "Anime series", 'Naruto'),
    entry("Anime", 'shippuden', 'Naruto: Shippuden', 2007, 'Action', 'Adventure', 'Naruto returns from training to face new threats and help his friends.', 'Studio Pierrot', "Anime series", 'Naruto Shippuuden'),
    entry("Anime", 'fmab', 'Fullmetal Alchemist: Brotherhood', 2009, 'Action', 'Adventure', 'Two brothers seek the Philosopher’s Stone after a forbidden alchemical experiment.', 'Bones', "Anime series", 'Fullmetal Alchemist: Brotherhood'),
    entry("Anime", 'bebop', 'Cowboy Bebop', 1998, 'Sci-Fi', 'Action', 'A crew of bounty hunters travels through the solar system while confronting the past.', 'Sunrise', "Anime series", 'Cowboy Bebop'),
    entry("Anime", 'chainsaw', 'Chainsaw Man', 2022, 'Action', 'Horror', 'A young man gains chainsaw powers and joins an organisation hunting dangerous devils.', 'MAPPA', "Anime series", 'Chainsaw Man'),
    entry("Anime", 'vinland', 'Vinland Saga', 2019, 'Action', 'Drama', 'A young warrior seeks revenge amid the violence and politics of Viking history.', 'Wit Studio / MAPPA', "Anime series", 'Vinland Saga'),
    entry("Anime", 'spyfamily', 'Spy x Family', 2022, 'Comedy', 'Action', 'A spy, an assassin and a telepath form an unlikely undercover family.', 'Wit Studio / CloverWorks', "Anime series", 'Spy x Family'),
    entry("Anime", 'frieren', 'Frieren: Beyond Journey’s End', 2023, 'Fantasy', 'Adventure', 'An elf mage travels through the world long after her party’s historic victory.', 'Madhouse', "Anime series", 'Sousou no Frieren'),
    entry("Anime", 'hxh', 'Hunter x Hunter', 2011, 'Adventure', 'Action', 'A boy sets out to become a Hunter and find his absent father.', 'Madhouse', "Anime series", 'Hunter x Hunter (2011)'),
    entry("Anime", 'onepunch', 'One Punch Man', 2015, 'Action', 'Comedy', 'A hero who can defeat enemies with a single punch searches for meaning and challenge.', 'Madhouse / J.C.Staff', "Anime series", 'One Punch Man'),
    entry("Anime", 'mha', 'My Hero Academia', 2016, 'Action', 'Adventure', 'A powerless boy is chosen to inherit an extraordinary heroic ability.', 'Bones', "Anime series", 'Boku no Hero Academia'),
    entry("Anime", 'steinsgate', 'Steins;Gate', 2011, 'Sci-Fi', 'Thriller', 'A group of friends uncovers a way to send messages to the past.', 'White Fox', "Anime series", 'Steins;Gate'),
    entry("Anime", 'bleach', 'Bleach', 2004, 'Action', 'Fantasy', 'Ichigo Kurosaki gains the powers and responsibilities of a Soul Reaper.', 'Studio Pierrot', "Anime series", 'Bleach'),
    entry("Anime", 'codegeass', 'Code Geass: Lelouch of the Rebellion', 2006, 'Sci-Fi', 'Drama', 'A brilliant exiled prince gains a mysterious power and starts a rebellion.', 'Sunrise', "Anime series", 'Code Geass: Hangyaku no Lelouch'),
    entry("Anime", 'haikyu', 'Haikyu!!', 2014, 'Sports', 'Comedy', 'A determined student joins his school volleyball club and pursues his passion.', 'Production I.G', "Anime series", 'Haikyuu!!'),
]

CATALOG = ORIGINAL_MOVIES + EXTRA_MOVIES + TV_SHOWS + ANIME
BY_ID = {m["id"]:m for m in CATALOG}
KINDS = ("Movies", "TV Shows", "Anime")

assert len(CATALOG)==len(BY_ID), "Duplicate catalogue IDs"
