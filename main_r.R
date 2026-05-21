library(randomForest)
library(tictoc)

pkgs <- c("randomForest", "tictoc")
for (p in pkgs) {
  if (!requireNamespace(p, quietly = TRUE)) install.packages(p, repos = "https://cloud.r-project.org")
}

calc_mcc <- function(actual, predicted) {
  tp <- sum(actual == 1 & predicted == 1)
  tn <- sum(actual == 0 & predicted == 0)
  fp <- sum(actual == 0 & predicted == 1)
  fn <- sum(actual == 1 & predicted == 0)
  denom <- sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
  if (denom == 0) return(0)
  return((tp * tn - fp * fn) / denom)
}

dataset_dir <- "/progetto/five_EHRs_public_datasets/"
csv_files <- list.files(dataset_dir, pattern = "\\.csv$", full.names = TRUE)

all_results <- list()

tic()

for(csv_path in csv_files){
  dataset_name <- tools::file_path_sans_ext(basename(csv_path))
  cat(sprintf("\nProcessing dataset %s\n", dataset_name))

  df <- read.csv(csv_path)
  target_col <- ncol(df)
  X <- df[, -target_col]
  y <- df[, target_col]  # numerico 0/1

  # Rimuovi feature a varianza zero (ottimizzazione)
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
  cat(sprintf("%s: MCC = %.4f ± %.4f\n", dataset_name, mean_mcc, std_mcc))

  all_results[[dataset_name]] <- data.frame(
    dataset  = dataset_name,
    mean_mcc = mean_mcc,
    std_mcc  = std_mcc
  )
}

elapsed <- toc(quiet = TRUE)
total_time <- elapsed$toc - elapsed$tic
cat(sprintf("\nTotal time: %.2f seconds\n", total_time))

# Salva risultati
results_dir <- "/progetto/results"
if (!dir.exists(results_dir)) dir.create(results_dir)

results_df <- do.call(rbind, all_results)
write.csv(results_df, file.path(results_dir, "r_results.csv"), row.names = FALSE)