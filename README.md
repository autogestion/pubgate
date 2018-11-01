
## Asyncronous Lightweight ActivityPub API
Based on [little-boxes](https://github.com/tsileo/little-boxes).
Implements both the client-to-server API and the federated server-to-server API.

Compatible (tested) with Mastodon, Pleroma and microblog.pub

##### Support extensions(collects blueprints and listeners):

 - [pubgate-rssbot](https://github.com/autogestion/pubgate-rssbot):  federates rss-feeds*

## Endpoints

#### Federated

 - /.well-known/    (webfinger)
 - /user/           (profile, following)
 - /inbox/          (create, list)
 - /outbox/         (create, list, item, activity, remote post)
 

#### Additional
 - /auth            (create user, get token)
 - /swagger         (api docs)

Full list of endpoints and their payloads available as [Postman collection](https://github.com/autogestion/pubgate/blob/master/pubgate.postman_collection.json)
or as [swagger docs example](http://pubgate.autogestion.org/swagger)


## Run

#### Prerequisites
`MongoDB`
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