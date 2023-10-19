if [ ${1:-not_full} == "full" ]
then
    pytest -k "main" --log-level="INFO" --html=report.html --self-contained-html --record-mode=new_episodes -vv "${@:2}"
else
    pytest -k "not main" --log-level="INFO" --html=report.html --self-contained-html --record-mode=new_episodes -vv "$@"
fi
