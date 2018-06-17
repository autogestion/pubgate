
## Web-server which supports activitypub protocol


## Endpoints

 - /.well-known/
 - /user/
 - /inbox
 - /outbox

## Api docs

 - /swagger

## Run

```shell
$ git clone https://github.com/autogestion/pubgate.git
$ pip install -r requirements.txt
$ cp -r config/sample_conf.cfg config/conf.cfg
python run_api.py
```