num.centers <- 8
sd.center <- 1.6
sd.user <- 0.2
post.min <- -4
post.max <- 4
user.min <- 15
user.max <- 80
num.posts <- 300
read.prob <- 0.3
disagreement.radius <- 1.8

sink("model_output.dat")

cluster.centers <- data.frame(x=rnorm(num.centers, 0, sd.center),
                              y=rnorm(num.centers, 0, sd.center))

users <- data.frame()
for(c in 1:dim(cluster.centers)[1]) {
	num.users <- sample(user.min:user.max, 1)
	for(i in 1:num.users) {
		user.x <- cluster.centers[c,1] + rnorm(1, 0, sd.user)
		user.y <- cluster.centers[c,2] + rnorm(1, 0, sd.user)
		users <- rbind(users, c(user.x, user.y))
	}
}
num.users <- dim(users)[1]

posts <- data.frame(x=runif(num.posts, post.min, post.max),
                    y=runif(num.posts, post.min, post.max))
votes <- data.frame()
for(u in 1:num.users) {
	read.article <- rbinom(num.posts, 1, read.prob)
	for(p in 1:num.posts) {
		if(read.article[p] == 1) {
			disagreement <- sqrt(sum((users[u,]-posts[p,])^2))
			if(disagreement < disagreement.radius) {
				cat(paste(c(p, u), collapse="|"))
				cat("\n")
			}
		}
	}
}

q(runLast=FALSE)
