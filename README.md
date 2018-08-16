
## Asyncronous Lightweight ActivityPub API
Based on [little-boxes](https://github.com/tsileo/little-boxes).
Implements both the client-to-server API and the federated server-to-server API.

Compatible with [Mastodon](https://github.com/tootsuite/mastodon), but will drop OStatus messages.

(will) Support extensions

## Endpoints

 - /.well-known/    (webfinger)
 - /user/           (create, profile, following)
 - /inbox/          (create, list)
 - /outbox/         (create, list, item, activity, remote post)
 - /swagger         (api docs)

Full list of endpoints and their payloads available as [Postman collection](https://github.com/autogestion/pubgate/blob/master/pubgate.postman_collection.json)
or as [swagger docs example](http://pubgate.autogestion.org/swagger)


## Run

### Prerequisites
`MongoDB`

### Shell

```
git clone https://github.com/autogestion/pubgate.git
pip install -r requirements.txt
cp -r config/sample_conf.cfg config/conf.cfg
python run_api.py
```