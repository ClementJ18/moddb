if [ ${1:-not_full} == "full" ]
then
    pytest tests/test_main.py --log-level="INFO" --reruns 3 --reruns-delay 15 --html=report.html --self-contained-html "${@:2}"
else
    pytest -k "not test_main and not test_client" --log-level="INFO" --reruns 3 --reruns-delay 15 --html=report.html --self-contained-html "$@"
fi
