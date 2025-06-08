if [ ${1:-not_full} == "full" ]
then
    python -m pytest -k "main and not test_client and not TestLogin" --log-level="INFO" --html=report.html --self-contained-html --record-mode=new_episodes -vv "${@:2}"
else
    python -m pytest -k "not main and not test_client and not TestLogin" --log-level="INFO" --html=report.html --self-contained-html --record-mode=new_episodes -vv "$@"
fi
