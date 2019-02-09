![python_version](https://img.shields.io/badge/python-3.6-blue.svg)

## Asyncronous Lightweight ActivityPub API
Based on [little-boxes](https://github.com/tsileo/little-boxes).
Implements both the client-to-server API and the federated server-to-server API.
Compatible with Mastodon, Pleroma and microblog.pub


##### Support extensions (collects blueprints):

 - [pubgate-rssbot](https://github.com/autogestion/pubgate-rssbot):  federates rss-feeds*
 - [pubgate-philip](https://github.com/autogestion/pubgate-philip):  minimalist blogging UI(early development)*

### API documentation
Support create / delete / un-/follow users / share / like / undo

#### Endpoints
Overview [swagger docs example](http://pubgate.autogestion.org/swagger)
##### Federated
 - /.well-known/    (webfinger, nodeinfo)
 - /user/           (create, profile, token(password grant OAuth 2), following, liked)
 - /inbox/          (create, list)
 - /outbox/         (create, list, details)
##### Additional
 - /timeline        (local, federated)
 - /swagger         (api docs)

More details:

At [Postman documenter](https://documenter.getpostman.com/view/4625755/RzZCFdXv) or download latest [Postman collection](https://github.com/autogestion/pubgate/blob/master/pubgate.postman_collection.json)

## Run

#### Prerequisites
`MongoDB, Python3.6`
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
##### Run

```
python run_api.py
```

### Tests

```
python -m pytest tests/
```
