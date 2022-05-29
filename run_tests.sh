if [ $1 == "full" ]
then
    pytest tests/test_main.py --log-level="INFO" --html=report.html --self-contained-html "${@:2}"
else
    pytest -k "not test_main and not test_client" --log-level="INFO" --html=report.html --self-contained-html "$@"
fi
