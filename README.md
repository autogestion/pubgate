<img src="https://user-images.githubusercontent.com/1098257/83571569-eb642700-a51f-11ea-8fca-c2b61798a4ce.png" width="200" height="200">
![python_version](https://img.shields.io/badge/python-3.7-blue.svg)


## Asyncronous Lightweight ActivityPub API / CMS
Implements both the client-to-server(C2S) API and the federated server-to-server(S2S) API.
 - S2S compatible with Mastodon, Pixelfed, Pleroma and microblog.pub

Can do create / delete / un-/follow users / share / like / undo

The idea is to develop PubGate as CMS, which could be used same as WordPress -
easy install on cheap hosting with customization by installing plugins and choosing themes.
As far as it based on asynchronous python framework,
which provides non-blocking delivery of AP objects to other instances, it supposed to be light and fast.

##### Support extensions (collects blueprints and tasks):

 - [pubgate-rssbot](https://github.com/autogestion/pubgate-rssbot):  federates rss-feeds*
 - [pubgate-telegram](https://github.com/autogestion/pubgate-telegram):  Telegram <-> ActivityPub bridge
 - [pubgate-steemit](https://github.com/autogestion/pubgate-steemit):  Steemit Blog -> ActivityPub bridge
 - [pubgate-philip](https://github.com/autogestion/pubgate-philip):  minimalist blogging js client, Svelte framework (beta)*

### API documentation
Overview [swagger docs example](http://pubgate.autogestion.org/swagger)

More details at [Postman documenter](https://documenter.getpostman.com/view/4625755/RzZCFdXv) or download latest [Postman collection](https://github.com/autogestion/pubgate/blob/master/pubgate.postman_collection.json)

## Deploy
### Docker
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

### Manual deploy on Android device
Guide from [@traumschule](https://github.com/traumschule)

Could be used for manual install on Ubuntu/Debian as well

##### Install dory mongodb server and termux

#### In termux:
```
pkg install git python make
git clone https://github.com/autogestion/pubgate
pip install -r requirements/base.txt
pip install -r requirements/extensions.txt
cp config/extensions_sample_conf.cfg config/conf.cfg
```
edit config/conf.cfg and change example.com to ip address and https to http (for dev instance)
```
python run_api.py
```

### Tests

```
python -m pytest tests/
```