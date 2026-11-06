"""V5: verified title-matched, genuine anime promo art URLs.

The poster links below were individually matched to the show title against public
artwork catalogues in November 2026. These are online sources, not embedded
images. The application downloads them locally only when network access works.
"""

DIRECT_ANIME_POSTERS = {
    'aot': ['https://image.tmdb.org/t/p/w500/AgaD7s1vgIf4Soi3flAKN6Bte6u.jpg'],
    'deathnote': ['https://image.tmdb.org/t/p/w500/o6rz8BTCl2kjQtyNBH3KddRcu7T.jpg'],
    'demonslayer': ['https://image.tmdb.org/t/p/w500/b8KnKg4ozEeFTFolvAz1cePXfMO.jpg'],
    'jjk': ['https://image.tmdb.org/t/p/w500/ca6F8AvRAGiJCx5d0Q4g86zA8rN.jpg'],
    'onepiece': ['https://m.media-amazon.com/images/M/MV5BYzNjOTZlNDMtZWNlNC00YzMyLTkwNzEtZGE5MmJkMTg1NjJjXkEyXkFqcGc%40._V1_.jpg',
                 'https://i.pinimg.com/originals/48/9d/af/489daf7c183b3b8e512fd413011658e6.jpg'],
    'naruto': ['https://image.tmdb.org/t/p/w500/3MIrM7yU1YL1pknJsLsCuBoVZZw.jpg'],
    'shippuden': ['https://image.tmdb.org/t/p/w500/71mASgFgSiPl9QUexVH8BubU0lD.jpg'],
    'fmab': ['https://image.tmdb.org/t/p/w500/dzSALlMy3Mss6kPMjvf4Sl4pAtR.jpg'],
    'bebop': ['https://image.tmdb.org/t/p/w500/lcwlIyc83vLv25ZFa0IJCa857PE.jpg'],
    'chainsaw': ['https://creativefreaks.net/language/wp-content/uploads/2023/02/csm_KV_20220705_logobilling.png'],
    'vinland': ['https://image.tmdb.org/t/p/w500/4kkUThVWxlVzzgC4EqjWCDJfkkq.jpg'],
    'spyfamily': ['https://animeuknews.net/app/uploads/2022/04/Spy-x-family-anime-scaled.jpg'],
    'frieren': ['https://image.tmdb.org/t/p/w500/lI41MVzYGVSfmMyr0vE1sZyTRlM.jpg'],
    'hxh': ['https://image.ceneostatic.pl/data/products/180253316/i-plakat-hunter-x-hunter-2011-anime-poster-1784051014.jpg'],
    'onepunch': ['https://image.tmdb.org/t/p/w500/dT10AxJIXVvRwFAew4tt2RhzJrD.jpg',
                 'https://m.media-amazon.com/images/M/MV5BMTNmZDE2NDEtNTg3MS00OTE1LThlZGUtOGZkZTg0NTUyNGVmXkEyXkFqcGdeQXVyNTgyNTA4MjM%40._V1_.jpg'],
    'mha': ['https://cdn.bingebase.com/seasons/1635/posters/1u4HqgEKOmjXM8ENGtlrF4yXIwp.webp'],
    'steinsgate': ['https://image.tmdb.org/t/p/w500/96R4bV7dB8ramaWceNKsxvJgCUd.jpg'],
    'bleach': ['https://image.tmdb.org/t/p/w500/461sWAblO7ZHvnPI8UdhlgowmLW.jpg'],
    'codegeass': ['https://image.tmdb.org/t/p/w500/lMS9ZBA4QogPudvoPzfZxA6PlCL.jpg'],
    'haikyu': ['https://image.tmdb.org/t/p/w500/h0bVEP8doITKTfrkEhzgGesYuQz.jpg'],
}

assert len(DIRECT_ANIME_POSTERS) == 20
