if [ ${1:-not_full} == "full" ]
then
    pytest tests/extended --log-level="INFO" --html=report.html --self-contained-html "$@" --record-mode=all
else
    pytest tests/standard --log-level="INFO" --html=report.html --self-contained-html "$@"  --record-mode=new_episodes
fi
