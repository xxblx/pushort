pushort 
=======

pushort is a tool prototype for URL shortening.

* Python3.6+
* Tornado 
* MongoDB 

In the first time the short part of the url creates as blake2b hash (digest size == 5) of the long url. If created short part already exists in the database, the app creates the new hash with random key, personalization and salt. The tool uses blake2b because blake has good speed.

For example `https://duckduckgo.com/?q=here+is+some+text%2C+word%2C+word2+and+word3&t=ffab&ia=qa` transforms into `http://example.com/932a7a7931`. 

On self-generated dataset of 2 389 815 random URLs by the test results 99.99% (2 389 813) URLs had got the unique short part in the first time. Dataset was created from top 1 000 000 domains from Alexa rank and random english words for the paths (endpoints) and GET queries parameters. 

# Usage 
* Create database indexes - `init_db.py`
* Run server - `run_server.py`
* Open `http://127.0.0.1:8888`
* Send POST to `http://127.0.0.1:8888/api` with `long_url` and `expires_in` parameters. 

If you don't want to create all indexes, modify `init_db.py` and create only TTL index `expire_time`. The index is need for auto deletion of expired URLs. 

Expired urls may exist for some time after expires_time is over because the background task that removes expired documents in MongoDB runs every 60 seconds. See [MongoDB docs](https://docs.mongodb.com/manual/core/index-ttl/#timing-of-the-delete-operation) for the details. 
