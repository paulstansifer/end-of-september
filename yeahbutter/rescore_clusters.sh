YB=/Users/paul/src/yeahbut/

echo scoring...
$YB/build/cpp/score -p 1.0 -c cluster_assignments -v ex.users_* | sort -n | tee temp_scores_inbetween |  $YB/yeahbutter/recover_netflix_titles.pl ex.map_articles ../../movie_titles.txt ../average_scores /dev/stdin | sort -n > temp_scores

echo rating...
$YB/yeahbutter/rate.pl --yb_scores temp_scores --ratings $YB/yeahbutter/ratings.txt --source ebert --source mc --source ord_nf --source ord_yb > i_e_m_n_y.matrix



cat <<EOF > r_script
dat <- read.table("i_e_m_n_y.matrix");
colnames(dat) <- c("id", "ebert", "mc", "nf", "yb");
#plot(dat)

train <- dat[(1:(dim(dat)[1]/2))*2, ]    
test  <- dat[(1:(dim(dat)[1]/2))*2-1, ]   #for cross-validation

#train <- dat
#test <- dat  #temporary -- cross-validation is killing us with so little data

rmsep <- function(x) sqrt(mean((predict(x, data=test) - test\$ebert)^2))

rmsep(lm(ebert ~ mc, data=test))

rmsep(lm(ebert ~ nf, data=test))
rmsep(lm(ebert ~ nf+yb, data=test))
rmsep(lm(ebert ~ yb, data=test))
rmsep(lm(mc ~ nf, data=test))
rmsep(lm(mc ~ nf+yb, data=test))
rmsep(lm(mc ~ yb, data=test))
EOF

echo ............................
cat r_script | R --vanilla --interactive | tail -n 16