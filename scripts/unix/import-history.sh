#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/../../server/ && pipenv run python console.py extract_history london
cd $DIR/../../server/ && pipenv run python console.py extract_history beijing