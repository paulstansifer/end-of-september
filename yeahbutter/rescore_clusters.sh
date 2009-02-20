YB=/Users/paul/src/yeahbut/

echo scoring...
$YB/build/cpp/score -p 0.80 -c cluster_assignments -v ex.users_* | sort -n |  $YB/yeahbutter/recover_netflix_titles.pl ex.map_articles ../../movie_titles.txt ../average_scores /dev/stdin > temp_scores

echo rating...
$YB/yeahbutter/rate.pl --yb_scores temp_scores --ratings $YB/yeahbutter/ratings.txt --source ebert --source ord_mc --source ord_nf --source ord_yb > i_e_m_n_y.matrix



cat <<EOF >r_script
dat <- read.table("i_e_m_n_y.matrix");
colnames(dat) <- c("id", "ebert", "mc", "nf", "yb");


train <- dat[(1:(dim(dat)[1]/2))*2, ]    
test  <- dat[(1:(dim(dat)[1]/2))*2-1, ]   #for cross-validation

rmsep <- function(x) sqrt(mean((predict(x, data=test) - dat$ebert)^2))

nf.ebert <- lm(ebert ~ nf, data=train);
yb.ebert <- lm(ebert ~ yb, data=train);

rmsep(nf.ebert)
rmsep(yb.ebert)
EOF