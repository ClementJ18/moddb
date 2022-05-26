if [$1 == "full"]
then
    pytest -k test_main --log-level="INFO" --html=report.html --self-contained-html "${@:2}"
else
    pytest -k "not test_main" -k "not test_client" --log-level="INFO" --html=report.html --self-contained-html "$@"
fi