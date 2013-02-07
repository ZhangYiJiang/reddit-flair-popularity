A very simple Python script that counts the popularity of flairs in a 
subreddit. Collects (by default) the flairs of the poster and commentators 
on the first 400 posts sorted by hot in a subreddit. 

## Usage

1. Edit `config.json`. See `mylittlepony.config.json` for example. The only 
two settings that *must* be changed are `subreddit` and `userAgent`. 
2. Run `python popularity.py config.json`. The script too around 21 minutes to run locally. 
Your time will depend on how heavy reddit's server are at the moment. By 
default the script will pause for 2 hours after that before running again - 
it is designed to be run on a server as a long running script. 