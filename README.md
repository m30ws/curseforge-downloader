# curseforge-downloader
Command-line downloader for Minecraft Curseforge modpacks

## Why
Whoever used CurseForge/Overwolf software probably isn't going to need an explanation for why, it is mostly comprised of bloat which is usually getting on my nerves too much to use it as intended so i put together this downloader.

## Example
I left in an example for Curseforge's Better MC 4 modpack (https://www.curseforge.com/minecraft/modpacks/better-mc-forge-bmc4) and a few additional mods.

#### Execute script using:
    $ py -3.9 curseforge_downloader.py <modpack_zip_file.zip> <additional_curse_mods.json> <additional_mods.json>

\* At this time the code is assuming all mods and additional files are are in curseforge format so `additional_mods.json` support needs to be patched in.

#### In this case the command would be:
    $ py curseforge_downloader.py "Better+MC+[FORGE]+1.20.1+v24+HF.zip" additional_curse_mods.json
which will when finished create a directory `Better MC [FORGE] 1.20.1 v24 HF Downloaded` with the contents of:
- `Better+MC+[FORGE]+1.20.1+v24+HF.zip/overrides/`
- Forge installer for version specified in manifest.json
- mods downloaded to `mods/`

Python's `urllib` is used instead od `requests` to avoid having to `pip install requests`.