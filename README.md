![python_version](https://img.shields.io/badge/python-3.7-blue.svg)

## Asyncronous Lightweight ActivityPub API
Based on [little-boxes](https://github.com/tsileo/little-boxes).
Implements both the client-to-server(C2S) API and the federated server-to-server(S2S) API.
 - S2S compatible with Mastodon, Pixelfed, Pleroma and microblog.pub

Can do create / delete / un-/follow users / share / like / undo

##### Support extensions (collects blueprints and tasks):

 - [pubgate-rssbot](https://github.com/autogestion/pubgate-rssbot):  federates rss-feeds*
 - [pubgate-telegram](https://github.com/autogestion/pubgate-telegram):  Telegram <-> ActivityPub bridge
 - [pubgate-steemit](https://github.com/autogestion/pubgate-steemit):  Steemit Blog -> ActivityPub bridge
 - [pubgate-philip](https://github.com/autogestion/pubgate-philip):  minimalist blogging js client, Svelte framework (alpha)*

### API documentation
Overview [swagger docs example](http://pubgate.autogestion.org/swagger)

More details at [Postman documenter](https://documenter.getpostman.com/view/4625755/RzZCFdXv) or download latest [Postman collection](https://github.com/autogestion/pubgate/blob/master/pubgate.postman_collection.json)

## Deploy
###### Install Docker + Docker Compose
#### Shell
```
git clone https://github.com/autogestion/pubgate.git
cp -r config/extensions_sample_conf.cfg config/conf.cfg
```
###### Check/Edit config/conf.cfg to change setup of your instance 
(registration status, title and description for UI App)

Then, instance could be started
```
domain=put-your-domain-here.com docker-compose up -d
```

This will install PubGate with extensions (marked * in list ). 
For custom configuration edit requirements/extensions.txt and config/conf.cfg . 
To install federator without extensions, empty requirements/extensions.txt and use 
config/base_sample_conf.cfg

### Tests

```
python -m pytest tests/
```
