if [ ${1:-not_full} == "full" ]
then
    pytest -k "extended" --log-level="INFO" --html=report.html --self-contained-html --record-mode=all "${@:2}"
else
    pytest -k "standard" --log-level="INFO" --html=report.html --self-contained-html --record-mode=new_episodes "$@"
fi
