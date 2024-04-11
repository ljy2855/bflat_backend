## bflat backend
model serving을 위한 API backend


### setup
#### set up virtual env
`python -m venv venv`

`source venv/bin/activate` #for mac,ubuntu

or

`venv\Scripts\activate` #for windows

#### get required package
`pip install -r requirements.txt`

### local test
#### Flask run
`python main.py`


### deploy (AWS)
#### AWS setup
```sh
pip install awscli
aws configure
```

### deploy to AWS lambda
`zappa deploy dev`