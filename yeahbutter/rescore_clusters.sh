YB=/Users/paul/src/yeahbut/

echo scoring...
$YB/build/cpp/score -p 0.6 -c cluster_assignments -v ex.users_* | sort -n | tee temp_scores_inbetween |  $YB/yeahbutter/recover_netflix_titles.pl ex.map_articles ../../movie_titles.txt ../average_scores /dev/stdin 0.0 | sort -n > temp_scores

echo rating...
$YB/yeahbutter/rate.pl --yb_scores temp_scores --ratings $YB/yeahbutter/ratings.txt --source ebert  --source mc --source nf --source yb > i_e_m_n_y.matrix

echo ............................
R --vanilla --interactive < $YB/yeahbutter/rescore.R | tail -n 32