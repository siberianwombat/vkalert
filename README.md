# requirements:

* python
* `vk_api` python lib: `pip install vk_api`
* vk.com login
* slack webhook url: (https://api.slack.com/incoming-webhooks)

# running
Copy `vkalert.cfg.dist` to `vkalert.cfg` and change configuration parameters in it.
Run `read.py --debug` to check it works.
Schedule as cronjob every N minutes.
