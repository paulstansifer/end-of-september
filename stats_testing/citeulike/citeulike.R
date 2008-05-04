# Testing code to work with the CiteULike data set
# Daniel Klein and Paul Stansifer, 1/19/2008

cite <- read.table("cl150k", sep="|", colClasses=c("character", "character", "character","character"), col.names=c("article","user","time","tag"))
cite <- cite[,1:2]

build.mat <- function(data.set, user.subset) {
	cols <- unique(data.set$article)
	rows <- unique(user.subset)
	mat <- matrix(0, nrow=length(rows), ncol=length(cols))
	colnames(mat) <- cols
	rownames(mat) <- rows
	for(r in 1:dim(data.set)[1]) {
		if(data.set$user[r] %in% rows) {
			row.idx <- which(data.set$user[r] == rows)
			col.idx <- data.set$article[r]
			mat[row.idx, col.idx] <- 1
		}
	}
	return(mat)
}