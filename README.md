# timew-sawayo

Sync timew work intervals to [sawayo](https://sawayo.de)

## Installation
```bash
pip install .
ln -s ~/.local/bin/sawayo-sync ~/.config/timewarrior/extensions/
```

## Configure
Use the browser devtools to extract your auth token.  
Edit `~/.config/timewarrior/timewarrior.cfg` and add:
```
sawayo-sync-token = "your_token_here"
```

## Run
This starts syncing intervals backwards in time to sawayo. 
If there is any entry for the interval day on sawayo, it stop's syncing.
```bash
timew sawayo-sync
```
