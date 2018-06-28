
## Frontendles ActivityPub API
Based on [little-boxes](https://github.com/tsileo/little-boxes)
Implements both the client to server API and the federated server to server API.
Compatible with [Mastodon](https://github.com/tootsuite/mastodon) (which is not following the spec closely), but will drop OStatus messages.
Support extensions

## Endpoints

 - /.well-known/    +
 - /user/           +
 - /inbox/
 - /outbox/         -/+
Full list of endpoints and their payloads avalaible in [Postman collection](https://github.com/autogestion/pubgate/blob/master/pubgate.postman_collection.json)

## Api docs

 - /swagger

## Run

### Prerequisites
`MongoDB`

### Shell

```
$ git clone https://github.com/autogestion/pubgate.git
$ pip install -r requirements.txt
$ cp -r config/sample_conf.cfg config/conf.cfg
python run_api.py
```