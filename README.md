![python_version](https://img.shields.io/badge/python-3.6-blue.svg)

## Asyncronous Lightweight ActivityPub API
Based on [little-boxes](https://github.com/tsileo/little-boxes).
Implements both the client-to-server API and the federated server-to-server API.
Compatible with Mastodon, Pleroma/litepub and microblog.pub

##### Support extensions (collects blueprints and listeners):

 - [pubgate-rssbot](https://github.com/autogestion/pubgate-rssbot):  federates rss-feeds*

## Endpoints

#### Federated

 - /.well-known/    (webfinger, nodeinfo)
 - /user/           (create, profile, token(password grant OAuth 2), following)
 - /inbox/          (create, list)
 - /outbox/         (create, list, details)
 

#### Additional
 - /swagger         (api docs)



#### API documentation:

[![Run in Postman](https://run.pstmn.io/button.svg)](https://documenter.getpostman.com/view/4625755/RzZCFdXv) 
or [swagger docs example](http://pubgate.autogestion.org/swagger)

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