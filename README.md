### bflat backend
model serving을 위한 API backend


### setup
`python -m venv venv`

`source venv/bin/activate` #for mac,ubuntu

or

`venv\Scripts\activate` #for windows

`pip install -r requirements.txt`

```sh
pip install awscli
aws configure
```

### deploy (AWS)
`zappa deploy dev`