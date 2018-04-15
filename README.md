pushort 
=======

# Description

pushort is a simple opensource tool for URL shortening.

* Python3.6+
* Tornado 
* MongoDB 

In first time the short part of the url creates as blake2b hash (digest size == 5) of the long url. If created short part already exists in the database, app creates the new with random key, personalization and salt. The tool uses blake2b because blake has good speed.

For example `https://duckduckgo.com/?q=here+is+some+text%2C+word%2C+word2+and+word3&t=ffab&ia=qa` transforms into `http://example.com/932a7a7931`. 

On self-generated dataset of 2 389 815 random URLs 2 389 813 URLs had got the unique short part in the first time. Dataset was created from top 1 000 000 domains from Alexa rank and random english words for the paths (endpoints) and GET queries parameters. 

# Usage 
* Create database indexes - `init_db.py`
* Run server - `run_server.py`
* Open `http://127.0.0.1:8888`
* Send POST to `http://127.0.0.1:8888/api` with `long_url` and `expires_in` parameters. 

If you don't want to create all indexes, modify `init_db.py` and create only the TTL index `expire_time`. The index is need for auto deletions of expired URLs. 

