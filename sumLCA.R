library(poLCA)
library(ggplot2)

factorsConvert <- function(df, exclude_columns = NULL) {
  for (col_name in colnames(df)) {
    if (!(col_name %in% exclude_columns)) {
      df[[col_name]] <- as.factor(df[[col_name]])
    }
  }
  return(df)  # Return the modified dataframe
}

defineClustersNumber <- function(df, formula, totaL_classes, maxiter = 10000) {
  n_classes = 2:totaL_classes
  bic_values <- numeric(length(n_classes))
  aic_values <- numeric(length(n_classes))
  observations_per_class <- list()
  class_shares <- list()
  
  # Loop through different numbers of classes
  for (k in n_classes) {
    # Fit the LCA model
    model <- poLCA(formula, df, nclass = k, maxiter = maxiter, graphs = FALSE,
                   nrep = 20)
    
    # Store the AIC and BIC values
    aic_values[k - 1] <- model$aic
    bic_values[k - 1] <- model$bic
    
    # Store the posterior probabilities (probabilities of each observation for each class)
    posterior_probs <- model$posterior
    
    # Calculate the population shares for each class (sum of posterior probabilities for each class)
    class_shares[[as.character(k)]] <- colSums(posterior_probs) / nrow(posterior_probs)
    
    # Get the predicted class assignments
    predicted_classes <- model$predclass
    
    # Count the number of observations in each class
    class_counts <- table(predicted_classes)
    
    # Store the proportion of observations in each class for the current model
    observations_per_class[[as.character(k)]] <- class_counts / sum(class_counts)
  }
  
  # Create the plot with BIC and AIC values for different numbers of classes
  p = ggplot(data.frame(
    n_classes = rep(n_classes, 2),
    criterion_value = c(bic_values, aic_values),
    criterion = rep(c("BIC", "AIC"), each = length(n_classes))
  ), aes(x = n_classes, y = criterion_value, color = criterion, shape = criterion)) +
    geom_point() +  # Add points
    geom_line() +   # Add lines
    labs(
      x = "Number of Classes",
      y = "Criterion Value",
      title = "BIC and AIC for Different Number of Latent Classes"
    ) +
    scale_color_manual(values = c("blue", "red")) +  # Set custom colors for BIC and AIC
    scale_shape_manual(values = c(19, 19)) +  # Use circles for both
    theme_bw()  # Use a minimal theme
  
  # Print summary of BIC, AIC, class population shares, and proportions of observations per class
  cat("\nSummary of BIC, AIC, Class Population Shares, and Number of Observations Allocated to Each Class:\n")
  for (k in n_classes) {
    cat("\nModel with", k, "classes:\n")
    cat("BIC:", bic_values[k - 1], "\n")
    cat("AIC:", aic_values[k - 1], "\n")
    # cat("Estimated Class Population Shares:", paste(round(class_shares[[as.character(k)]], 4), collapse = ", "), "\n")
    # cat("Proportion of Observations per Class:\n")
    # print(round(observations_per_class[[as.character(k)]], 4))  # Show proportions
  }
  return(p)
}

csv_link = '/Users/panosgtzouras/Desktop/datasets/csv/SUMsurveyData/finalDatasets/SumSurveySocioV1.csv'
df = read.csv(csv_link)

# exclude = c("pid", "gender", "age", "educ", "employ")

sele = c("gender", "age", "educ", "employ", "income")

df = factorsConvert(df)

formula = as.formula(paste("cbind(", paste(sele, collapse = ", "), ") ~1"))

defineClustersNumber(df, formula, 10, maxiter = 10000)

# lca_model <- poLCA(formula, df, nclass = 4, maxiter = 10000, graphs = FALSE,
#                   nrep = 10)
# lca_model$posterior

defineClustersNumber2 <- function(df, formula, totaL_classes, maxiter = 10000) {
  n_classes <- 2:totaL_classes
  bic_values <- numeric(length(n_classes))
  aic_values <- numeric(length(n_classes))
  aBIC_values <- numeric(length(n_classes))
  CAIC_values <- numeric(length(n_classes))
  logLik_values <- numeric(length(n_classes))
  npar_values <- numeric(length(n_classes))
  entropy_values <- numeric(length(n_classes))
  observations_per_class <- list()
  class_shares <- list()
  
  n <- nrow(df)  # sample size
  
  # Loop through different numbers of classes
  for (k in n_classes) {
    cat("Fitting model with", k, "classes...\n")
    model <- poLCA(formula, df, nclass = k, maxiter = maxiter, graphs = FALSE, nrep = 20)
    
    # Store log-likelihood and number of parameters
    LL <- model$llik
    npar <- model$npar
    logLik_values[k - 1] <- LL
    npar_values[k - 1] <- npar
    
    # AIC, BIC
    aic_values[k - 1] <- model$aic
    bic_values[k - 1] <- model$bic
    
    # Adjusted BIC and Consistent AIC
    aBIC_values[k - 1] <- -2*LL + npar*log((n + 2)/24)
    CAIC_values[k - 1] <- -2*LL + npar*(log(n) + 1)
    
    # Posterior probabilities and entropy
    # Posterior probabilities and entropy
    posterior_probs <- model$posterior
    entropy_values[k - 1] <- 1 + sum(posterior_probs * log(pmax(posterior_probs, 1e-10))) / (n * log(k))
    

    # class_shares[[as.character(k)]] <- colSums(posterior_probs) / nrow(posterior_probs)
    
    # Predicted class assignments
    # predicted_classes <- model$predclass
    # class_counts <- table(predicted_classes)
    # observations_per_class[[as.character(k)]] <- class_counts / sum(class_counts)
  }
  
  # Combine results into a data frame
  results_df <- data.frame(
    Classes = n_classes,
    logLik = logLik_values,
    npar = npar_values,
    AIC = aic_values,
    BIC = bic_values,
    aBIC = aBIC_values,
    CAIC = CAIC_values,
    Entropy = entropy_values
  )
  
  print(results_df)
  
  # Plot BIC and AIC for different numbers of classes
  p <- ggplot(data.frame(
    n_classes = rep(n_classes, 2),
    criterion_value = c(bic_values, aic_values),
    criterion = rep(c("BIC", "AIC"), each = length(n_classes))
  ), aes(x = n_classes, y = criterion_value, color = criterion, shape = criterion)) +
    geom_point() +
    geom_line() +
    labs(
      x = "Number of Classes",
      y = "Criterion Value",
      title = "BIC and AIC for Different Number of Latent Classes"
    ) +
    scale_color_manual(values = c("blue", "red")) +
    scale_shape_manual(values = c(19, 19)) +
    theme_bw()
  
  return(list(plot = p, table = results_df, class_shares = class_shares, observations = observations_per_class))
}

defineClustersNumber2(df, formula, 10, maxiter = 10000)


