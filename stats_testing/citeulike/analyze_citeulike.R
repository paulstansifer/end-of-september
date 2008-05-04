require(e1071)

k5 <- data.frame(as.matrix(read.matrix.csr("straight-key_users300")$x))
pca <- prcomp(k5, scale=FALSE)

plot(predict(pca,k5), col="red", type="n")


for(file in dir(".", pattern="straight-users_.*")) {
	more_users <- data.frame(as.matrix(read.matrix.csr(file)$x))
	points(predict(pca,more_users))
}	

points(predict(pca,k5), col="red")

#6 and 3 are very far apart
#6 and 7 are close.  



#k5 <- read.csv("key_users", header=FALSE)[,-1]
#pca <- prcomp(k5, scale=FALSE)

#plot(predict(pca,k5), col="red", xlim=c(-0.1,0.1), ylim=c(-0.1,0.1))

#for(file in dir(".", pattern="users.*csv")) {
#	more_users <- read.csv(file, header=FALSE)[,-1]
#	points(predict(pca,more_users))
#}	


#points(predict(pca,k5), col="red")