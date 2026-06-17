args <- commandArgs(trailingOnly = TRUE)
if (length(args) > 2) {
  stop("Usage: Rscript main_r.R [dataset_dir] [results_dir]")
}
csv_path <- args[1]
results_dir <- args[2]

library(randomForest)

if (!requireNamespace("randomForest", quietly = TRUE)) {
    install.packages("randomForest", repos = "https://cloud.r-project.org")
}

calc_mcc <- function(actual, predicted) {
  classes <- levels(as.factor(c(actual, predicted)))
  if(length(classes) < 2) return(0)
  class_neg <- classes[1]
  class_pos <- classes[2]
  tp <- sum(actual == class_pos & predicted == class_pos)
  tn <- sum(actual == class_neg & predicted == class_neg)
  fp <- sum(actual == class_neg & predicted == class_pos)
  fn <- sum(actual == class_pos & predicted == class_neg)
  denom <- sqrt(as.numeric(tp + fp) * as.numeric(tp + fn) * as.numeric(tn + fp) * as.numeric(tn + fn))
  if (denom == 0) return(0)
  return((tp * tn - fp * fn) / denom)
}

dataset_name <- tools::file_path_sans_ext(basename(csv_path))
cat(sprintf("R sta elaborando il dataset: %s\n", dataset_name))

df <- read.csv(csv_path)
target_col <- ncol(df)
X <- df[, -target_col]
y <- df[, target_col]

variances <- apply(X, 2, var)
X <- X[, variances > 0, drop = FALSE]

n <- nrow(df)
test_sz <- round(n * 0.2)
mccs <- numeric(100)

for (i in 1:100) {
  set.seed(i)
  idx_test  <- sample(1:n, test_sz)
  idx_train <- setdiff(1:n, idx_test)

  X_train <- X[idx_train, , drop = FALSE]
  y_train <- as.factor(y[idx_train])
  X_test  <- X[idx_test,  , drop = FALSE]
  y_test  <- y[idx_test]

  clf <- randomForest(
    x = X_train,
    y = y_train,
    ntree = 30,
    maxnodes = 31,
    importance = FALSE
  )

  y_pred <- as.numeric(as.character(predict(clf, X_test)))
  mccs[i] <- calc_mcc(y_test, y_pred)
}

mean_mcc <- mean(mccs, na.rm = TRUE)
std_mcc  <- sd(mccs, na.rm = TRUE)
cat(sprintf("Risultato R per %s: MCC = %.4f ± %.4f\n", dataset_name, mean_mcc, std_mcc))

results_df <- data.frame(
  dataset  = dataset_name,
  mean_mcc = mean_mcc,
  std_mcc  = std_mcc
)

output_file <- file.path(results_dir, "training_results_r.csv")
write.csv(results_df, output_file, row.names = FALSE)