' runs test1.html against FF
'saves results as results_fx_kdi-dev_OSI_all_suite.html

echo " runs test1.html against FF"
echo "saves results as results_fx_kdi-dev_OSI_all_suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "http://kdi-dev.sixfeetup.com:80/" "../OSI_suite.html" "../log/results_fx_kdi-dev_OSI_Suite.html"

