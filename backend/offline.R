require(e1071)
require(igraph)

loc <- "/Users/paul/Desktop/netflix/ex/"

d <- 7
small.distance <- 0.1

key.users <- data.frame(as.matrix(read.matrix.csr(loc+"ex.key_users")$x))

pca <- prcomp(key.users, scale=FALSE)

plot(predict(pca, key.users), col = 'red')

#TODO: prefill arrays of the correct size with NA
raw <- c()
accum <- c()

for(file in dir(loc, pattern="ex.users_.*")) {
	more.users <- data.frame(as.matrix(read.matrix.csr(file)$x))
	raw <- rbind(raw, more.users)
	accum <- rbind(accum, predict(pca, more.users)[,1:d])
}

points(accum, col = 'black')
points(predict(pca, key.users), col = 'red')

total.users <- dim(accum)[1]

clusters <- kmeans(accum, sqrt(total.users)/2)

distances <- as.matrix(dist(clusters$centers))
complete.graph <- graph.adjacency(distances, weighted=TRUE)
mst <- minimum.spanning.tree(complete.graph)
smallish.distances <- apply(distances, c(1,2), function(x) {if(x > small.distance) 0 else x})
community.connections <- graph.union(graph.adjacency(smallish.distances), mst)

write(t(accum), file="pcaed_users", ncolumns=dim(accum)[2])
write(t(clusters$cluster), file="cluster_assignments", ncolumns=1)
write(t(clusters$centers), file="cluster_centers", ncolumns=dim(clusters$centers)[2])

#pairs of connected nodes, as rows
write(t(cbind(unlist(community.connections[3]), unlist(community.connections[4]))), file="cluster_connections", ncolumns=2)
articles <- 1:(dim(raw)[2])
overall.value <- cbind(articles, articles)
for(article in articles) {
	clustered.votes <- 1:length(clusters$size) * 0
	for(voter in 1:(dim(raw)[1])) {
		if(raw[voter,article] > 0) {
			voter.cluster <- clusters$cluster[voter] 
			clustered.votes[voter.cluster] <- clustered.votes[voter.cluster] + 1
			#total.value <- total.value + 1/clusters$size[clusters$cluster[voter]]
		}
	}
	total.value <- sum((clustered.votes / clusters$size)^(1/4))
	overall.value[article,2] <- total.value
}
