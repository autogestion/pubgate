![python_version](https://img.shields.io/badge/python-3.7-blue.svg)

## Asyncronous Lightweight ActivityPub API / CMS
Based on [little-boxes](https://github.com/tsileo/little-boxes).
Implements both the client-to-server(C2S) API and the federated server-to-server(S2S) API.
 - S2S compatible with Mastodon, Pixelfed, Pleroma and microblog.pub

The idea is to develop PubGate as CMS, which could be used same as WordPress - 
easy install on cheap hosting with customization by installing plugins and choosing themes.
As far as it based on asynchronous python framework, 
which provides non-blocking delivery of AP objects to other instances, it supposed to be light and fast.


##### Support extensions (collects blueprints and tasks):

 - [pubgate-rssbot](https://github.com/autogestion/pubgate-rssbot):  federates rss-feeds*
 - [pubgate-telegram](https://github.com/autogestion/pubgate-telegram):  Telegram <-> ActivityPub bridge
 - [pubgate-steemit](https://github.com/autogestion/pubgate-steemit):  Steemit Blog -> ActivityPub bridge
 - [pubgate-philip](https://github.com/autogestion/pubgate-philip):  minimalist blogging js client, Svelte framework (alpha)*

### API documentation
Support create / delete / un-/follow users / share / like / undo

#### Endpoints
Overview [swagger docs example](http://pubgate.autogestion.org/swagger)
##### ActivityPub
 - /user/           (create, profile, token(password grant OAuth 2), following/ers, liked)
 - /inbox/          (create, list)
 - /outbox/         (create, list, details (replies, likes, shares))
##### Additional
 - /.well-known/    (webfinger, nodeinfo)
 - /timeline        (local, federated)
 - /swagger         (api docs)

More details:

At [Postman documenter](https://documenter.getpostman.com/view/4625755/RzZCFdXv) or download latest [Postman collection](https://github.com/autogestion/pubgate/blob/master/pubgate.postman_collection.json)

## Run

#### Prerequisites
`MongoDB 3.6, Python 3.7`
#### Shell
```
git clone https://github.com/autogestion/pubgate.git
pip install -r requirements/base.txt
```
##### Only federator
```
cp -r config/base_sample_conf.cfg config/conf.cfg
```
##### To run with extensions (marked * in list )
```
pip install -r requirements/extensions.txt
cp -r config/extensions_sample_conf.cfg config/conf.cfg
```

###### Update config/conf.cfg with your domain name
##### Run

```
python run_api.py
```

### Tests

```
python -m pytest tests/
```
